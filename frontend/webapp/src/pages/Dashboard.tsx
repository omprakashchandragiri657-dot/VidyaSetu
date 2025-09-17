import React, { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import StudentAchievements from '../components/StudentAchievements';
import StudentPortal from './StudentPortal';
import PrincipalDashboard from '../components/PrincipalDashboard';
import HODDashboard from '../components/HODDashboard';
import FacultyDashboard from '../components/FacultyDashboard';
import Navbar from '../components/Navbar';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user?.role === 'principal') {
      navigate('/principal/dashboard');
    }
  }, [user, navigate]);

  if (!user) return <div className="loading">Loading...</div>;

  // If user is a principal, this will be a brief flash before redirecting.
  // Or we can show a loading spinner until redirection is complete.
  if (user.role === 'principal') {
    return <div className="loading">Redirecting to Principal Dashboard...</div>;
  }

  return (
    <div className="dashboard-container">
      <Navbar />
      <div className="dashboard-content">
        <div className="dashboard-header">
          <h2>Dashboard</h2>
        </div>
        <div className="dashboard-body">
          {/* Render different components based on role */}
          {user.role === 'student' && <StudentDashboard />}
          {user.role === 'faculty' && <FacultyDashboard />}
          {user.role === 'hod' && <HODDashboard />}
          {/* Principal is handled by redirect now */}
        </div>
      </div>
    </div>
  );
};

const StudentDashboard: React.FC = () => {
  return (
    <div>
      <h3>Student Dashboard</h3>
      <p>View achievements, submit new ones, request permissions.</p>
      <StudentAchievements />
      <StudentPortal />
    </div>
  );
};







export default Dashboard;
