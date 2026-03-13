/**
 * API service for communicating with the backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.message);
    
    // Transform error for better handling
    const errorMessage = error.response?.data?.detail || error.message || 'An unexpected error occurred';
    const errorCode = error.response?.data?.error_code;
    
    return Promise.reject({
      message: errorMessage,
      code: errorCode,
      status: error.response?.status,
      originalError: error,
    });
  }
);

/**
 * Initiate a new crawl job
 * @param {string} url - The URL to crawl
 * @param {number} depth - The crawl depth (1-100)
 * @returns {Promise<{job_id: string, status: string}>}
 */
export const initiateCrawl = async (url, depth) => {
  try {
    const response = await apiClient.post('/api/crawl', {
      url,
      depth,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get the status and results of a crawl job
 * @param {string} jobId - The job ID to query
 * @returns {Promise<Object>} Job status and results
 */
export const getJobStatus = async (jobId) => {
  try {
    const response = await apiClient.get(`/api/crawl/${jobId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Check API health
 * @returns {Promise<{status: string}>}
 */
export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/api/health');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default {
  initiateCrawl,
  getJobStatus,
  checkHealth,
};
