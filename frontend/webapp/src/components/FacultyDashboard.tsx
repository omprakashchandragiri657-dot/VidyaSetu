import React, { useState, useEffect } from 'react';
import api from '../services/api';
import '../styles/buttons.css';
import './FacultyDashboard.css';

interface Achievement {
  id: number;
  title: string;
  description: string;
  status: string;
  student: {
    user: {
      first_name: string;
      last_name: string;
    };
  };
}

interface PermissionRequest {
  id: number;
  title: string;
  description: string;
  status: string;
  student: {
    user: {
      first_name: string;
      last_name: string;
    };
  };
}

const FacultyDashboard: React.FC = () => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [permissions, setPermissions] = useState<PermissionRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [achievementsRes, permissionsRes] = await Promise.all([
        api.get('achievements/pending/'),
        api.get('permission-requests/pending/'),
      ]);
      setAchievements(achievementsRes.data);
      setPermissions(permissionsRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const approveAchievement = async (id: number) => {
    try {
      await api.post(`achievements/${id}/approve/`, { status: 'approved' });
      fetchDashboardData();
    } catch (error) {
      console.error('Error approving achievement:', error);
    }
  };

  const rejectAchievement = async (id: number) => {
    try {
      await api.post(`achievements/${id}/approve/`, { status: 'rejected' });
      fetchDashboardData();
    } catch (error) {
      console.error('Error rejecting achievement:', error);
    }
  };

  const approvePermission = async (id: number) => {
    try {
      await api.post(`permission-requests/${id}/approve/`, { status: 'approved' });
      fetchDashboardData();
    } catch (error) {
      console.error('Error approving permission:', error);
    }
  };

  const rejectPermission = async (id: number) => {
    try {
      await api.post(`permission-requests/${id}/approve/`, { status: 'rejected' });
      fetchDashboardData();
    } catch (error) {
      console.error('Error rejecting permission:', error);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="faculty-dashboard">
      <div className="dashboard-header">
        <h2>Faculty Dashboard</h2>
        <p>Review and approve student achievements and permission requests</p>
      </div>

      <section className="dashboard-section">
        <h3>Pending Achievements</h3>
        {achievements.length > 0 ? (
          <ul className="item-list">
            {achievements.map(achievement => (
              <li key={achievement.id} className="list-item">
                <div className="item-content">
                  <div className="item-info">
                    <span className="item-title">{achievement.title}</span>
                    <span className="item-subtitle">
                      {achievement.student?.user?.first_name} {achievement.student?.user?.last_name}
                    </span>
                  </div>
                  <div className="action-buttons">
                    <button className="btn-success" onClick={() => approveAchievement(achievement.id)}>Approve</button>
                    <button className="btn-secondary" onClick={() => rejectAchievement(achievement.id)}>Reject</button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="no-data">No pending achievements to review</p>
        )}
      </section>

      <section className="dashboard-section">
        <h3>Pending Permission Requests</h3>
        {permissions.length > 0 ? (
          <ul className="item-list">
            {permissions.map(permission => (
              <li key={permission.id} className="list-item">
                <div className="item-content">
                  <div className="item-info">
                    <span className="item-title">{permission.title}</span>
                    <span className="item-subtitle">
                      {permission.student?.user?.first_name} {permission.student?.user?.last_name}
                    </span>
                  </div>
                  <div className="action-buttons">
                    <button className="btn-success" onClick={() => approvePermission(permission.id)}>Approve</button>
                    <button className="btn-secondary" onClick={() => rejectPermission(permission.id)}>Reject</button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="no-data">No pending permission requests to review</p>
        )}
      </section>
    </div>
  );
};

export default FacultyDashboard;
