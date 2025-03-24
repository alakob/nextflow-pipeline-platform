import React, { createContext, useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
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
      const decoded = jwtDecode(token);
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
      console.log('AuthContext: Starting login process');
      const response = await authApi.login(username, password);
      
      if (response && response.access_token) {
        console.log('AuthContext: Received valid token');
        localStorage.setItem('token', response.access_token);
        
        try {
          const userData = await authApi.getCurrentUser();
          console.log('AuthContext: Retrieved user data', userData);
          setCurrentUser(userData);
          return true;
        } catch (userError) {
          console.error('AuthContext: Failed to get user data after login', userError);
          // If we got a token but couldn't get user data, still consider it a success
          // The user data will be fetched again on the next page load
          return true;
        }
      }
      console.error('AuthContext: Login response missing token', response);
      return false;
    } catch (error) {
      console.error('AuthContext: Login error:', error);
      throw error;
    }
  };

  // Logout function
  const logout = () => {
    console.log('AuthContext: Logging out user');
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
