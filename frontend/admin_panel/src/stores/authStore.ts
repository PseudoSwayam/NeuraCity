import { create } from 'zustand';
import axios from 'axios';

interface User {
  id: string;
  email: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  getAuthHeaders: () => { Authorization: string } | {};
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: localStorage.getItem('neura-token') || null,
  user: localStorage.getItem('neura-user') ? JSON.parse(localStorage.getItem('neura-user')!) : null,
  isAuthenticated: !!localStorage.getItem('neura-token'),

  login: async (email: string, password: string) => {
    try {
      console.log('Attempting login to:', 'http://localhost:8005/auth/token');
      
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      console.log('Sending login request with:', { username: email, password: '***' });

      const response = await axios.post(
        'http://localhost:8005/auth/token',
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          timeout: 10000, // 10 second timeout
        }
      );

      console.log('Login response:', response.status, response.data);

      if (response.status === 200 && response.data.access_token) {
        const { access_token } = response.data;
        const user = { id: '1', email };
        
        localStorage.setItem('neura-token', access_token);
        localStorage.setItem('neura-user', JSON.stringify(user));
        
        set({
          token: access_token,
          user,
          isAuthenticated: true,
        });
        
        console.log('Login successful, token stored');
        return { success: true };
      }

      console.log('Login failed - no access_token in response');
      return { success: false, error: 'Login failed - Invalid response' };
    } catch (error) {
      console.error('Login error:', error);
      
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
          return { success: false, error: 'Invalid credentials' };
        }
        if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
          return { 
            success: false, 
            error: 'CORS Error: Cannot connect to localhost:8005 from HTTPS. Please add CORS headers to your API or run locally.' 
          };
        }
        return { success: false, error: `Server error: ${error.response?.status || 'Unknown'}` };
      }
      
      return { success: false, error: 'Connection error' };
    }
  },

  logout: () => {
    localStorage.removeItem('neura-token');
    localStorage.removeItem('neura-user');
    set({
      token: null,
      user: null,
      isAuthenticated: false,
    });
  },

  getAuthHeaders: () => {
    const token = get().token;
    return token ? { Authorization: `Bearer ${token}` } : {};
  },
}));