import React, { useState } from 'react';
import './Auth.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8090';

function Login({ onLogin, onSwitchToRegister }) {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const formBody = new FormData();
      formBody.append('username', formData.username);
      formBody.append('password', formData.password);

      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        body: formBody,
      });

      const data = await response.json();

      if (response.ok) {
        onLogin(data.access_token);
      } else {
        setMessage(data.detail || 'Login failed');
      }
    } catch (error) {
      setMessage('Connection error. Please check if backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>🏥 Healthcare Platform</h1>
          <h2>Welcome Back</h2>
          <p>Login to access your health dashboard</p>
        </div>

        {message && <div className="alert alert-error">{message}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              placeholder="Enter your username"
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="Enter your password"
              required
            />
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="auth-footer">
          <p>Don't have an account? <button onClick={onSwitchToRegister} className="link-btn">Register here</button></p>
        </div>
      </div>
    </div>
  );
}

export default Login;
