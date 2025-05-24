// File: src/components/CVListPage.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Container, Card, Button, Alert } from 'react-bootstrap';

export default function CVListPage({ userId }) {
  const [cvs, setCvs] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!userId) return;
    fetchCVs();
  }, [userId]);

  const fetchCVs = async () => {
    try {
      const res = await fetch(`http://localhost:5000/cv?user_id=${userId}`);
      const data = await res.json();
      if (res.ok) {
        setCvs(data);
        setError('');
      } else {
        setError(data.message || 'Error al cargar CVs');
      }
    } catch {
      setError('Error de conexión');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Seguro que deseas eliminar este CV?')) return;
    try {
      const res = await fetch(`http://localhost:5000/cv/${id}`, { method: 'DELETE' });
      const data = await res.json();
      if (res.ok) {
        setCvs(cvs.filter(cv => cv.id !== id));
      } else {
        setError(data.message || 'Error al eliminar CV');
      }
    } catch {
      setError('Error de conexión');
    }
  };

  if (!userId) {
    return <Alert variant="warning">Debes iniciar sesión para ver tus CVs.</Alert>;
  }

  return (
    <Container style={{ maxWidth: '800px' }} className="mt-4">
      <h2>Mis CVs</h2>

      <div className="mb-3">
        <Button as={Link} to="/cvs/scan" variant="warning" className="me-2">
          Escanear CV
        </Button>
        <Button as={Link} to="/cvs/create" variant="success">
          Crear CV Manual
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}
      {cvs.length === 0 && !error && (
        <Alert variant="info">Aún no tienes CVs guardados.</Alert>
      )}

      {cvs.map(cv => (
        <Card key={cv.id} className="mb-3">
          <Card.Body>
            <Card.Title>{cv.nombre}</Card.Title>
            <Card.Subtitle className="mb-2 text-muted">
              Educación: {cv.educacion}
            </Card.Subtitle>
            <Card.Text>
              <strong>Experiencia:</strong> {cv.experiencia}
              {cv.full_text && (
                <>
                  <br />
                  <strong>Texto adicional:</strong> {cv.full_text}
                </>
              )}
            </Card.Text>

            <Button
              as={Link}
              to={`/cvs/${cv.id}`}
              variant="outline-primary"
              className="me-2"
            >
              Ver detalle
            </Button>
            <Button
              as={Link}
              to={`/cvs/${cv.id}/edit`}
              variant="outline-secondary"
              className="me-2"
            >
              Editar
            </Button>
            <Button
              variant="danger"
              onClick={() => handleDelete(cv.id)}
            >
              Eliminar
            </Button>
          </Card.Body>
        </Card>
      ))}
    </Container>
  );
}



