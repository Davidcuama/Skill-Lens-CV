// File: src/App.jsx
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Navbar, Nav, Container, Button } from 'react-bootstrap';
import RegisterPage from './components/RegisterPage';
import LoginPage from './components/LoginPage';
import CVScanPage from './components/CVScanPage';
import CVListPage from './components/CVListPage';
import CVCreatePage from './components/CVCreatePage';
import CVDetailPage from './components/CVDetailPage';
import CVEditPage from './components/CVEditPage';

export default function App() {
  const [userId, setUserId] = useState(localStorage.getItem('userId'));

  const handleLogin = (id) => {
    setUserId(id);
    localStorage.setItem('userId', id);
  };

  const handleLogout = () => {
    setUserId(null);
    localStorage.removeItem('userId');
  };

  return (
    <Router>
      <Navbar bg="dark" variant="dark" expand="lg">
        <Container>
          <Navbar.Brand as={Link} to="/">SkillLens</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              {!userId && <Nav.Link as={Link} to="/register">Registrar</Nav.Link>}
              {!userId && <Nav.Link as={Link} to="/login">Login</Nav.Link>}
              {userId && <Nav.Link as={Link} to="/cvs">Mis CVs</Nav.Link>}
            </Nav>
            {userId && (<Button variant="outline-light" onClick={handleLogout}>Logout</Button>)}
          </Navbar.Collapse>
        </Container>
      </Navbar>
      <Container className="py-4">
        <Routes>
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
          <Route path="/cvs" element={<CVListPage userId={userId} />} />
          <Route path="/cvs/scan" element={<CVScanPage userId={userId} />} />
          <Route path="/cvs/create" element={<CVCreatePage userId={userId} />} />
          <Route path="/cvs/:id" element={<CVDetailPage userId={userId} />} />
          <Route path="/cvs/:id/edit" element={<CVEditPage userId={userId} />} />
          <Route
            path="/"
            element={
              userId ? <CVListPage userId={userId} /> : <p className="text-center">Bienvenido! Por favor regístrate o inicia sesión.</p>
            }
          />
        </Routes>
      </Container>
    </Router>
  );
}
