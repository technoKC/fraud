import React, { useState, useEffect } from 'react';
import axios from 'axios';
import getApiBaseUrl from '../utils/getApiBaseUrl';

const ManitDashboard = ({ setIsLoggedIn, showPage }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [verifiedTransactions, setVerifiedTransactions] = useState(new Set());
  const [pendingTransactions, setPendingTransactions] = useState(new Set());
  const [receivedTransactions, setReceivedTransactions] = useState(new Set());

  // Helper function to get auth headers
  const getAuthHeaders = () => {
    const token = localStorage.getItem('authToken');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  };

  const loadManitData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${getApiBaseUrl()}/manit/data/`, {
        headers: getAuthHeaders()
      });
      setData(response.data);
      console.log('MANIT data loaded successfully:', response.data);
    } catch (error) {
      console.error('Error loading MANIT data:', error);
      
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
    
    loadManitData();
  }, []);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || !file.name.endsWith('.csv')) {
      alert('Please upload a CSV file');
      return;
    }

    setUploadedFile(file.name);
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${getApiBaseUrl()}/manit/upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          ...getAuthHeaders()
        },
      });

      setData(response.data);
      alert('✅ File uploaded successfully!');
    } catch (error) {
      console.error('Error:', error);
      if (error.response && error.response.status === 401) {
        alert('❌ Session expired. Please login again.');
        logout();
      } else {
        alert('❌ Error processing file. Please check the CSV format.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Transaction status update with proper error handling and immediate UI update
  const updateTransactionStatus = async (transactionId, status) => {
    try {
      console.log(`Attempting to update transaction ${transactionId} to ${status}`);
      
      // Proper API call with correct endpoint
      const response = await axios.post(`${getApiBaseUrl()}/manit/update-status/`, {
        transaction_id: transactionId,
        status: status
      }, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      });
      
      console.log('Status update response:', response.data);
      
      // Immediate local state update for better UX
      if (status === 'verified') {
        setVerifiedTransactions(prev => new Set([...prev, transactionId]));
        setPendingTransactions(prev => {
          const newSet = new Set(prev);
          newSet.delete(transactionId);
          return newSet;
        });
        setReceivedTransactions(prev => {
          const newSet = new Set(prev);
          newSet.delete(transactionId);
          return newSet;
        });
        
        // Update DOM element immediately
        const itemElement = document.querySelector(`[data-transaction-id="${transactionId}"]`);
        if (itemElement) {
          itemElement.className = itemElement.className.replace(/verified|pending|received/g, '') + ' verified';
        }
        
      } else if (status === 'pending') {
        setPendingTransactions(prev => new Set([...prev, transactionId]));
        setVerifiedTransactions(prev => {
          const newSet = new Set(prev);
          newSet.delete(transactionId);
          return newSet;
        });
        setReceivedTransactions(prev => {
          const newSet = new Set(prev);
          newSet.delete(transactionId);
          return newSet;
        });
        
        // Update DOM element immediately
        const itemElement = document.querySelector(`[data-transaction-id="${transactionId}"]`);
        if (itemElement) {
          itemElement.className = itemElement.className.replace(/verified|pending|received/g, '') + ' pending';
        }
        
      } else if (status === 'received') {
        setReceivedTransactions(prev => new Set([...prev, transactionId]));
        setVerifiedTransactions(prev => {
          const newSet = new Set(prev);
          newSet.delete(transactionId);
          return newSet;
        });
        setPendingTransactions(prev => {
          const newSet = new Set(prev);
          newSet.delete(transactionId);
          return newSet;
        });
        
        // Update DOM element immediately
        const itemElement = document.querySelector(`[data-transaction-id="${transactionId}"]`);
        if (itemElement) {
          itemElement.className = itemElement.className.replace(/verified|pending|received/g, '') + ' received';
        }
      }
      
      // Update data state with new counts
      if (data && data.transactions) {
        const updatedTransactions = data.transactions.map(txn => 
          txn.transaction_id === transactionId ? {...txn, status: status} : txn
        );
        
        const newData = {
          ...data,
          transactions: updatedTransactions,
          verified: status === 'verified' ? (data.verified || 0) + 1 : Math.max(0, data.verified - (verifiedTransactions.has(transactionId) ? 1 : 0)),
          pending: status === 'pending' ? (data.pending || 0) + 1 : Math.max(0, data.pending - (pendingTransactions.has(transactionId) ? 1 : 0)),
          received: status === 'received' ? (data.received || 0) + 1 : Math.max(0, data.received - (receivedTransactions.has(transactionId) ? 1 : 0))
        };
        setData(newData);
      }
      
      alert(`✅ Transaction marked as ${status} successfully`);
      
    } catch (error) {
      console.error('Error updating status:', error);
      
      if (error.response) {
        const status_code = error.response.status;
        const message = error.response.data?.detail || 'Unknown error';
        
        if (status_code === 401) {
          alert('❌ Session expired. Please login again.');
          logout();
        } else if (status_code === 403) {
          alert('❌ Access denied. You do not have permission to perform this action.');
        } else {
          alert(`❌ Error updating transaction status (${status_code}): ${message}`);
        }
      } else if (error.request) {
        alert(`❌ Cannot connect to server. Please ensure the backend is running and accessible at: ${getApiBaseUrl()}`);
      } else {
        alert(`❌ Error: ${error.message}`);
      }
    }
  };

  // Enhanced PDF Report Generation for MANIT with Logo and Professional Design
  const generateReport = async () => {
    try {
      const { jsPDF } = await import('jspdf');
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      
      // Add MANIT Logo
      const addMANITLogo = async () => {
        try {
          const img = new Image();
          img.src = '/manit.png';
          
          await new Promise((resolve, reject) => {
            img.onload = resolve;
            img.onerror = reject;
          });
          
          // Add background for logo visibility
          doc.setFillColor(255, 255, 255);
          doc.roundedRect(15, 15, 40, 40, 3, 3, 'F');
          doc.addImage(img, 'PNG', 20, 20, 30, 30);
          
        } catch (e) {
          console.log('MANIT Logo loading failed, using text placeholder');
          doc.setFillColor(59, 130, 246);
          doc.roundedRect(15, 15, 40, 40, 3, 3, 'F');
          doc.setFontSize(12);
          doc.setTextColor(255, 255, 255);
          doc.text('MANIT', 35, 32, { align: 'center' });
          doc.text('BHOPAL', 35, 42, { align: 'center' });
        }
      };

      // Add MANIT logo
      await addMANITLogo();
      
      // Professional MANIT header
      doc.setFontSize(20);
      doc.setTextColor(30, 64, 175);
      doc.text('Maulana Azad National Institute of Technology', pageWidth / 2, 25, { align: 'center' });
      
      doc.setFontSize(14);
      doc.setTextColor(59, 130, 246);
      doc.text('Bhopal, Madhya Pradesh', pageWidth / 2, 35, { align: 'center' });
      
      doc.setFontSize(16);
      doc.setTextColor(5, 150, 105);
      doc.text('Student Loan Verification System', pageWidth / 2, 50, { align: 'center' });
      
      doc.setFontSize(12);
      doc.setTextColor(100, 116, 139);
      doc.text('Official Academic Report', pageWidth / 2, 60, { align: 'center' });
      
      doc.setFontSize(10);
      doc.text('Report Generated: ' + new Date().toLocaleString(), pageWidth / 2, 70, { align: 'center' });
      
      // Executive Summary Box
      doc.setDrawColor(59, 130, 246);
      doc.setFillColor(240, 249, 255);
      doc.roundedRect(15, 80, pageWidth - 30, 55, 3, 3, 'FD');
      
      doc.setFontSize(14);
      doc.setTextColor(30, 64, 175);
      doc.text('Loan Verification Summary', 20, 95);
      
      doc.setFontSize(10);
      doc.setTextColor(51, 65, 85);
      
      const summaryData = [
        'Total Applications: ' + (data?.total_transactions || 0),
        'Fees Received: ' + (data?.received || 0),
        'Verified Students: ' + ((data?.verified || 0) + verifiedTransactions.size),
        'Pending Verification: ' + ((data?.pending || 0) + pendingTransactions.size),
        'Verification Rate: ' + (data?.verification_rate?.toFixed(1) || '0') + '%',
        'Total Amount Received: Rs ' + (data?.total_amount_received?.toLocaleString('en-IN') || '0')
      ];
      
      summaryData.forEach((item, index) => {
        const x = index < 3 ? 20 : 115;
        const y = 105 + ((index % 3) * 10);
        doc.text(item, x, y);
      });
      
      // Financial Overview
      doc.setFontSize(14);
      doc.setTextColor(5, 150, 105);
      doc.text('Financial Overview', 20, 150);
      
      doc.setFontSize(10);
      doc.setTextColor(51, 65, 85);
      
      const financialData = [
        'Total Amount Received: Rs ' + (data?.total_amount_received?.toLocaleString('en-IN') || '0'),
        'Amount Pending Verification: Rs ' + (data?.total_amount_pending?.toLocaleString('en-IN') || '0'),
        'Average Loan Amount: Rs ' + (data?.total_transactions ? Math.round(data.total_amount_received / data.total_transactions).toLocaleString('en-IN') : '0')
      ];
      
      financialData.forEach((item, index) => {
        doc.text(item, 20, 160 + (index * 10));
      });
      
      // Department-wise Statistics
      if (data?.department_statistics) {
        doc.setFontSize(14);
        doc.setTextColor(30, 64, 175);
        doc.text('Department-wise Statistics', 20, 195);
        
        doc.setFontSize(9);
        
        // Table headers
        const headers = ['Department', 'Students', 'Verified', 'Amount (Rs)'];
        const headerY = 205;
        const colWidths = [55, 25, 25, 40];
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
        let rowIndex = 0;
        Object.entries(data.department_statistics).forEach(([dept, stats]) => {
          if (stats.total > 0 && rowIndex < 10) {
            const rowY = headerY + 10 + (rowIndex * 12);
            
            if (rowY > pageHeight - 40) return;
            
            // Alternating row colors
            if (rowIndex % 2 === 0) {
              doc.setFillColor(248, 250, 252);
              doc.rect(15, rowY - 5, pageWidth - 30, 12, 'F');
            }
            
            xPos = 20;
            doc.setFont(undefined, 'normal');
            doc.setTextColor(51, 65, 85);
            
            // Department name (truncated if too long)
            const deptName = dept.length > 20 ? dept.substring(0, 17) + '...' : dept;
            doc.text(deptName, xPos, rowY);
            xPos += colWidths[0];
            
            // Students
            doc.text(stats.total.toString(), xPos, rowY);
            xPos += colWidths[1];
            
            // Verified
            doc.setTextColor(5, 150, 105);
            doc.text(stats.verified.toString(), xPos, rowY);
            xPos += colWidths[2];
            
            // Amount
            doc.setTextColor(51, 65, 85);
            doc.text('Rs ' + (stats.amount?.toLocaleString('en-IN') || '0'), xPos, rowY);
            
            rowIndex++;
          }
        });
      }
      
      // Student Transaction Details on new page
      if (data?.transactions && data.transactions.length > 0) {
        doc.addPage();
        
        doc.setFontSize(16);
        doc.setTextColor(30, 64, 175);
        doc.text('Student Loan Transactions', 20, 30);
        
        doc.setFontSize(10);
        
        // Verified Transactions
        const verifiedTxns = data.transactions.filter(t => 
          t.status?.toLowerCase() === 'verified' || verifiedTransactions.has(t.transaction_id)
        );
        
        if (verifiedTxns.length > 0) {
          doc.setFontSize(14);
          doc.setTextColor(5, 150, 105);
          doc.text('Verified Transactions', 20, 45);
          
          doc.setFontSize(8);
          
          const vHeaders = ['Student ID', 'Name', 'Semester', 'Amount', 'Bank'];
          const vHeaderY = 55;
          const vColWidths = [30, 45, 20, 30, 30];
          let vxPos = 20;
          
          // Header background
          doc.setFillColor(5, 150, 105);
          doc.rect(15, vHeaderY - 5, pageWidth - 30, 10, 'F');
          
          vHeaders.forEach((header, index) => {
            doc.setFont(undefined, 'bold');
            doc.setTextColor(255, 255, 255);
            doc.text(header, vxPos, vHeaderY);
            vxPos += vColWidths[index];
          });
          
          verifiedTxns.slice(0, 8).forEach((txn, index) => {
            const vRowY = vHeaderY + 8 + (index * 10);
            
            if (index % 2 === 0) {
              doc.setFillColor(240, 253, 244);
              doc.rect(15, vRowY - 4, pageWidth - 30, 10, 'F');
            }
            
            vxPos = 20;
            doc.setFont(undefined, 'normal');
            doc.setTextColor(51, 65, 85);
            
            doc.text(txn.student_id || '', vxPos, vRowY);
            vxPos += vColWidths[0];
            
            const studentName = (txn.student_name || '').length > 18 ? 
              (txn.student_name || '').substring(0, 15) + '...' : (txn.student_name || '');
            doc.text(studentName, vxPos, vRowY);
            vxPos += vColWidths[1];
            
            doc.text(txn.semester || '', vxPos, vRowY);
            vxPos += vColWidths[2];
            
            doc.text('Rs ' + (txn.amount?.toLocaleString('en-IN') || 0), vxPos, vRowY);
            vxPos += vColWidths[3];
            
            doc.text(txn.bank_name || '', vxPos, vRowY);
          });
        }
        
        // Pending Transactions
        const pendingTxns = data.transactions.filter(t => 
          t.status?.toLowerCase() === 'pending' || 
          pendingTransactions.has(t.transaction_id) ||
          (!verifiedTransactions.has(t.transaction_id) && !receivedTransactions.has(t.transaction_id) && t.status?.toLowerCase() !== 'verified')
        );
        
        if (pendingTxns.length > 0) {
          const startY = verifiedTxns.length > 0 ? 150 : 45;
          
          doc.setFontSize(14);
          doc.setTextColor(245, 158, 11);
          doc.text('Pending Verification', 20, startY);
          
          doc.setFontSize(8);
          
          const pHeaders = ['Student ID', 'Name', 'Amount', 'Notes'];
          const pHeaderY = startY + 10;
          const pColWidths = [30, 45, 30, 50];
          let pxPos = 20;
          
          // Header background
          doc.setFillColor(245, 158, 11);
          doc.rect(15, pHeaderY - 5, pageWidth - 30, 10, 'F');
          
          pHeaders.forEach((header, index) => {
            doc.setFont(undefined, 'bold');
            doc.setTextColor(255, 255, 255);
            doc.text(header, pxPos, pHeaderY);
            pxPos += pColWidths[index];
          });
          
          pendingTxns.slice(0, 6).forEach((txn, index) => {
            const pRowY = pHeaderY + 8 + (index * 10);
            
            if (index % 2 === 0) {
              doc.setFillColor(255, 251, 235);
              doc.rect(15, pRowY - 4, pageWidth - 30, 10, 'F');
            }
            
            pxPos = 20;
            doc.setFont(undefined, 'normal');
            doc.setTextColor(51, 65, 85);
            
            doc.text(txn.student_id || '', pxPos, pRowY);
            pxPos += pColWidths[0];
            
            const studentName = (txn.student_name || '').length > 18 ? 
              (txn.student_name || '').substring(0, 15) + '...' : (txn.student_name || '');
            doc.text(studentName, pxPos, pRowY);
            pxPos += pColWidths[1];
            
            doc.text('Rs ' + (txn.amount?.toLocaleString('en-IN') || 0), pxPos, pRowY);
            pxPos += pColWidths[2];
            
            const notes = (txn.verification_notes || 'Manual verification required').length > 25 ? 
              (txn.verification_notes || 'Manual verification required').substring(0, 22) + '...' : 
              (txn.verification_notes || 'Manual verification required');
            doc.text(notes, pxPos, pRowY);
          });
        }
      }
      
      // Professional MANIT footer
      const footerY = pageHeight - 35;
      doc.setFillColor(30, 64, 175);
      doc.rect(0, footerY, pageWidth, 35, 'F');
      
      doc.setFontSize(10);
      doc.setTextColor(255, 255, 255);
      doc.text('MANIT Bhopal - Academic Office', pageWidth / 2, footerY + 10, { align: 'center' });
      doc.text('Generated by MANIT Academic Management System | ' + new Date().toLocaleDateString(), pageWidth / 2, footerY + 20, { align: 'center' });
      doc.text('This document is for academic and administrative purposes only.', pageWidth / 2, footerY + 30, { align: 'center' });
      
      // Save PDF
      doc.save('MANIT_Loan_Verification_Report_' + new Date().toISOString().split('T')[0] + '.pdf');
      
      alert('✅ MANIT PDF report generated successfully!');
      
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

  // Filter buttons functionality with proper state management
  const [currentFilter, setCurrentFilter] = useState('all');

  const getFilteredTransactions = () => {
    if (!data?.transactions) return [];
    
    switch (currentFilter) {
      case 'verified':
        return data.transactions.filter(t => 
          t.status?.toLowerCase() === 'verified' || verifiedTransactions.has(t.transaction_id)
        );
      case 'pending':
        return data.transactions.filter(t => 
          t.status?.toLowerCase() === 'pending' || 
          pendingTransactions.has(t.transaction_id) ||
          (!verifiedTransactions.has(t.transaction_id) && !receivedTransactions.has(t.transaction_id) && t.status?.toLowerCase() !== 'verified' && t.status?.toLowerCase() !== 'received')
        );
      case 'received':
        return data.transactions.filter(t => 
          t.status?.toLowerCase() === 'received' || receivedTransactions.has(t.transaction_id)
        );
      default:
        return data.transactions;
    }
  };

  return (
    <div id="manitDashboard" className="page active">
      <div className="dashboard manit-dashboard-enhanced">
        {/* Enhanced MANIT Header */}
        <div className="manit-header">
          <div className="manit-logo-section">
            <div className="manit-logo">
              <img src="/manit.png" alt="MANIT" className="manit-logo-img" />
            </div>
            <div className="manit-title-section">
              <h1 className="manit-main-title">Maulana Azad National Institute of Technology</h1>
              <h2 className="manit-subtitle">Bhopal, Madhya Pradesh</h2>
              <div className="manit-tagline">Student Loan Verification System</div>
            </div>
          </div>
          <button className="manit-logout-btn" onClick={logout}>
            <span>🚪</span> Secure Logout
          </button>
        </div>

        {data && (
          <>
            {/* Enhanced Statistics Cards */}
            <div className="manit-stats-grid">
              <div className="manit-stat-card primary">
                <div className="manit-stat-icon">📄</div>
                <div className="manit-stat-value">{data.total_transactions}</div>
                <div className="manit-stat-label">Total Applications</div>
              </div>
              <div className="manit-stat-card info">
                <div className="manit-stat-icon">💰</div>
                <div className="manit-stat-value">{(data.received || 0) + receivedTransactions.size}</div>
                <div className="manit-stat-label">Fees Received</div>
              </div>
              <div className="manit-stat-card success">
                <div className="manit-stat-icon">✅</div>
                <div className="manit-stat-value">{(data.verified || 0) + verifiedTransactions.size}</div>
                <div className="manit-stat-label">Verified Students</div>
              </div>
              <div className="manit-stat-card warning">
                <div className="manit-stat-icon">⏳</div>
                <div className="manit-stat-value">{(data.pending || 0) + pendingTransactions.size}</div>
                <div className="manit-stat-label">Pending Verification</div>
              </div>
            </div>

            {/* Financial Summary */}
            <div className="manit-financial-summary">
              <h3 className="manit-summary-title">💰 Financial Overview</h3>
              <div className="manit-financial-grid">
                <div className="manit-financial-item">
                  <span className="manit-financial-label">Total Amount Received</span>
                  <span className="manit-financial-value success">₹{data.total_amount_received?.toLocaleString('en-IN')}</span>
                </div>
                <div className="manit-financial-item">
                  <span className="manit-financial-label">Amount Pending</span>
                  <span className="manit-financial-value warning">₹{data.total_amount_pending?.toLocaleString('en-IN')}</span>
                </div>
                <div className="manit-financial-item">
                  <span className="manit-financial-label">Verification Rate</span>
                  <span className="manit-financial-value primary">{data.verification_rate?.toFixed(1)}%</span>
                </div>
              </div>
            </div>

            {/* Action Controls */}
            <div className="manit-action-controls">
              <label className="manit-btn manit-btn-primary">
                <span>📁</span> Upload Student Data
                <input 
                  type="file" 
                  accept=".csv" 
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                />
              </label>
              {uploadedFile && <span className="manit-uploaded-file">📄 {uploadedFile}</span>}
              <button className="manit-btn manit-btn-secondary" onClick={loadManitData}>
                <span>🔄</span> Refresh Data
              </button>
              <button className="manit-btn manit-btn-success" onClick={generateReport}>
                <span>📊</span> Generate PDF Report
              </button>
            </div>

            {/* Enhanced Tab Navigation */}
            <div className="manit-tabs">
              <button 
                className={`manit-tab ${activeTab === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveTab('overview')}
              >
                📊 Overview
              </button>
              <button 
                className={`manit-tab ${activeTab === 'verification' ? 'active' : ''}`}
                onClick={() => setActiveTab('verification')}
              >
                🎓 Loan Verification
              </button>
              <button 
                className={`manit-tab ${activeTab === 'departments' ? 'active' : ''}`}
                onClick={() => setActiveTab('departments')}
              >
                🏢 Departments
              </button>
            </div>

            {/* Enhanced Tab Content */}
            <div className="manit-tab-content">
              {activeTab === 'overview' && data.semester_statistics && (
                <div className="manit-overview-section">
                  <h3 className="manit-section-title">📚 Semester-wise Analysis</h3>
                  <div className="manit-semester-grid">
                    {Object.entries(data.semester_statistics).map(([sem, stats]) => (
                      <div key={sem} className="manit-semester-card">
                        <div className="manit-semester-header">
                          <h4>Semester {sem}</h4>
                          <div className="manit-semester-badge">{stats.total} Students</div>
                        </div>
                        <div className="manit-semester-stats">
                          <div className="manit-semester-stat">
                            <span className="manit-stat-label">Verified</span>
                            <span className="manit-stat-value success">{stats.verified}</span>
                          </div>
                          <div className="manit-semester-stat">
                            <span className="manit-stat-label">Expected Fee</span>
                            <span className="manit-stat-value">₹{stats.expected_fee?.toLocaleString('en-IN')}</span>
                          </div>
                          <div className="manit-semester-stat">
                            <span className="manit-stat-label">Collected</span>
                            <span className="manit-stat-value success">₹{stats.total_amount?.toLocaleString('en-IN')}</span>
                          </div>
                        </div>
                        <div className="manit-progress-section">
                          <div className="manit-progress-label">Verification Progress</div>
                          <div className="manit-progress-bar">
                            <div 
                              className="manit-progress-fill"
                              style={{ width: `${(stats.verified / stats.total * 100) || 0}%` }}
                            ></div>
                          </div>
                          <div className="manit-progress-text">{((stats.verified / stats.total * 100) || 0).toFixed(1)}%</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'verification' && data.transactions && (
                <div className="manit-verification-section">
                  <div className="manit-verification-header">
                    <h3 className="manit-section-title">🎓 Student Loan Verification</h3>
                    <div className="manit-verification-stats">
                      <span className="manit-verification-count">
                        {getFilteredTransactions().length} of {data.transactions.length} applications
                      </span>
                    </div>
                  </div>
                  
                  {/* Filter buttons with proper functionality */}
                  <div className="manit-verification-filters">
                    <button 
                      className={`manit-filter-btn ${currentFilter === 'all' ? 'active' : ''}`}
                      onClick={() => setCurrentFilter('all')}
                    >
                      All Students ({data.transactions.length})
                    </button>
                    <button 
                      className={`manit-filter-btn ${currentFilter === 'verified' ? 'active' : ''}`}
                      onClick={() => setCurrentFilter('verified')}
                    >
                      Verified ({(data.verified || 0) + verifiedTransactions.size})
                    </button>
                    <button 
                      className={`manit-filter-btn ${currentFilter === 'pending' ? 'active' : ''}`}
                      onClick={() => setCurrentFilter('pending')}
                    >
                      Pending ({(data.pending || 0) + pendingTransactions.size})
                    </button>
                    <button 
                      className={`manit-filter-btn ${currentFilter === 'received' ? 'active' : ''}`}
                      onClick={() => setCurrentFilter('received')}
                    >
                      Received ({(data.received || 0) + receivedTransactions.size})
                    </button>
                  </div>
                  
                  <div className="manit-verification-list">
                    {getFilteredTransactions().slice(0, 25).map((txn, index) => {
                      const currentStatus = verifiedTransactions.has(txn.transaction_id) ? 'verified' : 
                                           pendingTransactions.has(txn.transaction_id) ? 'pending' : 
                                           receivedTransactions.has(txn.transaction_id) ? 'received' : 
                                           txn.status?.toLowerCase() || 'pending';
                      
                      return (
                        <div 
                          className={`manit-verification-item ${currentStatus}`} 
                          key={index}
                          data-transaction-id={txn.transaction_id}
                        >
                          <div className="manit-student-info">
                            <div className="manit-student-header">
                              <h4 className="manit-student-name">{txn.student_name}</h4>
                              <div className="manit-student-id">ID: {txn.student_id}</div>
                              <div className={`manit-status-badge ${currentStatus}`}>
                                {currentStatus.toUpperCase()}
                              </div>
                            </div>
                            
                            <div className="manit-loan-details">
                              <div className="manit-detail-grid">
                                <div className="manit-detail-item">
                                  <span className="manit-detail-label">Semester</span>
                                  <span className="manit-detail-value">{txn.semester}</span>
                                </div>
                                <div className="manit-detail-item">
                                  <span className="manit-detail-label">Department</span>
                                  <span className="manit-detail-value">{txn.department}</span>
                                </div>
                                <div className="manit-detail-item">
                                  <span className="manit-detail-label">Bank</span>
                                  <span className="manit-detail-value">{txn.bank_name}</span>
                                </div>
                                <div className="manit-detail-item">
                                  <span className="manit-detail-label">Date</span>
                                  <span className="manit-detail-value">{txn.transaction_date}</span>
                                </div>
                              </div>
                              
                              <div className="manit-amount-section">
                                <span className="manit-amount-label">Loan Amount:</span>
                                <span className="manit-amount-value">₹{txn.amount?.toLocaleString('en-IN')}</span>
                              </div>
                            </div>
                          </div>
                          
                          {/* Working verification actions with proper event handlers */}
                          <div className="manit-verification-actions">
                            {currentStatus !== 'verified' && (
                              <button 
                                className="manit-action-btn manit-verify-btn"
                                onClick={() => updateTransactionStatus(txn.transaction_id, 'verified')}
                              >
                                ✓ Verify
                              </button>
                            )}
                            {currentStatus !== 'pending' && (
                              <button 
                                className="manit-action-btn manit-pending-btn"
                                onClick={() => updateTransactionStatus(txn.transaction_id, 'pending')}
                              >
                                ⏳ Mark Pending
                              </button>
                            )}
                            {currentStatus !== 'received' && currentStatus !== 'verified' && (
                              <button 
                                className="manit-action-btn manit-received-btn"
                                onClick={() => updateTransactionStatus(txn.transaction_id, 'received')}
                              >
                                💰 Mark Received
                              </button>
                            )}
                          </div>
                          
                          {currentStatus === 'verified' && (
                            <div className="manit-verified-indicator">
                              ✅ Student Verified for Registration
                            </div>
                          )}
                          
                          {txn.verification_notes && (
                            <div className="manit-verification-notes">
                              <strong>Notes:</strong> {txn.verification_notes}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {activeTab === 'departments' && data.department_statistics && (
                <div className="manit-departments-section">
                  <h3 className="manit-section-title">🏢 Department-wise Statistics</h3>
                  <div className="manit-departments-table">
                    <div className="manit-table-header">
                      <div className="manit-table-cell">Department</div>
                      <div className="manit-table-cell">Students</div>
                      <div className="manit-table-cell">Verified</div>
                      <div className="manit-table-cell">Pending</div>
                      <div className="manit-table-cell">Amount</div>
                      <div className="manit-table-cell">Progress</div>
                    </div>
                    {Object.entries(data.department_statistics).map(([dept, stats]) => (
                      <div key={dept} className="manit-table-row">
                        <div className="manit-table-cell">
                          <strong>{dept}</strong>
                        </div>
                        <div className="manit-table-cell">{stats.total}</div>
                        <div className="manit-table-cell success">{stats.verified}</div>
                        <div className="manit-table-cell warning">{stats.pending}</div>
                        <div className="manit-table-cell">₹{stats.amount?.toLocaleString('en-IN')}</div>
                        <div className="manit-table-cell">
                          <div className="manit-dept-progress">
                            <div 
                              className="manit-dept-progress-fill"
                              style={{ width: `${(stats.verified / stats.total * 100) || 0}%` }}
                            ></div>
                            <span className="manit-dept-progress-text">
                              {((stats.verified / stats.total * 100) || 0).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {loading && (
          <div className="manit-loading">
            <div className="manit-spinner"></div>
            <p>Loading MANIT Student Data...</p>
            <p className="manit-loading-sub">Processing loan applications • Updating verification status • Preparing dashboard</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ManitDashboard;