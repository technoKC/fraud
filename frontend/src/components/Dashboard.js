import React, { useState } from 'react';
import axios from 'axios';
import NetworkGraph from './NetworkGraph';
import getApiBaseUrl from '../utils/getApiBaseUrl';

const Dashboard = ({ data, setData }) => {
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState('');
  const [showGraph, setShowGraph] = useState(false);
  const [blockedTransactions, setBlockedTransactions] = useState(new Set());
  const [verifiedTransactions, setVerifiedTransactions] = useState(new Set());

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || !file.name.endsWith('.csv')) {
      alert('Please upload a CSV file');
      return;
    }

    setFileName(file.name);
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log('Checking backend connection...');
      const healthCheck = await axios.get(`${getApiBaseUrl()}/`);
      console.log('Backend is running:', healthCheck.data);

      console.log('Uploading file:', file.name);
      const response = await axios.post(`${getApiBaseUrl()}/detect-public/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000,
      });

      console.log('Upload successful:', response.data);
      setData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error details:', error);
      setLoading(false);
      
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        alert(`❌ Cannot connect to backend server!\n\nPlease ensure the backend is running and accessible at: ${getApiBaseUrl()}`);
      } else if (error.response) {
        const status = error.response.status;
        const message = error.response.data?.detail || error.response.statusText;
        
        if (status === 422) {
          alert('❌ Invalid CSV format!\n\nPlease check your CSV file has the required columns:\n- TXN_TIMESTAMP\n- TRANSACTION_ID\n- AMOUNT\n- PAYER_VPA\n- BENEFICIARY_VPA\n- IS_FRAUD (optional)');
        } else if (status === 500) {
          alert('❌ Server error!\n\nError processing your file. Please check:\n1. CSV format is correct\n2. Backend console for error details');
        } else {
          alert(`❌ Server Error (${status})\n\n${message}`);
        }
      } else if (error.request) {
        alert('❌ Request timeout!\n\nThe server is not responding. Please:\n1. Check if backend is running\n2. Try with a smaller CSV file\n3. Check backend console for errors');
      } else {
        alert(`❌ Upload Error\n\n${error.message}`);
      }
    }
  };

  const blockTransaction = (index, transactionId) => {
    const statusElement = document.getElementById(`status-${index}`);
    const alertElement = document.getElementById(`alert-${index}`);
    
    if (statusElement && alertElement) {
      statusElement.textContent = '🚫 Transaction Blocked';
      statusElement.style.color = '#ef4444';
      alertElement.style.backgroundColor = 'rgba(239, 68, 68, 0.2)';
      alertElement.style.borderColor = 'rgba(239, 68, 68, 0.5)';
      alertElement.style.boxShadow = '0 0 15px rgba(239, 68, 68, 0.3)';
      
      setBlockedTransactions(prev => new Set([...prev, transactionId]));
      
      // Update data state
      if (data && data.fraud_transactions) {
        const updatedTransactions = data.fraud_transactions.map(txn => 
          txn.transaction_id === transactionId ? {...txn, status: 'blocked'} : txn
        );
        setData({...data, fraud_transactions: updatedTransactions});
      }
    }
  };

  const verifyTransaction = (index, transactionId) => {
    const statusElement = document.getElementById(`status-${index}`);
    const alertElement = document.getElementById(`alert-${index}`);
    
    if (statusElement && alertElement) {
      statusElement.textContent = '✅ Transaction Verified';
      statusElement.style.color = '#22c55e';
      alertElement.style.backgroundColor = 'rgba(34, 197, 94, 0.2)';
      alertElement.style.borderColor = 'rgba(34, 197, 94, 0.5)';
      alertElement.style.boxShadow = '0 0 15px rgba(34, 197, 94, 0.3)';
      
      setVerifiedTransactions(prev => new Set([...prev, transactionId]));
      
      // Update data state
      if (data && data.fraud_transactions) {
        const updatedTransactions = data.fraud_transactions.map(txn => 
          txn.transaction_id === transactionId ? {...txn, status: 'verified'} : txn
        );
        setData({...data, fraud_transactions: updatedTransactions});
      }
    }
  };

  // FIXED: Complete PDF Report Generation with FraudShield Logo
  const generateAnalysisPDF = async () => {
  if (!data) {
    alert('No data available to generate report');
    return;
  }

  try {
    const { jsPDF } = await import('jspdf');
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    
    // Add FraudShield Logo
    try {
      // Add white background for logo
      doc.setFillColor(255, 255, 255);
      doc.roundedRect(15, 10, 40, 40, 3, 3, 'F');
      
      // Try to load the actual logo image
      const img = new Image();
      img.src = '/logo.png';
      
      await new Promise((resolve, reject) => {
        img.onload = () => {
          doc.addImage(img, 'PNG', 20, 15, 30, 30);
          resolve();
        };
        img.onerror = () => {
          console.log('Logo not found, using text placeholder');
          doc.setFillColor(59, 130, 246);
          doc.roundedRect(20, 15, 30, 30, 3, 3, 'F');
          doc.setFontSize(12);
          doc.setTextColor(255, 255, 255);
          doc.text('FS', 35, 35, { align: 'center' });
          resolve();
        };
      });
    } catch (e) {
      console.log('Error loading logo:', e);
    }
    
    // Header
    doc.setFontSize(24);
    doc.setTextColor(59, 130, 246);
    doc.text('FraudShield Analysis Report', pageWidth / 2, 30, { align: 'center' });
    
    doc.setFontSize(16);
    doc.setTextColor(100, 116, 139);
    doc.text('AI-Powered Fraud Detection System', pageWidth / 2, 45, { align: 'center' });
    
    doc.setFontSize(12);
    doc.text(`Generated: ${new Date().toLocaleString()}`, pageWidth / 2, 60, { align: 'center' });
    
    // Executive Summary Box
    doc.setDrawColor(59, 130, 246);
    doc.setFillColor(240, 249, 255);
    doc.roundedRect(15, 75, pageWidth - 30, 50, 3, 3, 'FD');
    
    doc.setFontSize(16);
    doc.setTextColor(30, 64, 175);
    doc.text('Executive Summary', 20, 90);
    
    doc.setFontSize(11);
    doc.setTextColor(51, 65, 85);
    
    const summaryData = [
      `Total Transactions Analyzed: ${data.total_transactions?.toLocaleString() || 0}`,
      `Fraud Cases Detected: ${data.fraud_detected || 0}`,
      `Transactions Blocked: ${blockedTransactions.size}`,
      `Transactions Verified: ${verifiedTransactions.size}`,
      `Detection Accuracy: ${data.total_transactions ? (100 - ((data.fraud_detected / data.total_transactions) * 100)).toFixed(1) : 100}%`,
      `Fraud Rate: ${data.total_transactions ? ((data.fraud_detected / data.total_transactions) * 100).toFixed(2) : 0}%`
    ];
    
    summaryData.forEach((item, index) => {
      const x = index < 3 ? 20 : 120;
      const y = 100 + ((index % 3) * 8);
      doc.text(item, x, y);
    });
    
    // AI Analysis Section
    if (data.ai_summary) {
      doc.setFontSize(16);
      doc.setTextColor(30, 64, 175);
      doc.text('AI Intelligence Analysis', 20, 145);
      
      doc.setFontSize(11);
      doc.setTextColor(51, 65, 85);
      
      const aiData = [
        `AI Fraud Detection: ${data.ai_summary.ai_fraud_detected || data.fraud_detected}`,
        `High Risk Transactions: ${data.ai_summary.high_risk_transactions || 0}`,
        `Average Risk Score: ${data.ai_summary.average_risk_score?.toFixed(1) || 0}/100`,
        `Detection Confidence: ${(data.ai_summary.confidence_level * 100).toFixed(1) || 95}%`,
        `Model Version: ${data.ai_summary.model_version || 'FraudShield-AI-v2.0'}`
      ];
      
      aiData.forEach((item, index) => {
        doc.text(item, 20, 155 + (index * 8));
      });
    }
    
    // Critical Fraud Transactions Section
    doc.setFontSize(16);
    doc.setTextColor(220, 38, 38);
    doc.text('Critical Fraud Transactions', 20, 195);
    
    if (data.fraud_transactions && data.fraud_transactions.length > 0) {
      doc.setFontSize(10);
      doc.setTextColor(51, 65, 85);
      
      // Table headers
      const headers = ['Transaction ID', 'Amount (Rs)', 'Risk Score', 'Status'];
      const headerY = 205;
      const colWidths = [55, 35, 30, 35];
      let xPos = 20;
      
      // Header background
      doc.setFillColor(59, 130, 246);
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
        
        if (rowY > pageHeight - 40) break;
        
        // Alternating row background
        if (i % 2 === 0) {
          doc.setFillColor(248, 250, 252);
          doc.rect(15, rowY - 5, pageWidth - 30, 12, 'F');
        }
        
        xPos = 20;
        doc.setFont(undefined, 'normal');
        doc.setTextColor(51, 65, 85);
        
        // Transaction ID
        const txnId = txn.transaction_id.length > 18 ? 
          txn.transaction_id.substring(0, 15) + '...' : txn.transaction_id;
        doc.text(txnId, xPos, rowY);
        xPos += colWidths[0];
        
        // Amount
        doc.text(`Rs ${txn.amount?.toLocaleString('en-IN') || 0}`, xPos, rowY);
        xPos += colWidths[1];
        
        // Risk Score
        doc.setTextColor(220, 38, 38);
        doc.text(`${txn.risk_score || 0}/100`, xPos, rowY);
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
    }
    
    // Footer
    const footerY = pageHeight - 30;
    doc.setFillColor(59, 130, 246);
    doc.rect(0, footerY - 5, pageWidth, 40, 'F');
    
    doc.setFontSize(10);
    doc.setTextColor(255, 255, 255);
    doc.text('FraudShield - AI-Powered Fraud Detection System', pageWidth / 2, footerY + 5, { align: 'center' });
    doc.text(`Generated on ${new Date().toLocaleDateString()} | Detect • Explain • Protect`, pageWidth / 2, footerY + 15, { align: 'center' });
    doc.text('This report contains confidential fraud analysis data.', pageWidth / 2, footerY + 25, { align: 'center' });
    
    // Save the PDF
    doc.save(`FraudShield_Analysis_Report_${new Date().toISOString().split('T')[0]}.pdf`);
    
    alert('PDF report generated successfully!');
    
  } catch (error) {
    console.error('PDF generation error:', error);
    alert('Error generating PDF report. Please try again.');
  }
};

  return (
    <div id="dashboard" className="page active">
      <div className="dashboard">
        <div className="dashboard-header">
          <h2 className="dashboard-title">
            <span style={{ marginRight: '10px' }}>🛡️</span>
            FraudShield - AI Fraud Detection Dashboard
          </h2>
          <div className="status-indicator">
            <span className="status-dot active"></span>
            <span>System Active</span>
          </div>
        </div>

        {/* Statistics Grid */}
        {data && (
          <>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">📊</div>
                <div className="stat-value">{data.total_transactions}</div>
                <div className="stat-label">Total Transactions</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">🚨</div>
                <div className="stat-value fraud-stat">{data.fraud_detected}</div>
                <div className="stat-label">Fraud Detected</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">🚫</div>
                <div className="stat-value warning-stat">{blockedTransactions.size}</div>
                <div className="stat-label">Transactions Blocked</div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">✅</div>
                <div className="stat-value success-stat">{verifiedTransactions.size}</div>
                <div className="stat-label">Transactions Verified</div>
              </div>
            </div>

            {/* Enhanced AI Summary */}
            {data.ai_summary && (
              <div className="ai-summary-enhanced">
                <h3 className="ai-title">🧠 AI Intelligence Analysis</h3>
                <div className="ai-summary-grid">
                  <div className="ai-card">
                    <div className="ai-card-header">
                      <span className="ai-icon">🔍</span>
                      <h4>Detection Overview</h4>
                    </div>
                    <div className="ai-stats">
                      <div className="ai-stat">
                        <span className="ai-label">Total Analyzed</span>
                        <span className="ai-value">{data.ai_summary.total_analyzed?.toLocaleString()}</span>
                      </div>
                      <div className="ai-stat">
                        <span className="ai-label">AI Fraud Detected</span>
                        <span className="ai-value fraud-stat">{data.ai_summary.ai_fraud_detected || data.fraud_detected}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="ai-card">
                    <div className="ai-card-header">
                      <span className="ai-icon">⚠️</span>
                      <h4>Risk Assessment</h4>
                    </div>
                    <div className="ai-stats">
                      <div className="ai-stat">
                        <span className="ai-label">High Risk Transactions</span>
                        <span className="ai-value warning-stat">{data.ai_summary.high_risk_transactions}</span>
                      </div>
                      <div className="ai-stat">
                        <span className="ai-label">Average Risk Score</span>
                        <span className="ai-value">{data.ai_summary.average_risk_score?.toFixed(1)}/100</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="ai-card">
                    <div className="ai-card-header">
                      <span className="ai-icon">🎯</span>
                      <h4>System Performance</h4>
                    </div>
                    <div className="ai-stats">
                      <div className="ai-stat">
                        <span className="ai-label">Confidence Level</span>
                        <span className="ai-value success-stat">{(data.ai_summary.confidence_level * 100).toFixed(1)}%</span>
                      </div>
                      <div className="ai-stat">
                        <span className="ai-label">Model Version</span>
                        <span className="ai-value">{data.ai_summary.model_version || 'v2.0'}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* Enhanced Upload Section */}
        {!data && !loading && (
          <div className="upload-section-enhanced">
            <div className="upload-icon-blue">📁</div>
            <h3>Upload Transaction Data</h3>
            <p>Drag and drop your CSV file here or click to browse</p>
            <p style={{ fontSize: '0.9rem', color: '#94a3b8', marginTop: '0.5rem' }}>
              ℹ️ For advanced features and authenticated uploads, use Central Bank or MANIT portals
            </p>
            <div className="csv-requirements">
              <strong>Required CSV Columns:</strong>
              <br />• TXN_TIMESTAMP • TRANSACTION_ID • AMOUNT • PAYER_VPA • BENEFICIARY_VPA
              <br /><em>Optional: IS_FRAUD, DEVICE_ID, IP_ADDRESS</em>
            </div>
            <input 
              type="file" 
              id="fileInput" 
              className="file-input" 
              accept=".csv" 
              onChange={handleFileUpload}
            />
            <button className="upload-btn-enhanced" onClick={() => document.getElementById('fileInput').click()}>
              <span>📤</span> Choose CSV File
            </button>
            {fileName && <div className="file-name">Selected: {fileName}</div>}
          </div>
        )}

        {/* Loading Status */}
        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>🧠 Processing transactions with AI algorithms...</p>
            <p className="loading-sub">Analyzing patterns • Detecting anomalies • Building network graph</p>
          </div>
        )}

        {/* Action Buttons */}
        {data && (
          <div className="action-buttons-enhanced">
            <button 
              className="btn-enhanced btn-primary-enhanced" 
              onClick={() => setShowGraph(!showGraph)}
            >
              {showGraph ? (
                <>
                  <span>📉</span> Hide Network Graph
                </>
              ) : (
                <>
                  <span>📈</span> Show Network Graph
                </>
              )}
            </button>
            <button 
              className="btn-enhanced btn-report-enhanced" 
              onClick={generateAnalysisPDF}
            >
              <span>📄</span> Download PDF Report
            </button>
          </div>
        )}

        {/* Enhanced Network Graph */}
        {data && showGraph && data.graph_data && (
          <div style={{ marginBottom: '2rem' }}>
            <NetworkGraph graphData={data.graph_data} />
          </div>
        )}

        {/* Enhanced Fraud Alerts */}
        {data && data.fraud_transactions && data.fraud_transactions.length > 0 && (
          <div className="fraud-alerts-enhanced">
            <div className="alerts-header">
              <h3>🚨 AI-Detected Fraud Alerts</h3>
              <span className="alert-count-enhanced">{data.fraud_transactions.length} suspicious transactions</span>
            </div>
            <div className="alerts-list-enhanced">
              {data.fraud_transactions.slice(0, 10).map((txn, index) => (
                <div className="alert-item-enhanced" id={`alert-${index}`} key={index}>
                  <div className="alert-content">
                    <div className="alert-header-enhanced">
                      <span className="alert-id">ID: {txn.transaction_id}</span>
                      <span className={`risk-badge-enhanced ${txn.risk_level?.toLowerCase()}`}>
                        {txn.risk_score}/100 ({txn.risk_level})
                      </span>
                    </div>
                    <div className="alert-details-enhanced">
                      <div className="alert-flow">
                        <strong>{txn.payer_vpa}</strong> → <strong>{txn.beneficiary_vpa}</strong>
                      </div>
                      <div className="alert-amount-enhanced">
                        Amount: <strong>₹{txn.amount?.toLocaleString('en-IN')}</strong>
                      </div>
                      <div className="alert-reason-enhanced">{txn.explanation}</div>
                      {txn.risk_factors && txn.risk_factors.length > 0 && (
                        <div className="risk-factors-enhanced">
                          <strong>Risk Factors:</strong>
                          <ul>
                            {txn.risk_factors.slice(0, 3).map((factor, idx) => (
                              <li key={idx}>{factor}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="alert-actions-enhanced">
                    <button 
                      className="btn-block-enhanced" 
                      onClick={() => blockTransaction(index, txn.transaction_id)}
                      disabled={blockedTransactions.has(txn.transaction_id) || verifiedTransactions.has(txn.transaction_id)}
                    >
                      <span>🚫</span> Block
                    </button>
                    <button 
                      className="btn-verify-enhanced" 
                      onClick={() => verifyTransaction(index, txn.transaction_id)}
                      disabled={blockedTransactions.has(txn.transaction_id) || verifiedTransactions.has(txn.transaction_id)}
                    >
                      <span>✅</span> Verify
                    </button>
                  </div>
                  <div className="status-text" id={`status-${index}`}></div>
                </div>
              ))}
            </div>
            {data.fraud_transactions.length > 10 && (
              <div style={{ textAlign: 'center', marginTop: '1rem', color: '#94a3b8' }}>
                Showing top 10 of {data.fraud_transactions.length} fraud alerts
              </div>
            )}
          </div>
        )}

        {/* No Data Message */}
        {data && data.fraud_transactions && data.fraud_transactions.length === 0 && (
          <div className="no-fraud-message">
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
            <h3 style={{ color: '#22c55e', marginBottom: '0.5rem' }}>No Fraud Detected!</h3>
            <p style={{ color: '#94a3b8' }}>
              All {data.total_transactions} transactions appear to be legitimate based on AI analysis.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;