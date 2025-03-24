import React, { useEffect } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
import { authApi } from '../../services/api';

const ProtectedRoute = () => {
  const { isAuthenticated, loading, currentUser } = useAuth();
  const location = useLocation();

  // Add debug logging for authentication state
  useEffect(() => {
    const token = localStorage.getItem('token');
    console.log('ProtectedRoute: Path', location.pathname);
    console.log('ProtectedRoute: Auth State:', { 
      isAuthenticated, 
      loading, 
      hasToken: !!token,
      currentUser: currentUser ? 'Yes' : 'No'
    });

    // Double-check token validity if we have a token but not authenticated
    if (token && !isAuthenticated && !loading) {
      console.log('ProtectedRoute: Token exists but not authenticated, checking token validity');
      // This is just for debugging, no state changes here
      authApi.getCurrentUser()
        .then(user => {
          console.log('ProtectedRoute: Token is valid, user data:', user);
        })
        .catch(err => {
          console.error('ProtectedRoute: Token validation failed:', err);
        });
    }
  }, [isAuthenticated, loading, location.pathname, currentUser]);

  // Show loading indicator while checking authentication
  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading authentication status...</p>
      </div>
    );
  }

  // Check for token directly as a fallback
  const hasToken = !!localStorage.getItem('token');
  
  // Use both context authentication state and token presence for validation
  const isUserAuthenticated = isAuthenticated || hasToken;

  console.log('ProtectedRoute: Final auth decision:', isUserAuthenticated ? 'Authenticated' : 'Not authenticated');

  // Redirect to login if not authenticated
  return isUserAuthenticated ? <Outlet /> : <Navigate to="/login" />;
};

export default ProtectedRoute;
