import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import { jwtDecode } from 'jwt-decode';

const API_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add JWT token
apiClient.interceptors.request.use(
  async (config) => {
    try {
      const token = await SecureStore.getItemAsync('userToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.log('Error retrieving token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor to handle response errors and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = await SecureStore.getItemAsync('refreshToken');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/api/auth/refresh/`, {
            refresh: refreshToken,
          });
          const { access } = response.data;
          await SecureStore.setItemAsync('userToken', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        await SecureStore.deleteItemAsync('userToken');
        await SecureStore.deleteItemAsync('refreshToken');
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (email, password) => {
    const response = await apiClient.post('/api/auth/login/', {
      email,
      password,
    });
    const { access, refresh, user } = response.data;
    
    // Store tokens securely
    await SecureStore.setItemAsync('userToken', access);
    if (refresh) {
      await SecureStore.setItemAsync('refreshToken', refresh);
    }
    await AsyncStorage.setItem('userData', JSON.stringify(user));
    
    return { token: access, user };
  },

  register: async (email, password, firstName, lastName, userType) => {
    const response = await apiClient.post('/api/auth/register/', {
      email,
      password,
      first_name: firstName,
      last_name: lastName,
      user_type: userType,
    });
    const { access, refresh, user } = response.data;
    
    await SecureStore.setItemAsync('userToken', access);
    if (refresh) {
      await SecureStore.setItemAsync('refreshToken', refresh);
    }
    await AsyncStorage.setItem('userData', JSON.stringify(user));
    
    return { token: access, user };
  },

  logout: async () => {
    await SecureStore.deleteItemAsync('userToken');
    await SecureStore.deleteItemAsync('refreshToken');
    await AsyncStorage.removeItem('userData');
  },

  getProfile: async () => {
    const response = await apiClient.get('/api/auth/profile/');
    return response.data;
  },
};

// Books API
export const booksAPI = {
  searchBooks: async (query, page = 1) => {
    const response = await apiClient.get('/api/books/', {
      params: { search: query, page },
    });
    return response.data;
  },

  getBookDetail: async (bookId) => {
    const response = await apiClient.get(`/api/books/${bookId}/`);
    return response.data;
  },

  issueBook: async (bookId) => {
    const response = await apiClient.post(`/api/books/${bookId}/issue/`);
    return response.data;
  },

  returnBook: async (issueId) => {
    const response = await apiClient.post(`/api/issues/${issueId}/return/`);
    return response.data;
  },

  getUserBooks: async () => {
    const response = await apiClient.get('/api/books/my-books/');
    return response.data;
  },
};

// Fine API
export const fineAPI = {
  getFines: async () => {
    const response = await apiClient.get('/api/fines/');
    return response.data;
  },

  getFineDetail: async (fineId) => {
    const response = await apiClient.get(`/api/fines/${fineId}/`);
    return response.data;
  },

  payFine: async (fineId) => {
    const response = await apiClient.post(`/api/fines/${fineId}/pay/`);
    return response.data;
  },
};

// Payment API
export const paymentAPI = {
  createPaymentIntent: async (fineId, amount) => {
    const response = await apiClient.post('/api/payments/create/', {
      fine_id: fineId,
      amount,
    });
    return response.data;
  },

  confirmPayment: async (paymentId, paymentMethodId) => {
    const response = await apiClient.post('/api/payments/confirm/', {
      payment_id: paymentId,
      payment_method_id: paymentMethodId,
    });
    return response.data;
  },

  getPaymentStatus: async (paymentId) => {
    const response = await apiClient.get(`/api/payments/${paymentId}/`);
    return response.data;
  },

  listPayments: async (page = 1) => {
    const response = await apiClient.get('/api/payments/', {
      params: { page },
    });
    return response.data;
  },
};

// Analytics API
export const analyticsAPI = {
  getUserAnalytics: async () => {
    const response = await apiClient.get('/api/analytics/user/');
    return response.data;
  },

  getFineStatistics: async () => {
    const response = await apiClient.get('/api/analytics/fines/');
    return response.data;
  },

  getOverdueBooks: async () => {
    const response = await apiClient.get('/api/analytics/overdue/');
    return response.data;
  },
};

export default apiClient;
