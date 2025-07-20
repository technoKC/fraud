import React, { useState } from 'react';
import axios from 'axios';
import getApiBaseUrl from '../utils/getApiBaseUrl';

const AdminLogin = ({ setIsLoggedIn, showPage }) => {
  const [adminId, setAdminId] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAdminLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      console.log('Attempting login with:', adminId);
      
      const response = await axios.post(`${getApiBaseUrl()}/admin/login/`, {
        username: adminId,
        password: password,
        dashboard_type: 'centralbank'
      });
      
      console.log('Login response:', response.data);
      
      if (response.data.status === 'success') {
        // Store the access token
        if (response.data.access_token) {
          localStorage.setItem('authToken', response.data.access_token);
          console.log('Token stored successfully');
        }
        
        setIsLoggedIn(true);
        showPage('adminDashboard');
        alert('✅ Login successful! Welcome to Central Bank Dashboard');
      } else {
        alert('❌ Login failed. Please check your credentials.');
      }
    } catch (error) {
      console.error('Login error:', error);
      
      if (error.response) {
        const status = error.response.status;
        const message = error.response.data?.detail || 'Login failed';
        
        if (status === 401) {
          alert('❌ Invalid credentials!\n\nPlease contact your administrator for login details.');
        } else if (status === 429) {
          alert('❌ Too many login attempts!\n\nPlease wait a few minutes before trying again.');
        } else {
          alert(`❌ Login Error (${status})\n\n${message}`);
        }
      } else if (error.request) {
        alert(`❌ Cannot connect to server!\n\nPlease ensure the backend is running and accessible at: ${getApiBaseUrl()}`);
      } else {
        alert(`❌ Login Error\n\n${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div id="admin" className="page active">
      <div className="admin-login">
        <div className="admin-logo">
          <img src="/centralbank.png" alt="Central Bank Logo" />
        </div>
        <h2>Central Bank of India</h2>
        <h3>Admin Portal</h3>
        <p className="login-subtitle">Fraud Detection & Prevention System</p>
        
        <form className="login-form" onSubmit={handleAdminLogin}>
          <div className="form-group">
            <label className="form-label">Admin ID</label>
            <input 
              type="text" 
              className="form-input" 
              placeholder="Enter Admin ID" 
              value={adminId}
              onChange={(e) => setAdminId(e.target.value)}
              required 
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input 
              type="password" 
              className="form-input" 
              placeholder="Enter Password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
              disabled={loading}
            />
          </div>
          <button type="submit" className="btn btn-primary admin-login-btn" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner-small"></span> Logging in...
              </>
            ) : (
              <>
                <span>🏦</span> Login to Central Bank
              </>
            )}
          </button>
        </form>
        
        <div className="login-footer">
          <p>Secured with TLS 1.3 • OAuth 2.0 • AI Security</p>
        </div>
      </div>
    </div>
  );
};

export default AdminLogin;