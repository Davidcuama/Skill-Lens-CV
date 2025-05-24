// File: src/components/CVDetailPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Card, Button, Alert } from 'react-bootstrap';

export default function CVDetailPage({ userId }) {
  const { id } = useParams();
  const [cv, setCv] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCV = async () => {
      try {
        const res = await fetch(`http://localhost:5000/cv/${id}`);
        const data = await res.json();
        if (!res.ok) {
          setError(data.message || 'Error al cargar CV');
        } else {
          setCv(data);
        }
      } catch (err) {
        setError('Error de conexión');
      }
    };
    fetchCV();
  }, [id]);

  // Si hay error de backend, lo mostramos
  if (error) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">{error}</Alert>
      </Container>
    );
  }

  // Cargando...
  if (!cv) {
    return (
      <Container className="mt-4">
        <p>Cargando...</p>
      </Container>
    );
  }

  // Autorización: comparamos numéricamente
  if (cv.owner_id !== Number(userId)) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">No autorizado</Alert>
      </Container>
    );
  }

  // Si todo OK, renderizamos detalle
  return (
    <Container style={{ maxWidth: '600px' }} className="mt-4">
      <Card>
        <Card.Body>
          <Card.Title>{cv.nombre}</Card.Title>
          <Card.Text>
            <strong>Experiencia:</strong> {cv.experiencia}
          </Card.Text>
          <Card.Text>
            <strong>Educación:</strong> {cv.educacion}
          </Card.Text>
          {cv.full_text && (
            <>
              <Card.Text>
                <strong>Texto adicional:</strong>
              </Card.Text>
              <Card.Text>
                <pre className="bg-light p-2">{cv.full_text}</pre>
              </Card.Text>
            </>
          )}
          <Button as={Link} to={`/cvs/${id}/edit`} variant="primary">
            Editar
          </Button>
        </Card.Body>
      </Card>
    </Container>
  );
}

