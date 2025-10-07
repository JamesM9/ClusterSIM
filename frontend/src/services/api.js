import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
};

// Node endpoints
export const nodeAPI = {
  list: () => api.get('/api/v1/nodes'),
  get: (nodeId) => api.get(`/api/v1/nodes/${nodeId}`),
  startInstance: (nodeId, instanceData) => api.post(`/api/v1/nodes/${nodeId}/start`, instanceData),
  stopInstance: (nodeId, instanceData) => api.post(`/api/v1/nodes/${nodeId}/stop`, instanceData),
};

// Instance endpoints
export const instanceAPI = {
  list: () => api.get('/api/v1/instances'),
  get: (instanceId) => api.get(`/api/v1/instances/${instanceId}`),
};

export default api;
