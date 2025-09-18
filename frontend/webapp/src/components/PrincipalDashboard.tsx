import React, { useState, useEffect } from 'react';
import api from '../services/api';
import '../styles/buttons.css';
import './PrincipalDashboard.css';

interface StudentFormData {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  password: string;
  student_id: string;
  year_of_admission: number;
  course: string;
  branch: string;
  department_id: number;
  phone_number: string;
  date_of_birth: string;
}

interface College {
  id: number;
  name: string;
  code: string;
  address: string;
  contact_email: string;
  contact_phone: string;
  principal: number;
}

interface Event {
  id: number;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  status: string;
  hod?: {
    user: {
      first_name: string;
      last_name: string;
    };
  };
}

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
}

const PrincipalDashboard: React.FC = () => {
  const [college, setCollege] = useState<College | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [hods, setHods] = useState<User[]>([]);
  const [faculty, setFaculty] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showStudentForm, setShowStudentForm] = useState(false);
  const [studentForm, setStudentForm] = useState<StudentFormData>({
    email: '',
    username: '',
    first_name: '',
    last_name: '',
    password: '',
    student_id: '',
    year_of_admission: new Date().getFullYear(),
    course: '',
    branch: '',
    department_id: 0,
    phone_number: '',
    date_of_birth: '',
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [collegeRes, eventsRes, hodsRes, facultyRes] = await Promise.all([
        api.get('colleges/'),
        api.get('principal/events/'),
        api.get('hods/'),
        api.get('faculty/'),
      ]);
      setCollege(collegeRes.data[0]); // Assuming one college
      setEvents(eventsRes.data);
      setHods(hodsRes.data);
      setFaculty(facultyRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStudentFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setStudentForm(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCreateStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const userData = {
        email: studentForm.email,
        username: studentForm.username,
        first_name: studentForm.first_name,
        last_name: studentForm.last_name,
        password: studentForm.password,
        college_id: college?.id,
        department_id: studentForm.department_id,
        role: 'student',
      };
      const userResponse = await api.post('register/', userData);
      const studentData = {
        student_id: studentForm.student_id,
        year_of_admission: studentForm.year_of_admission,
        course: studentForm.course,
        branch: studentForm.branch,
        department_id: studentForm.department_id,
        phone_number: studentForm.phone_number,
        date_of_birth: studentForm.date_of_birth,
      };
      await api.post('student-profile/', studentData);
      alert('Student created successfully');
      setShowStudentForm(false);
      setStudentForm({
        email: '',
        username: '',
        first_name: '',
        last_name: '',
        password: '',
        student_id: '',
        year_of_admission: new Date().getFullYear(),
        course: '',
        branch: '',
        department_id: 0,
        phone_number: '',
        date_of_birth: '',
      });
    } catch (error) {
      console.error('Error creating student:', error);
      alert('Failed to create student');
    }
  };

  const approveEvent = async (eventId: number) => {
    try {
      await api.post(`principal/events/${eventId}/approve/`, { status: 'approved' });
      fetchDashboardData();
    } catch (error) {
      console.error('Error approving event:', error);
      alert('Failed to approve event');
    }
  };

  const rejectEvent = async (eventId: number) => {
    try {
      await api.post(`principal/events/${eventId}/approve/`, { status: 'rejected' });
      fetchDashboardData();
    } catch (error) {
      console.error('Error rejecting event:', error);
      alert('Failed to reject event');
    }
  };

  const pendingEvents = events.filter(event => event.status === 'pending');

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="principal-dashboard">
      <div className="dashboard-header">
        <h2>Principal Dashboard</h2>
        <p>Manage college information, events, and staff</p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>College Information</h3>
          {college && (
            <div className="college-info">
              <div className="info-item">
                <strong>Name:</strong> {college.name}
              </div>
              <div className="info-item">
                <strong>Code:</strong> {college.code}
              </div>
              <div className="info-item">
                <strong>Address:</strong> {college.address}
              </div>
              <div className="info-item">
                <strong>Email:</strong> {college.contact_email}
              </div>
              <div className="info-item">
                <strong>Phone:</strong> {college.contact_phone}
              </div>
            </div>
          )}
        </div>

        <div className="dashboard-card">
          <h3>Events</h3>
          <div className="list-container">
            {events.length > 0 ? (
              <ul className="item-list">
                {events.map(event => (
                  <li key={event.id} className="list-item">
                    <div className="item-content">
                      <span className="item-title">{event.name}</span>
                      <span className={`status-badge ${event.status.toLowerCase()}`}>
                        {event.status}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="no-data">No events found</p>
            )}
          </div>
        </div>

        <div className="dashboard-card">
          <h3>HODs</h3>
          <div className="list-container">
            {hods.length > 0 ? (
              <ul className="item-list">
                {hods.map(hod => (
                  <li key={hod.id} className="list-item">
                    <div className="item-content">
                      <span className="item-title">{hod.first_name} {hod.last_name}</span>
                      <span className="item-subtitle">{hod.email}</span>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="no-data">No HODs found</p>
            )}
          </div>
        </div>

        <div className="dashboard-card">
          <h3>Faculty</h3>
          <div className="list-container">
            {faculty.length > 0 ? (
              <ul className="item-list">
                {faculty.map(f => (
                  <li key={f.id} className="list-item">
                    <div className="item-content">
                      <span className="item-title">{f.first_name} {f.last_name}</span>
                      <span className="item-subtitle">{f.email}</span>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="no-data">No faculty found</p>
            )}
          </div>
        </div>
      </div>

      {pendingEvents.length > 0 && (
        <section className="dashboard-section">
          <h3>Pending Event Approvals</h3>
          <div className="list-container">
            <ul className="item-list">
              {pendingEvents.map(event => (
                <li key={event.id} className="list-item">
                  <div className="item-content">
                    <div className="item-info">
                      <span className="item-title">{event.name}</span>
                      <span className="item-subtitle">
                        {event.hod?.user?.first_name} {event.hod?.user?.last_name} - {new Date(event.start_date).toLocaleDateString()} to {new Date(event.end_date).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="action-buttons">
                      <button className="btn-success" onClick={() => approveEvent(event.id)}>Approve</button>
                      <button className="btn-secondary" onClick={() => rejectEvent(event.id)}>Reject</button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      <div className="dashboard-actions">
        <button
          className="btn-cta"
          onClick={() => setShowStudentForm(!showStudentForm)}
        >
          {showStudentForm ? 'Hide Form' : 'Add New Student'}
        </button>
      </div>

      {showStudentForm && (
        <div className="form-card">
          <h3>Create New Student</h3>
          <form onSubmit={handleCreateStudent} className="student-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={studentForm.email}
                  onChange={handleStudentFormChange}
                  required
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={studentForm.username}
                  onChange={handleStudentFormChange}
                  required
                  className="form-control"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="first_name">First Name</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={studentForm.first_name}
                  onChange={handleStudentFormChange}
                  required
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label htmlFor="last_name">Last Name</label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={studentForm.last_name}
                  onChange={handleStudentFormChange}
                  required
                  className="form-control"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={studentForm.password}
                  onChange={handleStudentFormChange}
                  required
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label htmlFor="student_id">Student ID</label>
                <input
                  type="text"
                  id="student_id"
                  name="student_id"
                  value={studentForm.student_id}
                  onChange={handleStudentFormChange}
                  required
                  className="form-control"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="year_of_admission">Year of Admission</label>
                <input
                  type="number"
                  id="year_of_admission"
                  name="year_of_admission"
                  value={studentForm.year_of_admission}
                  onChange={handleStudentFormChange}
                  required
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label htmlFor="course">Course</label>
                <input
                  type="text"
                  id="course"
                  name="course"
                  value={studentForm.course}
                  onChange={handleStudentFormChange}
                  required
                  className="form-control"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="branch">Branch</label>
                <input
                  type="text"
                  id="branch"
                  name="branch"
                  value={studentForm.branch}
                  onChange={handleStudentFormChange}
                  required
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label htmlFor="department_id">Department ID</label>
                <input
                  type="number"
                  id="department_id"
                  name="department_id"
                  value={studentForm.department_id}
                  onChange={handleStudentFormChange}
                  required
                  className="form-control"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="phone_number">Phone Number</label>
                <input
                  type="text"
                  id="phone_number"
                  name="phone_number"
                  value={studentForm.phone_number}
                  onChange={handleStudentFormChange}
                  required
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label htmlFor="date_of_birth">Date of Birth</label>
                <input
                  type="date"
                  id="date_of_birth"
                  name="date_of_birth"
                  value={studentForm.date_of_birth}
                  onChange={handleStudentFormChange}
                  required
                  className="form-control"
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-success">Create Student</button>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setShowStudentForm(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default PrincipalDashboard;
