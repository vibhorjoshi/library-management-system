/**
 * API Service
 * Handles all HTTP requests to the backend
 */

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT || '5000');

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle responses
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication endpoints
export const authAPI = {
  login: (username, password) =>
    apiClient.post('/api/token/', { username, password }),
  
  register: (username, email, password, role) =>
    apiClient.post('/api/register/', { username, email, password, role }),
  
  refreshToken: (refreshToken) =>
    apiClient.post('/api/token/refresh/', { refresh: refreshToken }),
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    return Promise.resolve();
  },
};

// Dashboard endpoint
export const dashboardAPI = {
  getDashboard: () => apiClient.get('/api/dashboard/'),
};

// Book endpoints
export const bookAPI = {
  getBooks: (params = {}) => apiClient.get('/api/books/', { params }),
  getBook: (id) => apiClient.get(`/api/books/${id}/`),
  issueBook: (bookId) => apiClient.post('/api/books/issue/', { book_id: bookId }),
  returnBook: (issuedBookId) => 
    apiClient.post('/api/books/return/', { issued_book_id: issuedBookId }),
};

// User endpoints
export const userAPI = {
  getProfile: () => apiClient.get('/api/users/profile/'),
  updateProfile: (data) => apiClient.put('/api/users/profile/', data),
};

export default apiClient;
