// File: src/components/CVCreatePage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Form, Button, Alert } from 'react-bootstrap';

export default function CVCreatePage({ userId }) {
  const [nombre, setNombre] = useState('');
  const [experiencia, setExperiencia] = useState('');
  const [educacion, setEducacion] = useState('');
  const [fullText, setFullText] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch('http://localhost:5000/cv/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        nombre,
        experiencia,
        educacion,
        full_text: fullText
      })
    });
    const data = await res.json();
    if (res.ok) {
      navigate('/cvs');
    } else {
      setError(data.message || 'Error al crear CV');
    }
  };

  return (
    <Container style={{ maxWidth: '480px' }}>
      <h2 className="mb-4">Crear CV Manual</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>Nombre</Form.Label>
          <Form.Control
            type="text"
            value={nombre}
            onChange={e => setNombre(e.target.value)}
            required
          />
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>Experiencia</Form.Label>
          <Form.Control
            as="textarea"
            rows={3}
            value={experiencia}
            onChange={e => setExperiencia(e.target.value)}
            required
          />
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>Educación</Form.Label>
          <Form.Control
            as="textarea"
            rows={2}
            value={educacion}
            onChange={e => setEducacion(e.target.value)}
            required
          />
        </Form.Group>
        <Form.Group className="mb-3">
          <Form.Label>Texto adicional</Form.Label>
          <Form.Control
            as="textarea"
            rows={4}
            value={fullText}
            onChange={e => setFullText(e.target.value)}
          />
        </Form.Group>
        <Button type="submit" variant="success">
          Crear
        </Button>
      </Form>
    </Container>
  );
}

