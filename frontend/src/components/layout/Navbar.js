import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import './Layout.css';

const Navbar = () => {
  const { currentUser, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          Nextflow Pipeline Platform
        </Link>

        <div className="navbar-menu">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="navbar-link">
                Dashboard
              </Link>
              <Link to="/jobs/new" className="navbar-link">
                New Job
              </Link>
              <div className="navbar-user">
                <span className="username">
                  {currentUser?.username}
                </span>
                <button 
                  onClick={handleLogout} 
                  className="logout-button"
                >
                  Logout
                </button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="navbar-link">
                Login
              </Link>
              <Link to="/register" className="navbar-link">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
