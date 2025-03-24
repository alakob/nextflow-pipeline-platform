import React, { createContext, useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import jwt_decode from 'jwt-decode';
import { authApi } from '../../services/api';

// Create the context
const AuthContext = createContext(null);

// Hook to use the auth context
export const useAuth = () => useContext(AuthContext);

// Provider component
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Check if token is valid or expired
  const isTokenValid = () => {
    const token = localStorage.getItem('token');
    if (!token) return false;

    try {
      const decoded = jwt_decode(token);
      const currentTime = Date.now() / 1000;
      
      // Check if token is not expired
      return decoded.exp > currentTime;
    } catch (error) {
      console.error('Error decoding token:', error);
      return false;
    }
  };

  // Load user data when component mounts
  useEffect(() => {
    const loadUserData = async () => {
      if (!isTokenValid()) {
        localStorage.removeItem('token');
        setCurrentUser(null);
        setLoading(false);
        return;
      }

      try {
        const userData = await authApi.getCurrentUser();
        setCurrentUser(userData);
      } catch (error) {
        console.error('Failed to load user data:', error);
        localStorage.removeItem('token');
        setCurrentUser(null);
      } finally {
        setLoading(false);
      }
    };

    loadUserData();
  }, []);

  // Login function
  const login = async (username, password) => {
    try {
      const response = await authApi.login(username, password);
      if (response && response.access_token) {
        const userData = await authApi.getCurrentUser();
        setCurrentUser(userData);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  // Logout function
  const logout = () => {
    authApi.logout();
    setCurrentUser(null);
    navigate('/login');
  };

  // Register function
  const register = async (username, password) => {
    try {
      return await authApi.register(username, password);
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  // Context value
  const value = {
    currentUser,
    isAuthenticated: !!currentUser,
    loading,
    login,
    logout,
    register,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
