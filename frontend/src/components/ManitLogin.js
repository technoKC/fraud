import React, { useState } from 'react';
import axios from 'axios';
import getApiBaseUrl from '../utils/getApiBaseUrl';

const ManitLogin = ({ setIsLoggedIn, showPage }) => {
  const [adminId, setAdminId] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleManitLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      console.log('Attempting MANIT login with:', adminId);
      
      const response = await axios.post(`${getApiBaseUrl()}/admin/login/`, {
        username: adminId,
        password: password,
        dashboard_type: 'manit'
      });
      
      console.log('MANIT login response:', response.data);

      if (response.data.status === 'success') {
        // Store the access token
        if (response.data.access_token) {
          localStorage.setItem('authToken', response.data.access_token);
          console.log('MANIT token stored successfully');
        }
        
        setIsLoggedIn(true);
        showPage('manitDashboard');
        alert('✅ Login successful! Welcome to MANIT Dashboard');
      } else {
        alert('❌ Login failed. Please check your credentials.');
      }
    } catch (error) {
      console.error('MANIT login error:', error);
      
      if (error.response) {
        const status = error.response.status;
        const message = error.response.data?.detail || 'Login failed';
        
        if (status === 401) {
          alert('❌ Invalid credentials!\n\nPlease use:\nUsername: manit\nPassword: bhopal123');
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
    <div id="manit-login" className="page active">
      <div className="admin-login manit-theme">
        <div className="admin-logo">
          <img src="/manit.png" alt="MANIT Logo" />
        </div>
        <h2>Maulana Azad National Institute of Technology</h2>
        <h3>Bhopal</h3>
        <p className="login-subtitle">Student Loan Verification Portal</p>
        
        <div className="login-info" style={{
          background: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          borderRadius: '8px',
          padding: '1rem',
          margin: '1rem 0',
          fontSize: '0.9rem',
          color: '#3b82f6'
        }}>
          <strong>Default Credentials:</strong><br />
          Username: <code>manit</code><br />
          Password: <code>bhopal123</code>
        </div>
        
        <form className="login-form" onSubmit={handleManitLogin}>
          <div className="form-group">
            <label className="form-label">Admin ID</label>
            <input 
              type="text" 
              className="form-input" 
              placeholder="Enter MANIT Admin ID (manit)" 
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
              placeholder="Enter Password (bhopal123)" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
              disabled={loading}
            />
          </div>
          <button type="submit" className="btn btn-primary manit-btn" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner-small"></span> Logging in...
              </>
            ) : (
              <>
                <span>🎓</span> Login to MANIT Portal
              </>
            )}
          </button>
        </form>
        
        <div className="login-footer">
          <p>For technical support, contact: support@manit.ac.in</p>
        </div>
      </div>
    </div>
  );
};

export default ManitLogin;