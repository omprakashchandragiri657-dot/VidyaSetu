import React from 'react';
import { useAuth } from '../context/AuthContext';
import StudentAchievements from '../components/StudentAchievements';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();

  if (!user) return <div>Loading...</div>;

  return (
    <div>
      <h2>Dashboard</h2>
      <p>Welcome, {user.first_name} {user.last_name}</p>
      <p>Role: {user.role}</p>
      <button onClick={logout}>Logout</button>
      {/* Render different components based on role */}
      {user.role === 'student' && <StudentDashboard />}
      {user.role === 'faculty' && <FacultyDashboard />}
      {user.role === 'hod' && <HODDashboard />}
      {user.role === 'principal' && <PrincipalDashboard />}
    </div>
  );
};

const StudentDashboard: React.FC = () => {
  return (
    <div>
      <h3>Student Dashboard</h3>
      <p>View achievements, submit new ones, request permissions.</p>
      <StudentAchievements />
    </div>
  );
};

const FacultyDashboard: React.FC = () => {
  return (
    <div>
      <h3>Faculty Dashboard</h3>
      <p>Approve achievements and permissions.</p>
    </div>
  );
};

const HODDashboard: React.FC = () => {
  return (
    <div>
      <h3>HOD Dashboard</h3>
      <p>Manage faculty, approve requests.</p>
    </div>
  );
};

const PrincipalDashboard: React.FC = () => {
  return (
    <div>
      <h3>Principal Dashboard</h3>
      <p>Manage college, events, etc.</p>
    </div>
  );
};

export default Dashboard;
