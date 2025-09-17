import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Login.css';
import academicIllustration from '../assets/academic-illustration.svg';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="illustration-container">
          <img src={academicIllustration} alt="Academic Illustration" className="academic-illustration" />
        </div>
        
        <div className="login-form-container">
          <div className="login-card">
            <div className="login-header">
              <h1>VidyaSethu</h1>
              <p>Bridging Students, Faculty & Institutions</p>
            </div>
            
            <form onSubmit={handleSubmit} className="login-form">
              <div className="form-group">
                <label htmlFor="username">Email / Username</label>
                <input
                  type="text"
                  id="username"
                  className="form-control"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                  type="password"
                  id="password"
                  className="form-control"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                />
              </div>
              
              <div className="forgot-password">
                <a href="#">Forgot Password?</a>
              </div>
              
              {error && <div className="error-message">{error}</div>}
              
              <button type="submit" className="login-button">
                Login
              </button>
            </form>
          </div>
          
          <div className="login-footer">
            <p>© 2025 VidyaSethu. All rights reserved.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
