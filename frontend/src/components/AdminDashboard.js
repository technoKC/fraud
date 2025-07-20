import React, { useState, useEffect } from 'react';
import axios from 'axios';
import NetworkGraph from './NetworkGraph';
import getApiBaseUrl from '../utils/getApiBaseUrl';

const AdminDashboard = ({ setIsLoggedIn, showPage }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showGraph, setShowGraph] = useState(false);
  const [activeTab, setActiveTab] = useState('alerts');
  const [blockedTransactions, setBlockedTransactions] = useState(new Set());
  const [verifiedTransactions, setVerifiedTransactions] = useState(new Set());

  // Helper function to get auth headers
  const getAuthHeaders = () => {
    const token = localStorage.getItem('authToken');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  };

  const loadBackendData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${getApiBaseUrl()}/admin/data/`, {
        headers: getAuthHeaders()
      });
      setData(response.data);
      console.log('Admin data loaded successfully');
    } catch (error) {
      console.error('Error loading admin data:', error);
      
      if (error.response && error.response.status === 401) {
        alert('❌ Session expired. Please login again.');
        logout();
      } else if (error.response && error.response.status === 403) {
        alert('❌ Access denied. Insufficient permissions.');
      } else {
        alert('❌ Error loading data. Please ensure the backend is running and you are logged in.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (!token) {
      alert('❌ Please login first');
      logout();
      return;
    }
    
    loadBackendData();
  }, []);

  // Transaction action handler with proper error handling and immediate UI update
  const handleTransactionAction = async (transactionId, action) => {
    try {
      console.log(`Attempting to ${action} transaction: ${transactionId}`);
      
      // Proper API call with correct endpoint and headers
      const response = await axios.post(`${getApiBaseUrl()}/admin/transaction-action/`, {
        transaction_id: transactionId,
        action: action
      }, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      });
      
      console.log('Transaction action response:', response.data);
      
      // Immediate UI state update for better UX
      if (action === 'blocked') {
        setBlockedTransactions(prev => new Set([...prev, transactionId]));
        setVerifiedTransactions(prev => {
          const newSet = new Set(prev);
          newSet.delete(transactionId);
          return newSet;
        });
        
        // Update DOM element immediately
        const alertElement = document.querySelector(`[data-transaction-id="${transactionId}"]`);
        if (alertElement) {
          alertElement.classList.add('blocked');
          alertElement.classList.remove('verified');
        }
        
      } else if (action === 'verified') {
        setVerifiedTransactions(prev => new Set([...prev, transactionId]));
        setBlockedTransactions(prev => {
          const newSet = new Set(prev);
          newSet.delete(transactionId);
          return newSet;
        });
        
        // Update DOM element immediately
        const alertElement = document.querySelector(`[data-transaction-id="${transactionId}"]`);
        if (alertElement) {
          alertElement.classList.add('verified');
          alertElement.classList.remove('blocked');
        }
      }
      
      // Update data state with new counts
      if (data && data.fraud_transactions) {
        const updatedTransactions = data.fraud_transactions.map(txn => 
          txn.transaction_id === transactionId ? {...txn, status: action} : txn
        );
        
        setData({
          ...data, 
          fraud_transactions: updatedTransactions,
          blocked_accounts: action === 'blocked' ? (data.blocked_accounts || 0) + 1 : data.blocked_accounts,
          verified_accounts: action === 'verified' ? (data.verified_accounts || 0) + 1 : data.verified_accounts
        });
      }
      
      alert(`✅ Transaction ${action === 'blocked' ? 'blocked' : 'verified'} successfully`);
      
    } catch (error) {
      console.error('Transaction action error:', error);
      
      if (error.response) {
        const status = error.response.status;
        const message = error.response.data?.detail || 'Unknown error';
        
        if (status === 401) {
          alert('❌ Session expired. Please login again.');
          logout();
        } else if (status === 403) {
          alert('❌ Access denied. You do not have permission to perform this action.');
        } else {
          alert(`❌ Error updating transaction status (${status}): ${message}`);
        }
      } else if (error.request) {
        alert(`❌ Cannot connect to server. Please ensure the backend is running and accessible at: ${getApiBaseUrl()}`);
      } else {
        alert(`❌ Error: ${error.message}`);
      }
    }
  };

  // Enhanced PDF Report Generation with CBI Logo and Professional Design
  const generateReport = async () => {
    try {
      const { jsPDF } = await import('jspdf');
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      
      // Add FraudShield watermark in background
      const addWatermark = () => {
        doc.setGState(new doc.GState({opacity: 0.1}));
        doc.setFontSize(60);
        doc.setTextColor(200, 200, 200);
        doc.text('FraudShield', pageWidth / 2, pageHeight / 2, {
          align: 'center',
          angle: 45
        });
        doc.setGState(new doc.GState({opacity: 1}));
      };
      
      // Add watermark
      addWatermark();
      
      // Add CBI Logo
      const addCBILogo = async () => {
        try {
          const img = new Image();
          img.src = '/centralbank.png';
          
          await new Promise((resolve, reject) => {
            img.onload = resolve;
            img.onerror = reject;
          });
          
          // Add white background for logo visibility
          doc.setFillColor(255, 255, 255);
          doc.roundedRect(15, 15, 40, 40, 3, 3, 'F');
          doc.addImage(img, 'PNG', 20, 20, 30, 30);
          
        } catch (e) {
          console.log('CBI Logo loading failed, using text placeholder');
          doc.setFillColor(220, 38, 38);
          doc.roundedRect(15, 15, 40, 40, 3, 3, 'F');
          doc.setFontSize(18);
          doc.setTextColor(255, 255, 255);
          doc.text('CBI', 35, 35, { align: 'center' });
        }
      };

      // Add CBI logo
      await addCBILogo();
      
      // Professional CBI header
      doc.setFontSize(22);
      doc.setTextColor(30, 64, 175);
      doc.text('Central Bank of India', pageWidth / 2, 30, { align: 'center' });
      
      doc.setFontSize(16);
      doc.setTextColor(220, 38, 38);
      doc.text('Fraud Detection & Prevention System', pageWidth / 2, 45, { align: 'center' });
      
      doc.setFontSize(14);
      doc.setTextColor(100, 116, 139);
      doc.text('Official Fraud Analysis Report', pageWidth / 2, 60, { align: 'center' });
      
      doc.setFontSize(10);
      doc.text('Report Generated: ' + new Date().toLocaleString(), pageWidth / 2, 70, { align: 'center' });
      
      // Executive Summary Box
      doc.setDrawColor(30, 64, 175);
      doc.setFillColor(240, 245, 255);
      doc.roundedRect(15, 80, pageWidth - 30, 55, 3, 3, 'FD');
      
      doc.setFontSize(14);
      doc.setTextColor(30, 64, 175);
      doc.text('Executive Summary', 20, 95);
      
      doc.setFontSize(10);
      doc.setTextColor(51, 65, 85);
      
      const summaryData = [
        'Total Transactions Monitored: ' + (data?.total_transactions?.toLocaleString() || 0),
        'Fraud Cases Detected: ' + (data?.fraud_detected || 0),
        'Accounts Blocked: ' + blockedTransactions.size,
        'Accounts Verified: ' + verifiedTransactions.size,
        'System Health: ' + (data?.system_health || 95) + '%',
        'Detection Accuracy: ' + (data?.total_transactions ? (100 - ((data.fraud_detected / data.total_transactions) * 100)).toFixed(1) : 100) + '%'
      ];
      
      summaryData.forEach((item, index) => {
        const x = index < 3 ? 20 : 115;
        const y = 105 + ((index % 3) * 10);
        doc.text(item, x, y);
      });
      
      // AI Analysis Section
      if (data?.ai_insights) {
        doc.setFontSize(14);
        doc.setTextColor(30, 64, 175);
        doc.text('AI Intelligence Analysis', 20, 150);
        
        doc.setFontSize(10);
        doc.setTextColor(51, 65, 85);
        
        const aiData = [
          'AI Fraud Detection: ' + (data.ai_insights.ai_fraud_detected || data.fraud_detected),
          'High Risk Transactions: ' + (data.ai_insights.high_risk_transactions || 0),
          'Average Risk Score: ' + (data.ai_insights.average_risk_score?.toFixed(1) || 0) + '/100',
          'Detection Confidence: ' + ((data.ai_insights.confidence_level * 100).toFixed(1) || 95) + '%',
          'Model Version: ' + (data.ai_insights.model_version || 'FraudShield-AI-v2.0')
        ];
        
        aiData.forEach((item, index) => {
          doc.text(item, 20, 160 + (index * 8));
        });
      }
      
      // Critical Fraud Transactions Section
      doc.setFontSize(14);
      doc.setTextColor(220, 38, 38);
      doc.text('Critical Fraud Transactions', 20, 200);
      
      if (data?.fraud_transactions && data.fraud_transactions.length > 0) {
        doc.setFontSize(9);
        
        // Table headers
        const headers = ['Transaction ID', 'Amount (Rs)', 'Risk Score', 'Status'];
        const headerY = 210;
        const colWidths = [55, 35, 30, 35];
        let xPos = 20;
        
        // Header background
        doc.setFillColor(30, 64, 175);
        doc.rect(15, headerY - 5, pageWidth - 30, 12, 'F');
        
        headers.forEach((header, index) => {
          doc.setFont(undefined, 'bold');
          doc.setTextColor(255, 255, 255);
          doc.text(header, xPos, headerY);
          xPos += colWidths[index];
        });
        
        // Table data
        const maxTransactions = Math.min(data.fraud_transactions.length, 15);
        
        for (let i = 0; i < maxTransactions; i++) {
          const txn = data.fraud_transactions[i];
          const rowY = headerY + 10 + (i * 12);
          
          if (rowY > pageHeight - 30) break;
          
          // Alternating row colors
          if (i % 2 === 0) {
            doc.setFillColor(248, 250, 252);
            doc.rect(15, rowY - 5, pageWidth - 30, 12, 'F');
          }
          
          xPos = 20;
          doc.setFont(undefined, 'normal');
          doc.setTextColor(51, 65, 85);
          
          // Transaction ID (truncated)
          const txnId = txn.transaction_id.length > 20 ? 
            txn.transaction_id.substring(0, 17) + '...' : txn.transaction_id;
          doc.text(txnId, xPos, rowY);
          xPos += colWidths[0];
          
          // Amount
          doc.text('Rs ' + (txn.amount?.toLocaleString('en-IN') || 0), xPos, rowY);
          xPos += colWidths[1];
          
          // Risk Score
          doc.setTextColor(220, 38, 38);
          doc.text((txn.risk_score || 0) + '/100', xPos, rowY);
          xPos += colWidths[2];
          
          // Status
          const status = blockedTransactions.has(txn.transaction_id) ? 'BLOCKED' : 
                        verifiedTransactions.has(txn.transaction_id) ? 'VERIFIED' : 'PENDING';
          
          if (status === 'BLOCKED') {
            doc.setTextColor(220, 38, 38);
          } else if (status === 'VERIFIED') {
            doc.setTextColor(5, 150, 105);
          } else {
            doc.setTextColor(245, 158, 11);
          }
          
          doc.text(status, xPos, rowY);
          doc.setTextColor(51, 65, 85);
        }
      } else {
        doc.setFontSize(10);
        doc.text('No fraud transactions detected.', 20, 220);
      }
      
      // Professional CBI footer
      const footerY = pageHeight - 35;
      doc.setFillColor(30, 64, 175);
      doc.rect(0, footerY, pageWidth, 35, 'F');
      
      doc.setFontSize(10);
      doc.setTextColor(255, 255, 255);
      doc.text('Central Bank of India - Fraud Prevention Unit', pageWidth / 2, footerY + 10, { align: 'center' });
      doc.text('Powered by FraudShield AI v2.0 | Generated on ' + new Date().toLocaleDateString(), pageWidth / 2, footerY + 20, { align: 'center' });
      doc.text('This is a confidential document for internal use only.', pageWidth / 2, footerY + 30, { align: 'center' });
      
      // Save PDF
      doc.save('CBI_Fraud_Report_' + new Date().toISOString().split('T')[0] + '.pdf');
      
      alert('✅ CBI PDF report generated successfully!');
      
    } catch (error) {
      console.error('PDF generation error:', error);
      alert('❌ Error generating PDF report. Please try again.');
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setIsLoggedIn(false);
    showPage('home');
  };

  // Calculate accurate risk distribution
  const calculateRiskDistribution = () => {
    if (!data?.fraud_transactions || data.fraud_transactions.length === 0) {
      return { critical: 0, high: 0, medium: 0, low: 0 };
    }

    return {
      critical: data.fraud_transactions.filter(t => t.risk_score >= 80).length,
      high: data.fraud_transactions.filter(t => t.risk_score >= 60 && t.risk_score < 80).length,
      medium: data.fraud_transactions.filter(t => t.risk_score >= 40 && t.risk_score < 60).length,
      low: data.fraud_transactions.filter(t => t.risk_score < 40).length
    };
  };

  const riskDistribution = calculateRiskDistribution();

  return (
    <div id="adminDashboard" className="page active">
      <div className="dashboard admin-dashboard-enhanced">
        {/* Enhanced Professional Header with CBI Logo */}
        <div className="cbi-header">
          <div className="cbi-logo-section">
            <div className="cbi-logo">
              <img src="/centralbank.png" alt="Central Bank" className="cbi-logo-img" />
            </div>
            <div className="cbi-title-section">
              <h1 className="cbi-main-title">Central Bank of India</h1>
              <h2 className="cbi-subtitle">Fraud Detection & Prevention System</h2>
              <div className="cbi-tagline">Protecting India's Financial Ecosystem</div>
            </div>
          </div>
          <button className="cbi-logout-btn" onClick={logout}>
            <span>🚪</span> Secure Logout
          </button>
        </div>

        {data && (
          <>
            {/* Enhanced Statistics Dashboard */}
            <div className="cbi-stats-grid">
              <div className="cbi-stat-card primary">
                <div className="cbi-stat-icon">📊</div>
                <div className="cbi-stat-value">{data.total_transactions?.toLocaleString()}</div>
                <div className="cbi-stat-label">Total Transactions Monitored</div>
              </div>
              <div className="cbi-stat-card danger">
                <div className="cbi-stat-icon">🚨</div>
                <div className="cbi-stat-value">{data.fraud_detected}</div>
                <div className="cbi-stat-label">Fraud Cases Detected</div>
              </div>
              <div className="cbi-stat-card warning">
                <div className="cbi-stat-icon">🚫</div>
                <div className="cbi-stat-value">{blockedTransactions.size}</div>
                <div className="cbi-stat-label">Accounts Blocked</div>
              </div>
              <div className="cbi-stat-card success">
                <div className="cbi-stat-icon">✅</div>
                <div className="cbi-stat-value">{verifiedTransactions.size}</div>
                <div className="cbi-stat-label">Accounts Verified</div>
              </div>
              <div className="cbi-stat-card info">
                <div className="cbi-stat-icon">💚</div>
                <div className="cbi-stat-value">{data.system_health || 95}%</div>
                <div className="cbi-stat-label">System Health</div>
              </div>
            </div>

            {/* AI Insights Panel */}
            {data.ai_insights && (
              <div className="cbi-ai-panel">
                <h3 className="cbi-ai-title">🧠 AI Intelligence Dashboard</h3>
                <div className="cbi-ai-grid">
                  <div className="cbi-ai-metric">
                    <span className="cbi-ai-label">AI Fraud Detection</span>
                    <span className="cbi-ai-value danger">{data.ai_insights.ai_fraud_detected}</span>
                  </div>
                  <div className="cbi-ai-metric">
                    <span className="cbi-ai-label">High Risk Transactions</span>
                    <span className="cbi-ai-value warning">{data.ai_insights.high_risk_transactions}</span>
                  </div>
                  <div className="cbi-ai-metric">
                    <span className="cbi-ai-label">Average Risk Score</span>
                    <span className="cbi-ai-value">{data.ai_insights.average_risk_score?.toFixed(1)}/100</span>
                  </div>
                  <div className="cbi-ai-metric">
                    <span className="cbi-ai-label">Detection Confidence</span>
                    <span className="cbi-ai-value success">{(data.ai_insights.confidence_level * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            )}

            {/* Enhanced Action Controls */}
            <div className="cbi-action-controls">
              <button className="cbi-btn cbi-btn-primary" onClick={loadBackendData}>
                <span>🔄</span> Refresh Intelligence
              </button>
              <button className="cbi-btn cbi-btn-success" onClick={generateReport}>
                <span>📊</span> Generate PDF Report
              </button>
              <button className="cbi-btn cbi-btn-info" onClick={() => setShowGraph(!showGraph)}>
                {showGraph ? (
                  <>
                    <span>📉</span> Hide Network Analysis
                  </>
                ) : (
                  <>
                    <span>📈</span> Show Network Analysis
                  </>
                )}
              </button>
            </div>

            {/* Enhanced Network Graph */}
            {showGraph && data.graph_data && (
              <div className="cbi-graph-section">
                <h3 className="cbi-section-title">🔍 Transaction Network Analysis</h3>
                <NetworkGraph graphData={data.graph_data} />
              </div>
            )}

            {/* Enhanced Tab Navigation */}
            <div className="cbi-tabs">
              <button 
                className={`cbi-tab ${activeTab === 'alerts' ? 'active' : ''}`}
                onClick={() => setActiveTab('alerts')}
              >
                🚨 Critical Alerts
              </button>
              <button 
                className={`cbi-tab ${activeTab === 'analysis' ? 'active' : ''}`}
                onClick={() => setActiveTab('analysis')}
              >
                📊 Risk Analysis
              </button>
              <button 
                className={`cbi-tab ${activeTab === 'actions' ? 'active' : ''}`}
                onClick={() => setActiveTab('actions')}
              >
                ⚡ Recent Actions
              </button>
            </div>

            {/* Enhanced Tab Content */}
            <div className="cbi-tab-content">
              {activeTab === 'alerts' && data.fraud_transactions && data.fraud_transactions.length > 0 && (
                <div className="cbi-alerts-section">
                  <div className="cbi-alerts-header">
                    <h3 className="cbi-alerts-title">🔴 Critical Fraud Alerts</h3>
                    <span className="cbi-alerts-count">{data.fraud_transactions.length} critical alerts requiring immediate attention</span>
                  </div>
                  <div className="cbi-alerts-list">
                    {data.fraud_transactions.slice(0, 15).map((txn, index) => (
                      <div 
                        className={`cbi-alert-item ${
                          blockedTransactions.has(txn.transaction_id) ? 'blocked' : 
                          verifiedTransactions.has(txn.transaction_id) ? 'verified' : ''
                        }`} 
                        key={index}
                        data-transaction-id={txn.transaction_id}
                      >
                        <div className="cbi-alert-header">
                          <div className="cbi-alert-severity">
                            {txn.risk_score >= 80 ? '🔴' : txn.risk_score >= 60 ? '🟠' : '🟡'}
                          </div>
                          <div className="cbi-alert-id">Transaction: {txn.transaction_id}</div>
                          <div className={`cbi-risk-badge ${txn.risk_level?.toLowerCase()}`}>
                            {txn.risk_score}/100 ({txn.risk_level})
                          </div>
                        </div>
                        
                        <div className="cbi-alert-details">
                          <div className="cbi-transaction-flow">
                            <strong>{txn.payer_vpa}</strong> → <strong>{txn.beneficiary_vpa}</strong>
                          </div>
                          <div className="cbi-transaction-amount">
                            Amount: <strong>₹{txn.amount?.toLocaleString('en-IN')}</strong>
                          </div>
                          <div className="cbi-alert-reason">{txn.explanation}</div>
                          
                          {txn.risk_factors && txn.risk_factors.length > 0 && (
                            <div className="cbi-risk-factors">
                              <strong>Risk Indicators:</strong>
                              <ul>
                                {txn.risk_factors.slice(0, 3).map((factor, idx) => (
                                  <li key={idx}>{factor}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                        
                        <div className="cbi-alert-actions">
                          <button 
                            className="cbi-action-btn cbi-block-btn"
                            onClick={() => handleTransactionAction(txn.transaction_id, 'blocked')}
                            disabled={blockedTransactions.has(txn.transaction_id) || verifiedTransactions.has(txn.transaction_id)}
                          >
                            🚫 Block Account
                          </button>
                          <button 
                            className="cbi-action-btn cbi-verify-btn"
                            onClick={() => handleTransactionAction(txn.transaction_id, 'verified')}
                            disabled={blockedTransactions.has(txn.transaction_id) || verifiedTransactions.has(txn.transaction_id)}
                          >
                            ✅ Mark Safe
                          </button>
                        </div>
                        
                        {(blockedTransactions.has(txn.transaction_id) || verifiedTransactions.has(txn.transaction_id)) && (
                          <div className="cbi-status-indicator">
                            {blockedTransactions.has(txn.transaction_id) ? 
                              '🚫 Account Blocked - Under Investigation' : 
                              '✅ Transaction Verified - Cleared for Processing'
                            }
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'analysis' && (
                <div className="cbi-analysis-section">
                  <h3 className="cbi-section-title">📊 Risk Analysis Dashboard</h3>
                  <div className="cbi-analysis-grid">
                    <div className="cbi-analysis-card">
                      <h4>Transaction Volume Analysis</h4>
                      <div className="cbi-metric-display">
                        <div className="cbi-large-metric">
                          {data.total_transactions?.toLocaleString()}
                        </div>
                        <div className="cbi-metric-label">Total Transactions</div>
                      </div>
                      <div className="cbi-sub-metrics">
                        <div className="cbi-sub-metric">
                          <span>Fraud Rate:</span>
                          <span className="danger">{((data.fraud_detected / data.total_transactions) * 100).toFixed(2)}%</span>
                        </div>
                        <div className="cbi-sub-metric">
                          <span>System Accuracy:</span>
                          <span className="success">{(100 - ((data.fraud_detected / data.total_transactions) * 100)).toFixed(1)}%</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="cbi-analysis-card">
                      <h4>Risk Distribution Analysis</h4>
                      <div className="cbi-risk-bars">
                        <div className="cbi-risk-bar critical">
                          <span className="cbi-risk-label">Critical Risk</span>
                          <div className="cbi-risk-progress">
                            <div className="cbi-risk-fill" style={{ 
                              width: `${data.fraud_transactions ? (riskDistribution.critical / data.fraud_transactions.length * 100) : 0}%` 
                            }}></div>
                          </div>
                          <span className="cbi-risk-count">{riskDistribution.critical}</span>
                        </div>
                        <div className="cbi-risk-bar high">
                          <span className="cbi-risk-label">High Risk</span>
                          <div className="cbi-risk-progress">
                            <div className="cbi-risk-fill" style={{ 
                              width: `${data.fraud_transactions ? (riskDistribution.high / data.fraud_transactions.length * 100) : 0}%` 
                            }}></div>
                          </div>
                          <span className="cbi-risk-count">{riskDistribution.high}</span>
                        </div>
                        <div className="cbi-risk-bar medium">
                          <span className="cbi-risk-label">Medium Risk</span>
                          <div className="cbi-risk-progress">
                            <div className="cbi-risk-fill" style={{ 
                              width: `${data.fraud_transactions ? (riskDistribution.medium / data.fraud_transactions.length * 100) : 0}%` 
                            }}></div>
                          </div>
                          <span className="cbi-risk-count">{riskDistribution.medium}</span>
                        </div>
                        <div className="cbi-risk-bar low">
                          <span className="cbi-risk-label">Low Risk</span>
                          <div className="cbi-risk-progress">
                            <div className="cbi-risk-fill" style={{ 
                              width: `${data.fraud_transactions ? (riskDistribution.low / data.fraud_transactions.length * 100) : 0}%` 
                            }}></div>
                          </div>
                          <span className="cbi-risk-count">{riskDistribution.low}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'actions' && (
                <div className="cbi-actions-section">
                  <h3 className="cbi-section-title">⚡ Recent Administrative Actions</h3>
                  <div className="cbi-timeline">
                    {blockedTransactions.size > 0 && Array.from(blockedTransactions).slice(0, 5).map((txnId, idx) => (
                      <div className="cbi-timeline-item" key={`blocked-${idx}`}>
                        <div className="cbi-timeline-icon blocked">🚫</div>
                        <div className="cbi-timeline-content">
                          <h4>Account Blocked</h4>
                          <p>Transaction {txnId} blocked due to high fraud risk</p>
                          <span className="cbi-timeline-time">Just now</span>
                        </div>
                      </div>
                    ))}
                    {verifiedTransactions.size > 0 && Array.from(verifiedTransactions).slice(0, 5).map((txnId, idx) => (
                      <div className="cbi-timeline-item" key={`verified-${idx}`}>
                        <div className="cbi-timeline-icon verified">✅</div>
                        <div className="cbi-timeline-content">
                          <h4>Transaction Verified</h4>
                          <p>Transaction {txnId} verified and cleared for processing</p>
                          <span className="cbi-timeline-time">Just now</span>
                        </div>
                      </div>
                    ))}
                    <div className="cbi-timeline-item">
                      <div className="cbi-timeline-icon system">🔄</div>
                      <div className="cbi-timeline-content">
                        <h4>AI System Updated</h4>
                        <p>Fraud detection models refreshed with latest data</p>
                        <span className="cbi-timeline-time">5 minutes ago</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {loading && (
          <div className="cbi-loading">
            <div className="cbi-spinner"></div>
            <p>Loading Central Bank Intelligence Data...</p>
            <p className="cbi-loading-sub">Analyzing fraud patterns • Updating security metrics • Preparing dashboard</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;