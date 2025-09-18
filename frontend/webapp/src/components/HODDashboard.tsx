import React, { useState, useEffect } from 'react';
import api from '../services/api';
import '../styles/buttons.css';
import './HODDashboard.css';

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

interface Event {
  id: number;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  status: string;
  created_at: string;
}

interface EventFormData {
  name: string;
  description: string;
  start_date: string;
  end_date: string;
}

const HODDashboard: React.FC = () => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [permissions, setPermissions] = useState<PermissionRequest[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [showEventForm, setShowEventForm] = useState(false);
  const [eventFormData, setEventFormData] = useState<EventFormData>({
    name: '',
    description: '',
    start_date: '',
    end_date: '',
  });
  const [eventLoading, setEventLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [achievementsRes, permissionsRes, eventsRes] = await Promise.all([
        api.get('achievements/pending/'),
        api.get('permission-requests/pending/'),
        api.get('hod/events/'),
      ]);
      setAchievements(achievementsRes.data);
      setPermissions(permissionsRes.data);
      setEvents(eventsRes.data);
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

  const handleEventFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setEventFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEventSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setEventLoading(true);
    setMessage('');
    try {
      await api.post('hod/events/', eventFormData);
      setMessage('Event submitted for approval successfully.');
      setEventFormData({
        name: '',
        description: '',
        start_date: '',
        end_date: '',
      });
      setShowEventForm(false);
      fetchDashboardData();
    } catch (error) {
      console.error('Error submitting event:', error);
      setMessage('Failed to submit event.');
    } finally {
      setEventLoading(false);
    }
  };

  const sendReminder = async (eventId: number) => {
    try {
      await api.post(`hod/events/${eventId}/remind/`);
      setMessage('Reminder sent successfully.');
      fetchDashboardData();
    } catch (error) {
      console.error('Error sending reminder:', error);
      setMessage('Failed to send reminder.');
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="hod-dashboard">
      <div className="dashboard-header">
        <h2>HOD Dashboard</h2>
        <p>Review and approve student achievements and permission requests</p>
      </div>

      <section className="dashboard-section">
        <div className="section-header">
          <h3>Event Management</h3>
          <button
            className="btn-cta"
            onClick={() => setShowEventForm(!showEventForm)}
          >
            {showEventForm ? 'Cancel' : 'Create Event'}
          </button>
        </div>

        {message && <p className="message">{message}</p>}

        {showEventForm && (
          <form onSubmit={handleEventSubmit} className="event-form">
            <div className="form-group">
              <label htmlFor="name">Event Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={eventFormData.name}
                onChange={handleEventFormChange}
                required
                className="form-control"
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                name="description"
                value={eventFormData.description}
                onChange={handleEventFormChange}
                required
                className="form-control"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="start_date">Start Date</label>
                <input
                  type="date"
                  id="start_date"
                  name="start_date"
                  value={eventFormData.start_date}
                  onChange={handleEventFormChange}
                  required
                  className="form-control"
                />
              </div>

              <div className="form-group">
                <label htmlFor="end_date">End Date</label>
                <input
                  type="date"
                  id="end_date"
                  name="end_date"
                  value={eventFormData.end_date}
                  onChange={handleEventFormChange}
                  required
                  className="form-control"
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-cta" disabled={eventLoading}>
                {eventLoading ? 'Submitting...' : 'Submit for Approval'}
              </button>
            </div>
          </form>
        )}

        <div className="events-list">
          <h4>My Events</h4>
          {events.length > 0 ? (
            <ul className="item-list">
              {events.map(event => (
                <li key={event.id} className="list-item">
                  <div className="item-content">
                    <div className="item-info">
                      <span className="item-title">{event.name}</span>
                      <span className="item-subtitle">
                        {new Date(event.start_date).toLocaleDateString()} - {new Date(event.end_date).toLocaleDateString()}
                      </span>
                      <span className={`status-badge status-${event.status}`}>
                        {event.status}
                      </span>
                    </div>
                    <div className="action-buttons">
                      {event.status === 'pending' && (
                        <button
                          className="btn-secondary"
                          onClick={() => sendReminder(event.id)}
                        >
                          Send Reminder
                        </button>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="no-data">No events created yet</p>
          )}
        </div>
      </section>

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

export default HODDashboard;
