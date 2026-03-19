import { create } from 'zustand';
import api from '../lib/axios';
import toast from 'react-hot-toast';

export const useAuthStore = create((set, get) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: true,

  // Validate token by fetching user profile
  checkAuth: async () => {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      set({ user: null, isAuthenticated: false, isLoading: false });
      return;
    }

    try {
      const { data } = await api.get('/auth/me/');
      set({ user: data.data, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  // Login action
  login: async (email, password) => {
    try {
      const { data } = await api.post('/auth/login/', { email, password });
      localStorage.setItem('access_token', data.data.access);
      localStorage.setItem('refresh_token', data.data.refresh);
      set({ user: data.data.user, isAuthenticated: true });
      toast.success('Welcome back!');
      return true;
    } catch (error) {
      toast.error(error.response?.data?.error?.message || 'Login failed');
      return false;
    }
  },

  // Register action
  register: async (username, email, password) => {
    try {
      const { data } = await api.post('/auth/register/', { username, email, password });
      localStorage.setItem('access_token', data.data.access);
      localStorage.setItem('refresh_token', data.data.refresh);
      set({ user: data.data.user, isAuthenticated: true });
      toast.success('Registration successful!');
      return true;
    } catch (error) {
      toast.error(error.response?.data?.error?.message || 'Registration failed');
      return false;
    }
  },

  // Logout action
  logout: async () => {
    const refresh = localStorage.getItem('refresh_token');
    if (refresh) {
      try {
        await api.post('/auth/logout/', { refresh });
      } catch (e) {
        console.error("Logout failed on server, continuing local logout");
      }
    }
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false });
    toast.success('Logged out successfully');
  }
}));

// Listen for axios interceptor logout triggers
window.addEventListener('auth-logout', () => {
  useAuthStore.getState().logout();
});
