// File: src/components/CVScanPage.jsx
import React, { useState } from 'react';
import { Container, Form, Button, Alert, Card } from 'react-bootstrap';

export default function CVScanPage({ userId }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Selecciona un archivo');
      return;
    }
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('file', file);
    const res = await fetch('http://localhost:5000/cv/scan', {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();
    if (res.ok) {
      setResult(data);
      setError('');
    } else {
      setError(data.message);
      setResult(null);
    }
  };

  return (
    <Container style={{ maxWidth: '600px' }}>
      <h2 className="mb-4">Escanear CV</h2>
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3" controlId="cvFile">
          <Form.Label>Archivo de imagen</Form.Label>
          <Form.Control type="file" accept="image/*" onChange={e => setFile(e.target.files[0])} />
        </Form.Group>
        <Button variant="warning" type="submit">Escanear</Button>
      </Form>
      {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
      {result && (
        <Card className="mt-4">
          <Card.Body>
            <Card.Title>{result.nombre}</Card.Title>
            <Card.Text><strong>Experiencia:</strong> {result.experiencia}</Card.Text>
            <Card.Text><strong>Educación:</strong> {result.educacion}</Card.Text>
            <Card.Text>
              <pre className="bg-light p-2">{result.full_text}</pre>
            </Card.Text>
          </Card.Body>
        </Card>
      )}
    </Container>
  );
}