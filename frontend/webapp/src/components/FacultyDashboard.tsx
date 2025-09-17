import React, { useState, useEffect } from 'react';
import api from '../services/api';

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

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h3>Faculty Dashboard</h3>
      <div>
        <h4>Pending Achievements</h4>
        <ul>
          {achievements.map(achievement => (
            <li key={achievement.id}>
              {achievement.title} - {achievement.student && achievement.student.user ? 
                `${achievement.student.user.first_name || ''} ${achievement.student.user.last_name || ''}` : 
                'Unknown Student'}
              <button onClick={() => approveAchievement(achievement.id)}>Approve</button>
              <button onClick={() => rejectAchievement(achievement.id)}>Reject</button>
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h4>Pending Permission Requests</h4>
        <ul>
          {permissions.map(permission => (
            <li key={permission.id}>
              {permission.title} - {permission.student && permission.student.user ? 
                `${permission.student.user.first_name || ''} ${permission.student.user.last_name || ''}` : 
                'Unknown Student'}
              <button onClick={() => approvePermission(permission.id)}>Approve</button>
              <button onClick={() => rejectPermission(permission.id)}>Reject</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default FacultyDashboard;
