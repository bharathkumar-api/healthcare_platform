import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Appointments from './pages/Appointments';

function App() {
  const isAuthenticated = () => {
    return localStorage.getItem('token') !== null;
  };

  const PrivateRoute = ({ children }) => {
    return isAuthenticated() ? children : <Navigate to="/login" />;
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/appointments" element={<PrivateRoute><Appointments /></PrivateRoute>} />
        <Route path="/profile" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/billing" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/records" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Router>
  );
}

export default App;
