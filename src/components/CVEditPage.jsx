// File: src/components/CVEditPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Form, Button, Alert } from 'react-bootstrap';

export default function CVEditPage({ userId }) {
  const { id } = useParams();
  const navigate = useNavigate();

  const [cv, setCv] = useState(null);
  const [nombre, setNombre] = useState('');
  const [experiencia, setExperiencia] = useState('');
  const [educacion, setEducacion] = useState('');
  const [fullText, setFullText] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCV = async () => {
      try {
        const res = await fetch(`http://localhost:5000/cv/${id}`);
        const data = await res.json();
        if (!res.ok) {
          setError(data.message || 'Error al cargar el CV');
          return;
        }
        // Autorización: comparamos numéricamente
        if (data.owner_id !== Number(userId)) {
          setError('No autorizado');
          navigate('/cvs');
          return;
        }
        setCv(data);
        setNombre(data.nombre || '');
        setExperiencia(data.experiencia || '');
        setEducacion(data.educacion || '');
        setFullText(data.full_text || '');
      } catch (err) {
        setError('Error de conexión');
      }
    };
    fetchCV();
  }, [id, userId, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`http://localhost:5000/cv/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nombre,
          experiencia,
          educacion,
          full_text: fullText
        }),
      });
      if (res.ok) {
        navigate(`/cvs/${id}`);
      } else {
        const data = await res.json();
        setError(data.message || 'Error al actualizar el CV');
      }
    } catch (err) {
      setError('Error de conexión');
    }
  };

  if (error) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">{error}</Alert>
      </Container>
    );
  }

  if (!cv) {
    return (
      <Container className="mt-4">
        <p>Cargando CV...</p>
      </Container>
    );
  }

  return (
    <Container style={{ maxWidth: '480px' }} className="mt-4">
      <h2 className="mb-4">Editar CV</h2>
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3" controlId="editNombre">
          <Form.Label>Nombre</Form.Label>
          <Form.Control
            type="text"
            value={nombre}
            onChange={e => setNombre(e.target.value)}
            required
          />
        </Form.Group>
        <Form.Group className="mb-3" controlId="editExperiencia">
          <Form.Label>Experiencia</Form.Label>
          <Form.Control
            as="textarea"
            rows={3}
            value={experiencia}
            onChange={e => setExperiencia(e.target.value)}
            required
          />
        </Form.Group>
        <Form.Group className="mb-3" controlId="editEducacion">
          <Form.Label>Educación</Form.Label>
          <Form.Control
            as="textarea"
            rows={2}
            value={educacion}
            onChange={e => setEducacion(e.target.value)}
            required
          />
        </Form.Group>
        <Form.Group className="mb-3" controlId="editFullText">
          <Form.Label>Texto adicional</Form.Label>
          <Form.Control
            as="textarea"
            rows={4}
            value={fullText}
            onChange={e => setFullText(e.target.value)}
          />
        </Form.Group>
        <Button variant="primary" type="submit">
          Guardar cambios
        </Button>
      </Form>
    </Container>
  );
}
