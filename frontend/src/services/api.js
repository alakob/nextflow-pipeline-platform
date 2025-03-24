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
    
    // Don't override Content-Type if it's a FormData object
    if (config.data instanceof FormData) {
      // Remove the Content-Type header to let axios set it with boundary
      delete config.headers['Content-Type'];
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Authentication API calls
export const authApi = {
  login: async (username, password) => {
    // Use URLSearchParams for proper form data encoding
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    try {
      const response = await apiClient.post('/login', formData.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      if (response.data.access_token) {
        // Store token with explicit storage and return the data
        localStorage.setItem('token', response.data.access_token);
        return response.data;
      }
      console.error('Login response missing access_token:', response.data);
      return null;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },
  
  register: async (username, password) => {
    // Use URLSearchParams for proper form data encoding
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    try {
      const response = await apiClient.post('/register', formData.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  },
  
  logout: () => {
    localStorage.removeItem('token');
    // Clear any other auth-related data
    console.log('User logged out, token removed');
  },
  
  getCurrentUser: async () => {
    try {
      // Check if we have a token first
      const token = localStorage.getItem('token');
      if (!token) {
        console.log('No token found in localStorage');
        throw new Error('Not authenticated');
      }
      
      const response = await apiClient.get('/users/me');
      return response.data;
    } catch (error) {
      console.error('Get current user error:', error);
      // If 401 unauthorized, clear token as it might be expired
      if (error.response && error.response.status === 401) {
        localStorage.removeItem('token');
      }
      throw error;
    }
  },
  
  // Check if user is authenticated based on token existence
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
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
      // Ensure params is an object and then stringify it for proper JSON serialization
      const paramsToSubmit = typeof params === 'string' ? params : JSON.stringify(params || {});
      
      console.log('Submitting job with processed parameters:', {
        pipeline_id: pipelineId,
        params: paramsToSubmit,
        description: description || ''
      });
      
      const response = await apiClient.post('/jobs', {
        pipeline_id: pipelineId,
        params: paramsToSubmit, // Send stringified params
        description: description || ''
      });
      
      // Log the response structure for debugging
      console.log('API response from job submission:', response.data);
      
      // Ensure we have a consistent response format
      if (!response.data) {
        throw new Error('Empty response received from server');
      }
      
      return response.data;
    } catch (error) {
      console.error('Submit job error:', error);
      throw error;
    }
  },
  
  getJobStatus: async (jobId) => {
    try {
      console.log('Fetching job details for job ID:', jobId);
      
      // Ensure job ID is properly formatted
      // Check if it includes 'job-' prefix, as that's how they're stored in backend
      const formattedJobId = jobId.startsWith('job-') ? jobId : `job-${jobId}`;
      
      const response = await apiClient.get(`/jobs/${formattedJobId}`);
      
      console.log('Job details API response:', response.data);
      
      if (!response.data) {
        throw new Error('Empty job details response from server');
      }
      
      return response.data;
    } catch (error) {
      console.error('Get job status error:', error);
      throw error;
    }
  },
  
  getJobDownloadLink: async (jobId) => {
    try {
      const response = await apiClient.get(`/jobs/${jobId}/download`);
      return response.data;
    } catch (error) {
      console.error('Get job download link error:', error);
      throw error;
    }
  },
  
  listJobs: async () => {
    try {
      const response = await apiClient.get('/jobs');
      // Extract jobs array from the response structure
      return response.data.jobs || [];
    } catch (error) {
      console.error('List jobs error:', error);
      throw error;
    }
  },
  
  cancelJob: async (jobId) => {
    try {
      // Format job ID consistently, matching the same approach as getJobStatus
      const formattedJobId = jobId.startsWith('job-') ? jobId : `job-${jobId}`;
      
      const response = await apiClient.delete(`/jobs/${formattedJobId}`);
      return response.data;
    } catch (error) {
      console.error('Cancel job error:', error);
      throw error;
    }
  }
};

export default apiClient;
