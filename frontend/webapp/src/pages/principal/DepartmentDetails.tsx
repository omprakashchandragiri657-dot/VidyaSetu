import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../../services/api';

// --- Placeholder Data and Interfaces ---

interface HOD {
  name: string;
  email: string;
  employee_id: string;
}

interface FacultyMember {
  id: number;
  name: string;
  designation: string;
}

interface StudentDistribution {
  year: string;
  count: number;
}

interface DepartmentDetailsData {
  id: number;
  name: string;
  code: string;
  hod: HOD;
  faculty: FacultyMember[];
  student_distribution: StudentDistribution[];
}

const placeholderData: DepartmentDetailsData = {
    id: 1,
    name: 'Computer Science & Engineering',
    code: 'CSE',
    hod: {
        name: 'Dr. Alan Turing',
        email: 'alan.t@vidyasetu.edu',
        employee_id: 'HOD-CSE-001'
    },
    faculty: [
        { id: 1, name: 'Prof. Ada Lovelace', designation: 'Professor' },
        { id: 2, name: 'Prof. Charles Babbage', designation: 'Associate Professor' },
        { id: 3, name: 'Dr. Grace Hopper', designation: 'Assistant Professor' },
    ],
    student_distribution: [
        { year: '1st Year', count: 300 },
        { year: '2nd Year', count: 280 },
        { year: '3rd Year', count: 250 },
        { year: '4th Year', count: 220 },
    ]
};

// --- Main Component ---

const DepartmentDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [details, setDetails] = useState<DepartmentDetailsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        // Replace with actual API call
        // const response = await api.get(`/api/departments/${id}`);
        // setDetails(response.data);
        setDetails(placeholderData);
      } catch (error) {
        console.error('Error fetching department details:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (!details) return <div>Department not found.</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-deep-blue">{details.name}</h1>
        <p className="text-slate-gray">{details.code}</p>
      </div>

      {/* HOD Info */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-bold text-deep-blue mb-4">Head of Department (HOD)</h2>
        <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-slate-gray rounded-full" />
            <div>
                <p className="font-semibold text-lg">{details.hod.name}</p>
                <p className="text-slate-gray">{details.hod.email}</p>
                <p className="text-sm text-slate-gray">ID: {details.hod.employee_id}</p>
            </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Faculty List */}
        <div className="lg:col-span-1 bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold text-deep-blue mb-4">Faculty ({details.faculty.length})</h2>
            <ul className="space-y-2">
                {details.faculty.map(f => (
                    <li key={f.id} className="border-b pb-2">
                        <p className="font-semibold">{f.name}</p>
                        <p className="text-sm text-slate-gray">{f.designation}</p>
                    </li>
                ))}
            </ul>
        </div>

        {/* Student Distribution Chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-deep-blue mb-4">Student Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={details.student_distribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#1E3A8A" name="Number of Students" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default DepartmentDetails;
