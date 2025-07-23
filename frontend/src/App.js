import React, { useEffect, useState } from 'react';
import Home from './components/Home';
import Dashboard from './components/Dashboard';
import AdminLogin from './components/AdminLogin';
import AdminDashboard from './components/AdminDashboard';
import ManitLogin from './components/ManitLogin';
import ManitDashboard from './components/ManitDashboard';
import './styles/App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [uploadedData, setUploadedData] = useState(null);
  const [isAdminLoggedIn, setIsAdminLoggedIn] = useState(false);
  const [isManitLoggedIn, setIsManitLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [isOAuthUser, setIsOAuthUser] = useState(false);

  const showPage = (page) => {
    setCurrentPage(page);
  };

  // Handle OAuth callback and check existing authentication
  useEffect(() => {
    // First, check if user is already logged in via localStorage (from OAuth callback)
    const storedToken = localStorage.getItem('token');
    const storedUsername = localStorage.getItem('username');
    const storedDashboardType = localStorage.getItem('dashboard_type');
    const storedFullName = localStorage.getItem('full_name');

    if (storedToken && storedUsername) {
      // User is logged in via OAuth
      setUser({
        email: storedUsername,
        name: storedFullName || storedUsername,
        token: storedToken,
        dashboardType: storedDashboardType
      });
      setIsOAuthUser(true);

      // Set appropriate login state and redirect to correct dashboard
      if (storedDashboardType === 'centralbank') {
        setIsAdminLoggedIn(true);
        setCurrentPage('adminDashboard');
      } else if (storedDashboardType === 'manit') {
        setIsManitLoggedIn(true);
        setCurrentPage('manitDashboard');
      } else {
        setCurrentPage('dashboard');
      }
      return;
    }

    // Handle OAuth callback parameters (if coming from backend redirect)
    const params = new URLSearchParams(window.location.search);
    const email = params.get("email");
    const name = params.get("name");
    const token = params.get("token");

    if (email && name && token) {
      // Store OAuth data
      localStorage.setItem('token', token);
      localStorage.setItem('username', email);
      localStorage.setItem('full_name', name);
      
      setUser({ email, name, token });
      setIsOAuthUser(true);
      setCurrentPage("dashboard");
      
      // Clean up URL parameters
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  // Handle traditional login success
  const handleTraditionalLogin = (loginData, loginType) => {
    if (loginType === 'admin') {
      setIsAdminLoggedIn(true);
      setCurrentPage('adminDashboard');
    } else if (loginType === 'manit') {
      setIsManitLoggedIn(true);
      setCurrentPage('manitDashboard');
    }
    
    // Store traditional login data
    if (loginData.token) {
      localStorage.setItem('token', loginData.token);
      localStorage.setItem('username', loginData.username || 'admin');
      localStorage.setItem('dashboard_type', loginData.dashboard_type || loginType);
    }
  };

  // Handle logout
  const handleLogout = () => {
    // Clear all stored data
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('full_name');
    localStorage.removeItem('dashboard_type');
    localStorage.removeItem('role');
    
    // Reset all states
    setUser(null);
    setIsOAuthUser(false);
    setIsAdminLoggedIn(false);
    setIsManitLoggedIn(false);
    setCurrentPage('home');
  };

  // Google OAuth login function
  const handleGoogleLogin = () => {
    window.location.href = "https://fraud-shield-back.onrender.com/auth/google/login";
  };

  return (
    <div className="App">
      <div className="animated-bg">
        <div className="particles-container"></div>
      </div>

      <header className="header">
        <div className="logo-section">
          <img 
            src="/logo.png" 
            alt="FraudShield Logo" 
            className="header-logo"
          />
          <span className="header-title">FraudShield</span>
        </div>
        <nav className="nav-links">
          <a href="#" className="nav-link" onClick={() => showPage('home')}>
            <span className="nav-icon">🏠</span> Home
          </a>
          <a href="#" className="nav-link" onClick={() => showPage('dashboard')}>
            <span className="nav-icon">📊</span> Dashboard
          </a>
          <a href="#" className="nav-link" onClick={() => showPage('admin')}>
            <span className="nav-icon">🏦</span> Central Bank
          </a>
          <a href="#" className="nav-link" onClick={() => showPage('manit')}>
            <span className="nav-icon">🎓</span> MANIT
          </a>
          {(user || isAdminLoggedIn || isManitLoggedIn) && (
            <a href="#" className="nav-link logout-link" onClick={handleLogout}>
              <span className="nav-icon">🚪</span> Logout
            </a>
          )}
        </nav>
      </header>

      <main className="main-content">
        {currentPage === 'home' && (
          <div>
            <Home showPage={showPage} />
            {/* Add Google Login Button to Home page */}
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <button 
                onClick={handleGoogleLogin}
                style={{
                  backgroundColor: '#4285f4',
                  color: 'white',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                🔐 Login with Google
              </button>
            </div>
          </div>
        )}
        
        {currentPage === 'dashboard' && (
          <Dashboard 
            data={uploadedData} 
            setData={setUploadedData} 
            user={user}
            onLogout={handleLogout}
          />
        )}
        
        {currentPage === 'admin' && !isAdminLoggedIn && (
          <div>
            <AdminLogin 
              setIsLoggedIn={setIsAdminLoggedIn} 
              showPage={showPage}
              onLogin={handleTraditionalLogin}
            />
            {/* Add Google Login option to Admin Login */}
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <p>or</p>
              <button 
                onClick={handleGoogleLogin}
                style={{
                  backgroundColor: '#4285f4',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                🔐 Login with Google
              </button>
            </div>
          </div>
        )}
        
        {currentPage === 'adminDashboard' && isAdminLoggedIn && (
          <AdminDashboard 
            setIsLoggedIn={setIsAdminLoggedIn} 
            showPage={showPage}
            user={user}
            onLogout={handleLogout}
          />
        )}
        
        {currentPage === 'manit' && !isManitLoggedIn && (
          <div>
            <ManitLogin 
              setIsLoggedIn={setIsManitLoggedIn} 
              showPage={showPage}
              onLogin={handleTraditionalLogin}
            />
            {/* Add Google Login option to MANIT Login */}
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <p>or</p>
              <button 
                onClick={handleGoogleLogin}
                style={{
                  backgroundColor: '#4285f4',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                🔐 Login with Google
              </button>
            </div>
          </div>
        )}
        
        {currentPage === 'manitDashboard' && isManitLoggedIn && (
          <ManitDashboard 
            setIsLoggedIn={setIsManitLoggedIn} 
            showPage={showPage}
            user={user}
            onLogout={handleLogout}
          />
        )}
      </main>

      <footer className="footer">
        <p>&copy; 2025 FraudShield - Powered by AI | Detect • Explain • Protect</p>
      </footer>
    </div>
  );
}

export default App;