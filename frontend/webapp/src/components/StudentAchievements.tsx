import React, { useState, useEffect } from 'react';
import api from '../services/api';

interface Achievement {
  id: number;
  title: string;
  description: string;
  category: string;
  date_achieved: string;
  status: string;
  evidence_file: string;
}

const StudentAchievements: React.FC = () => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAchievements();
  }, []);

  const fetchAchievements = async () => {
    try {
      const response = await api.get('achievements/');
      setAchievements(response.data);
    } catch (error) {
      console.error('Error fetching achievements:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h3>My Achievements</h3>
      <ul>
        {achievements.map((achievement) => (
          <li key={achievement.id}>
            <h4>{achievement.title}</h4>
            <p>{achievement.description}</p>
            <p>Status: {achievement.status}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default StudentAchievements;
