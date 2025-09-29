import axios from 'axios';
import Cookies from 'js-cookie';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api/v1';

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth cookie and redirect to login
      Cookies.remove('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data: { email: string; password: string; firstName?: string; lastName?: string }) =>
    api.post('/auth/register', data),
  
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  
  logout: () =>
    api.post('/auth/logout'),
  
  getProfile: () =>
    api.get('/auth/profile'),
};

// Threads API
export const threadsAPI = {
  getAll: (page = 1, limit = 20) =>
    api.get(`/threads?page=${page}&limit=${limit}`),
  
  getById: (id: string) =>
    api.get(`/threads/${id}`),
  
  create: (data: { title: string }) =>
    api.post('/threads', data),
  
  update: (id: string, data: { title?: string }) =>
    api.put(`/threads/${id}`, data),
  
  delete: (id: string) =>
    api.delete(`/threads/${id}`),
};

// Chat API
export const chatAPI = {
  sendMessage: (data: { message: string; threadId: string; metadata?: any }) =>
    api.post('/chat/send', data),
  
  getMessages: (threadId: string, page = 1, limit = 50) =>
    api.get(`/chat/threads/${threadId}/messages?page=${page}&limit=${limit}`),
  
  // Server-sent events for streaming
  streamMessage: (data: { message: string; threadId: string; metadata?: any }) => {
    return new EventSource(
      `${API_BASE_URL}/chat/stream`,
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${Cookies.get('auth_token')}`,
        },
      }
    );
  },
};

export default api;