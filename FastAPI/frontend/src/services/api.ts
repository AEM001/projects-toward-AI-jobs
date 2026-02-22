import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: async (email: string, password: string) => {
    const response = await api.post('/api/v1/auth/register', { email, password });
    return response.data;
  },
  login: async (email: string, password: string) => {
    const response = await api.post('/api/v1/auth/login', { email, password });
    return response.data;
  },
  getCurrentUser: async () => {
    const response = await api.get('/api/v1/auth/me');
    return response.data;
  },
};

// Todo API
export const todoAPI = {
  getTodos: async (params?: {
    skip?: number;
    limit?: number;
    title?: string;
    filter_today?: boolean;
    filter_week?: boolean;
    sort_by?: string;
    sort_order?: string;
  }) => {
    const response = await api.get('/api/v1/todos', { params });
    return response.data;
  },
  createTodo: async (data: { title: string; ddl?: string }) => {
    const response = await api.post('/api/v1/todos', data);
    return response.data;
  },
  updateTodo: async (id: number, data: { title?: string; done?: boolean; ddl?: string }) => {
    const response = await api.put(`/api/v1/todos/${id}`, data);
    return response.data;
  },
  deleteTodo: async (id: number) => {
    const response = await api.delete(`/api/v1/todos/${id}`);
    return response.data;
  },
};
