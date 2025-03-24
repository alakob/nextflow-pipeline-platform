import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Create axios instance with base URL
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to include auth token in requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Authentication API calls
export const authApi = {
  login: async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    try {
      const response = await apiClient.post('/login', formData);
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        return response.data;
      }
      return null;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },
  
  register: async (username, password) => {
    try {
      const response = await apiClient.post('/register', { username, password });
      return response.data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  },
  
  logout: () => {
    localStorage.removeItem('token');
  },
  
  getCurrentUser: async () => {
    try {
      const response = await apiClient.get('/users/me');
      return response.data;
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  }
};

// Pipeline API calls
export const pipelineApi = {
  listPipelines: async () => {
    try {
      const response = await apiClient.get('/pipelines');
      return response.data;
    } catch (error) {
      console.error('List pipelines error:', error);
      throw error;
    }
  },
  
  submitJob: async (pipelineId, params, description) => {
    try {
      const response = await apiClient.post('/pipelines/jobs', {
        pipeline_id: pipelineId,
        params,
        description
      });
      return response.data;
    } catch (error) {
      console.error('Submit job error:', error);
      throw error;
    }
  },
  
  getJobStatus: async (jobId) => {
    try {
      const response = await apiClient.get(`/pipelines/jobs/${jobId}`);
      return response.data;
    } catch (error) {
      console.error('Get job status error:', error);
      throw error;
    }
  },
  
  listJobs: async () => {
    try {
      const response = await apiClient.get('/pipelines/jobs');
      return response.data;
    } catch (error) {
      console.error('List jobs error:', error);
      throw error;
    }
  },
  
  cancelJob: async (jobId) => {
    try {
      const response = await apiClient.delete(`/pipelines/jobs/${jobId}`);
      return response.data;
    } catch (error) {
      console.error('Cancel job error:', error);
      throw error;
    }
  }
};

export default apiClient;
