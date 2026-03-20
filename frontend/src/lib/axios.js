import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach access token and prevent IE/browser caching
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Disable browser caching for GET requests to fix stale dashboard bug
    if (config.method?.toLowerCase() === 'get') {
      config.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate';
      config.headers['Pragma'] = 'no-cache';
      config.headers['Expires'] = '0';
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 & token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 Unauthorized and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token');

        // Request new access token
        const { data } = await axios.post(`${api.defaults.baseURL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const newAccessToken = data.access;
        localStorage.setItem('access_token', newAccessToken);
        
        // Update header and retry
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (err) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.dispatchEvent(new Event('auth-logout')); // Trigger Zustand logout via event
        return Promise.reject(err);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
