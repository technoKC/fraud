// API Configuration and Utilities
import getApiBaseUrl from './getApiBaseUrl';

const API_BASE_URL = getApiBaseUrl();


// Token management
const getToken = () => localStorage.getItem('authToken');
const setToken = (token) => localStorage.setItem('authToken', token);
const removeToken = () => localStorage.removeItem('authToken');

// API instance with interceptors
const apiCall = async (endpoint, options = {}) => {
  const token = getToken();
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });
    
    if (response.status === 401) {
      // Token expired or invalid
      removeToken();
      window.location.href = '/';
      throw new Error('Authentication failed');
    }
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }
    
    // Handle empty responses
    const text = await response.text();
    return text ? JSON.parse(text) : {};
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

// API endpoints
export const api = {
  // Authentication
  login: async (username, password, dashboardType) => {
    const response = await apiCall('/admin/login/', {
      method: 'POST',
      body: JSON.stringify({
        username,
        password,
        dashboard_type: dashboardType,
      }),
    });
    
    if (response.access_token) {
      setToken(response.access_token);
    }
    
    return response;
  },
  
  logout: () => {
    removeToken();
  },
  
  // Fraud Detection
  detectFraud: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return await apiCall('/detect/', {
      method: 'POST',
      headers: {
        // Don't set Content-Type for FormData
      },
      body: formData,
    });
  },
  
  // Admin Dashboard
  getAdminData: async () => {
    return await apiCall('/admin/data/');
  },
  
  updateTransactionStatus: async (transactionId, action) => {
    return await apiCall('/admin/transaction-action/', {
      method: 'POST',
      body: JSON.stringify({
        transaction_id: transactionId,
        action: action,
      }),
    });
  },
  
  generateReport: async () => {
    const response = await fetch(`${API_BASE_URL}/admin/generate-report/`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to generate report');
    }
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `fraud_report_${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
  
  // MANIT Dashboard
  getManitData: async () => {
    return await apiCall('/manit/data/');
  },
  
  uploadManitData: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return await apiCall('/manit/upload/', {
      method: 'POST',
      headers: {
        // Don't set Content-Type for FormData
      },
      body: formData,
    });
  },
  
  updateManitStatus: async (transactionId, status) => {
    return await apiCall('/manit/update-status/', {
      method: 'POST',
      body: JSON.stringify({
        transaction_id: transactionId,
        status: status,
      }),
    });
  },
  
  generateManitReport: async () => {
    const response = await fetch(`${API_BASE_URL}/manit/generate-report/`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to generate report');
    }
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `manit_report_${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};

export default api;