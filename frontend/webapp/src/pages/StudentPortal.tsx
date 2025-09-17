import React, { useState, useEffect } from 'react';
import api from '../services/api';

interface Event {
  id: number;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
}

interface AchievementFormData {
  title: string;
  description: string;
  category: string;
  date_achieved: string;
  evidence_file: File | null;
  event_id: number | null;
}

const StudentPortal: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [formData, setFormData] = useState<AchievementFormData>({
    title: '',
    description: '',
    category: 'academic',
    date_achieved: '',
    evidence_file: null,
    event_id: null,
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      const response = await api.get('principal/events/');
      setEvents(response.data);
    } catch (error) {
      console.error('Error fetching events:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFormData(prev => ({
        ...prev,
        evidence_file: e.target.files![0],
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.event_id) {
      setMessage('Please select an event.');
      return;
    }
    setLoading(true);
    setMessage('');
    try {
      const data = new FormData();
      data.append('title', formData.title);
      data.append('description', formData.description);
      data.append('category', formData.category);
      data.append('date_achieved', formData.date_achieved);
      if (formData.evidence_file) {
        data.append('evidence_file', formData.evidence_file);
      }
      data.append('event_id', formData.event_id.toString());

      await api.post('achievements/', data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setMessage('Achievement submitted successfully.');
      setFormData({
        title: '',
        description: '',
        category: 'academic',
        date_achieved: '',
        evidence_file: null,
        event_id: null,
      });
    } catch (error) {
      console.error('Error submitting achievement:', error);
      setMessage('Failed to submit achievement.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Student Portal - Submit Achievement</h2>
      {message && <p>{message}</p>}
      <form onSubmit={handleSubmit}>
        <label>
          Event:
          <select name="event_id" value={formData.event_id ?? ''} onChange={handleChange} required>
            <option value="" disabled>Select an event</option>
            {events.map(event => (
              <option key={event.id} value={event.id}>
                {event.name} ({new Date(event.start_date).toLocaleDateString()} - {new Date(event.end_date).toLocaleDateString()})
              </option>
            ))}
          </select>
        </label>
        <br />
        <label>
          Title:
          <input type="text" name="title" value={formData.title} onChange={handleChange} required />
        </label>
        <br />
        <label>
          Description:
          <textarea name="description" value={formData.description} onChange={handleChange} required />
        </label>
        <br />
        <label>
          Category:
          <select name="category" value={formData.category} onChange={handleChange} required>
            <option value="academic">Academic</option>
            <option value="sports">Sports</option>
            <option value="cultural">Cultural</option>
            <option value="other">Other</option>
          </select>
        </label>
        <br />
        <label>
          Date Achieved:
          <input type="date" name="date_achieved" value={formData.date_achieved} onChange={handleChange} required />
        </label>
        <br />
        <label>
          Evidence File:
          <input type="file" name="evidence_file" onChange={handleFileChange} accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" />
        </label>
        <br />
        <button type="submit" disabled={loading}>{loading ? 'Submitting...' : 'Submit Achievement'}</button>
      </form>
    </div>
  );
};

export default StudentPortal;
