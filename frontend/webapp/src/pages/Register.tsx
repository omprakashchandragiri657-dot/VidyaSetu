import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const Register: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    first_name: '',
    last_name: '',
    password: '',
    password_confirm: '',
    college_id: '',
    department_id: '',
    role: 'student',
  });
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register(formData);
      navigate('/login');
    } catch (err) {
      setError('Registration failed');
    }
  };

  return (
    <div>
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <input name="email" type="email" placeholder="Email" onChange={handleChange} required />
        <input name="username" type="text" placeholder="Username" onChange={handleChange} required />
        <input name="first_name" type="text" placeholder="First Name" onChange={handleChange} required />
        <input name="last_name" type="text" placeholder="Last Name" onChange={handleChange} required />
        <input name="password" type="password" placeholder="Password" onChange={handleChange} required />
        <input name="password_confirm" type="password" placeholder="Confirm Password" onChange={handleChange} required />
        <input name="college_id" type="number" placeholder="College ID" onChange={handleChange} required />
        <input name="department_id" type="number" placeholder="Department ID" onChange={handleChange} />
        <select name="role" onChange={handleChange}>
          <option value="student">Student</option>
          <option value="faculty">Faculty</option>
          <option value="hod">HOD</option>
          <option value="principal">Principal</option>
        </select>
        <button type="submit">Register</button>
      </form>
      {error && <p>{error}</p>}
    </div>
  );
};

export default Register;
