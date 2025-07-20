import React, { useState } from 'react';
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

  const showPage = (page) => {
    setCurrentPage(page);
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
        </nav>
      </header>

      <main className="main-content">
        {currentPage === 'home' && (
          <Home showPage={showPage} />
        )}
        
        {currentPage === 'dashboard' && (
          <Dashboard data={uploadedData} setData={setUploadedData} />
        )}
        
        {currentPage === 'admin' && !isAdminLoggedIn && (
          <AdminLogin 
            setIsLoggedIn={setIsAdminLoggedIn} 
            showPage={showPage} 
          />
        )}
        
        {currentPage === 'adminDashboard' && isAdminLoggedIn && (
          <AdminDashboard 
            setIsLoggedIn={setIsAdminLoggedIn} 
            showPage={showPage} 
          />
        )}
        
        {currentPage === 'manit' && !isManitLoggedIn && (
          <ManitLogin 
            setIsLoggedIn={setIsManitLoggedIn} 
            showPage={showPage} 
          />
        )}
        
        {currentPage === 'manitDashboard' && isManitLoggedIn && (
          <ManitDashboard 
            setIsLoggedIn={setIsManitLoggedIn} 
            showPage={showPage} 
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