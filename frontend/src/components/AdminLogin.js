// Update your AdminLogin.js component

import React, { useState } from 'react';

function AdminLogin({ setIsLoggedIn, showPage, onLogin }) {
  const [credentials, setCredentials] = useState({
    username: '',
    password: '',
    dashboard_type: 'centralbank'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('https://fraud-shield-back.onrender.com/admin/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
      });

      const data = await response.json();

      if (response.ok && data.status === 'success') {
        // Store token and user info
        if (data.access_token) {
          localStorage.setItem('token', data.access_token);
          localStorage.setItem('username', credentials.username);
          localStorage.setItem('dashboard_type', data.dashboard_type);
        }

        // Call the parent's login handler
        if (onLogin) {
          onLogin({
            token: data.access_token,
            username: credentials.username,
            dashboard_type: data.dashboard_type
          }, 'admin');
        } else {
          // Fallback to old method
          setIsLoggedIn(true);
          showPage('adminDashboard');
        }
      } else {
        setError(data.detail || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <img src="/centralbank.png" alt="Central Bank" className="login-logo" />
          <h2>Central Bank Admin</h2>
          <p>Secure Banking Fraud Detection System</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="error-message" style={{
              color: '#e74c3c',
              backgroundColor: '#fdf2f2',
              padding: '10px',
              borderRadius: '5px',
              marginBottom: '15px',
              border: '1px solid #e74c3c'
            }}>
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={credentials.username}
              onChange={handleChange}
              required
              disabled={isLoading}
              placeholder="Enter your username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              required
              disabled={isLoading}
              placeholder="Enter your password"
            />
          </div>

          <button 
            type="submit" 
            className="login-button"
            disabled={isLoading}
            style={{
              opacity: isLoading ? 0.7 : 1,
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }}
          >
            {isLoading ? 'Logging in...' : '🔐 Login'}
          </button>
        </form>

        <div className="login-footer">
          <p>Authorized personnel only</p>
          <button 
            onClick={() => showPage('home')} 
            className="back-button"
            disabled={isLoading}
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}

export default AdminLogin;