// Utility to get the API base URL
const getApiBaseUrl = () => {
  return process.env.REACT_APP_API_URL || 'https://fraud-shield-back.onrender.com';
};

export default getApiBaseUrl; 
 