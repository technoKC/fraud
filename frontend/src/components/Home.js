import React, { useEffect } from 'react';

const Home = ({ showPage }) => {
  useEffect(() => {
    // Initialize particles
    const container = document.querySelector('.particles-container');
    if (!container) return;

    const createParticle = () => {
      const particle = document.createElement('div');
      particle.className = 'particle';
      particle.style.left = Math.random() * 100 + '%';
      particle.style.width = Math.random() * 4 + 2 + 'px';
      particle.style.height = particle.style.width;
      particle.style.animationDuration = Math.random() * 10 + 10 + 's';
      particle.style.animationDelay = Math.random() * 2 + 's';
      
      container.appendChild(particle);
      
      setTimeout(() => {
        particle.remove();
      }, 20000);
    };

    const interval = setInterval(createParticle, 300);
    return () => clearInterval(interval);
  }, []);

  return (
    <div id="home" className="page active">
      <div className="home-hero">
        <div className="hero-header">
          <h1 className="hero-title">FraudShield</h1>
          <p className="hero-subtitle">AI-Powered Fraud Detection & Security Platform</p>
          <p className="hero-tagline">Detect | Explain | Protect</p>
        </div>

        {/* Security Features Display */}
        <div className="security-features">
          <div className="security-badge">
            <span className="lock-icon">🔒</span>
            <span>TLS 1.3</span>
          </div>
          <div className="security-badge">
            <span className="lock-icon">🔐</span>
            <span>OAuth 2.0</span>
          </div>
          <div className="security-badge">
            <span className="lock-icon">👥</span>
            <span>RBAC</span>
          </div>
          <div className="security-badge">
            <span className="lock-icon">🔑</span>
            <span>Hashing</span>
          </div>
          <div className="security-badge">
            <span className="lock-icon">📊</span>
            <span>Anomaly Detection</span>
          </div>
        </div>
        
        {/* Three Main Action Buttons with Simple Blue Glow */}
        <div className="hero-main-actions">
          <div className="action-card" onClick={() => showPage('dashboard')}>
            <div className="action-logo">
              <img src="/logo.png" alt="FraudShield" />
            </div>
            <h3>Upload CSV</h3>
            <p>Analyze transactions with AI-powered fraud detection</p>
            <button className="action-button">
              <span>🛡️</span> Start Detection
            </button>
          </div>

          <div className="action-card" onClick={() => showPage('admin')}>
            <div className="action-logo">
              <img src="/centralbank.png" alt="Central Bank" />
            </div>
            <h3>Central Bank Login</h3>
            <p>Access fraud monitoring dashboard</p>
            <button className="action-button">
              <span>🏦</span> Admin Portal
            </button>
          </div>

          <div className="action-card" onClick={() => showPage('manit')}>
            <div className="action-logo">
              <img src="/manit.png" alt="MANIT Bhopal" />
            </div>
            <h3>MANIT Bhopal Login</h3>
            <p>Student loan verification system</p>
            <button className="action-button">
              <span>🎓</span> Student Portal
            </button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="features-section">
          <h2 className="features-title">Advanced Security & AI Features</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Real-Time Detection</h3>
              <p>Instant fraud detection with AI-powered analysis</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3>Enterprise Security</h3>
              <p>TLS 1.3, OAuth 2.0, and advanced encryption</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🧠</div>
              <h3>AI Neural Analysis</h3>
              <p>Machine learning algorithms for pattern detection</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Anomaly Detection</h3>
              <p>AI-based security monitoring and alerts</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">👥</div>
              <h3>Role-Based Access</h3>
              <p>Secure RBAC with granular permissions</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h3>Interactive Analytics</h3>
              <p>Dynamic graphs with zoom and pan controls</p>
            </div>
          </div>
        </div>

        {/* Statistics - FIXED */}
        <div className="stats-section">
          <div className="stat-item">
            <div className="stat-number">99.5%</div>
            <div className="stat-label">Accuracy Rate</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">{'< 100ms'}</div>
            <div className="stat-label">Detection Speed</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">TLS 1.3</div>
            <div className="stat-label">Security</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">AI Powered</div>
            <div className="stat-label">Technology</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;