import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/variables.css';
import './Navbar.css';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h1>VidyaSethu</h1>
        <p>Education Management Portal</p>
      </div>
      <div className="navbar-user">
        <span className="user-greeting">Welcome, {user.first_name} {user.last_name}</span>
        <span className="user-role">{user.role}</span>
        <button className="logout-button" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </nav>
  );
};

export default Navbar;