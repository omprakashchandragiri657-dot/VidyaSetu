import React, { useState, useEffect } from 'react';
import api from '../services/api';

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

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h3>Principal Dashboard</h3>
      <div>
        <h4>College Information</h4>
        {college && (
          <div>
            <p>Name: {college.name}</p>
            <p>Code: {college.code}</p>
            <p>Address: {college.address}</p>
            <p>Email: {college.contact_email}</p>
            <p>Phone: {college.contact_phone}</p>
          </div>
        )}
      </div>
      <div>
        <h4>Events</h4>
        <ul>
          {events.map(event => (
            <li key={event.id}>
              {event.name} - {event.status}
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h4>HODs</h4>
        <ul>
          {hods.map(hod => (
            <li key={hod.id}>
              {hod.first_name} {hod.last_name} - {hod.email}
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h4>Faculty</h4>
        <ul>
          {faculty.map(f => (
            <li key={f.id}>
              {f.first_name} {f.last_name} - {f.email}
            </li>
          ))}
        </ul>
      </div>
      <div>
        <button onClick={() => setShowStudentForm(!showStudentForm)}>
          {showStudentForm ? 'Hide' : 'Add New Student'}
        </button>
        {showStudentForm && (
          <form onSubmit={handleCreateStudent}>
            <h4>Create New Student</h4>
            <label>
              Email:
              <input type="email" name="email" value={studentForm.email} onChange={handleStudentFormChange} required />
            </label>
            <br />
            <label>
              Username:
              <input type="text" name="username" value={studentForm.username} onChange={handleStudentFormChange} required />
            </label>
            <br />
            <label>
              First Name:
              <input type="text" name="first_name" value={studentForm.first_name} onChange={handleStudentFormChange} required />
            </label>
            <br />
            <label>
              Last Name:
              <input type="text" name="last_name" value={studentForm.last_name} onChange={handleStudentFormChange} required />
            </label>
            <br />
            <label>
              Password:
              <input type="password" name="password" value={studentForm.password} onChange={handleStudentFormChange} required />
            </label>
            <br />
            <label>
              Student ID:
              <input type="text" name="student_id" value={studentForm.student_id} onChange={handleStudentFormChange} required />
            </label>
            <br />
            <label>
              Year of Admission:
              <input type="number" name="year_of_admission" value={studentForm.year_of_admission} onChange={handleStudentFormChange} required />
            </label>
            <br />
            <label>
              Course:
              <input type="text" name="course" value={studentForm.course} onChange={handleStudentFormChange} required />
            </label>
            <br />
            <label>
              Branch:
              <input type="text" name="branch" value={studentForm.branch} onChange={handleStudentFormChange} required />
            </label>
            <br />
            <label>
              Department ID:
              <input type="number" name="department_id" value={studentForm.department_id} onChange={handleStudentFormChange} required />
            </label>
            <br />
            <label>
              Phone Number:
              <input type="text" name="phone_number" value={studentForm.phone_number} onChange={handleStudentFormChange} required />
            </label>
            <br />
            <label>
              Date of Birth:
              <input type="date" name="date_of_birth" value={studentForm.date_of_birth} onChange={handleStudentFormChange} required />
            </label>
            <br />
            <button type="submit">Create Student</button>
          </form>
        )}
      </div>
    </div>
  );
};

export default PrincipalDashboard;
