import axios from 'axios';

// Detect the correct API URL based on how the app is accessed
const getAPIUrl = () => {
  // In browser environment
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;

    // If accessed via IP address, use IP for API
    if (/^\d+\.\d+\.\d+\.\d+$/.test(hostname)) {
      return `http://${hostname}:8000`;
    }

    // If accessed via interpretation-service.com domain
    if (hostname.includes('interpretation-service.com')) {
      return 'http://app.interpretation-service.com:8000';
    }

    // If accessed via localhost
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:8000';
    }
  }

  // Server-side or fallback
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};

const API_URL = getAPIUrl();

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
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
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export const callAPI = {
  getActiveCalls: async () => {
    const response = await api.get('/calls/active');
    return response.data;
  },
  startCall: async (roomName: string, customerInfo?: any) => {
    const response = await api.post('/calls/start', { roomName, customerInfo });
    return response.data;
  },
  endCall: async (callId: string) => {
    const response = await api.post('/calls/end', { callId });
    return response.data;
  },
  getCallHistory: async (limit = 50) => {
    const response = await api.get(`/calls/history?limit=${limit}`);
    return response.data;
  },
};

export const queueAPI = {
  getQueue: async () => {
    const response = await api.get('/queue');
    return response.data;
  },
  getMetrics: async () => {
    const response = await api.get('/queue/metrics');
    return response.data;
  },
};
