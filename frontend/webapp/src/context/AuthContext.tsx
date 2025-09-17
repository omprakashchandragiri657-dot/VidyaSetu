import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '../services/api';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  college: number;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Fetch user details
      api.get('me/').then((response) => {
        setUser(response.data);
        setIsAuthenticated(true);
      }).catch((error) => {
        console.error('Authentication error:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setIsAuthenticated(false);
      });
    }
  }, []);

  const login = async (username: string, password: string) => {
    // Determine if user is admin or normal user by a simple heuristic or separate login function
    // For simplicity, try user-login first, then admin-login if needed

    try {
      // Try user login
      const response = await api.post('user-login/', { username, password });
      // On success, store tokens
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      // Fetch user details
      const userResponse = await api.get('me/');
      setUser(userResponse.data);
      setIsAuthenticated(true);
    } catch (userLoginError) {
      try {
        // Try admin login
        const response = await api.post('admin-login/', { username, password });
        // On success, store tokens
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
        // Fetch user details
        const userResponse = await api.get('me/');
        setUser(userResponse.data);
        setIsAuthenticated(true);
      } catch (adminLoginError) {
        throw new Error('Invalid credentials');
      }
    }
  };

  const register = async (userData: any) => {
    await api.post('register/', userData);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};
