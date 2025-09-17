import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

// --- Helper Components ---

const StatCard: React.FC<{ title: string; value: number | string; icon: React.ReactNode }> = ({ title, value, icon }) => (
  <div className="bg-white p-6 rounded-lg shadow-md flex items-center space-x-4">
    <div className="bg-light-gray p-3 rounded-full">
      {icon}
    </div>
    <div>
      <p className="text-slate-gray text-sm font-medium">{title}</p>
      <p className="text-3xl font-bold text-deep-blue">{value}</p>
    </div>
  </div>
);

const CreateButton: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);

    const actions = [
      { label: 'Create Event', link: '/principal/events/new' },
      { label: 'Create Department', link: '/principal/departments/new' },
      { label: 'Create HOD', link: '/principal/hods/new' },
      { label: 'Create Faculty', link: '/principal/faculty/new' },
      { label: 'Create Student', link: '/principal/students/new' },
    ];

    return (
      <div className="fixed bottom-10 right-10">
        {isOpen && (
          <div className="bg-white rounded-lg shadow-lg py-2 mb-2">
            <ul>
              {actions.map(action => (
                <li key={action.label}>
                  <Link to={action.link} className="block px-4 py-2 text-slate-gray hover:bg-light-gray">
                    {action.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="bg-saffron-orange text-white w-16 h-16 rounded-full shadow-lg flex items-center justify-center transform hover:scale-110 transition-transform"
        >
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
        </button>
      </div>
    );
};

// --- Main Dashboard Component ---

interface DashboardStats {
  total_hods: number;
  total_faculty: number;
  total_students: number;
  total_events: number;
}

interface Department {
  id: number;
  name: string;
  code: string;
}

const PrincipalDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Using placeholder data until the API is ready
        const placeholderStats: DashboardStats = {
          total_hods: 12,
          total_faculty: 75,
          total_students: 1200,
          total_events: 25,
        };
        const placeholderDepartments: Department[] = [
            { id: 1, name: 'Computer Science', code: 'CSE' },
            { id: 2, name: 'Mechanical Engineering', code: 'ME' },
            { id: 3, name: 'Electronics & Communication', code: 'ECE' },
            { id: 4, name: 'Civil Engineering', code: 'CE' },
        ]

        setStats(placeholderStats);
        setDepartments(placeholderDepartments);

        // const [statsRes, deptsRes] = await Promise.all([
        //   api.get('/api/principal/dashboard/'),
        //   api.get('/api/departments/')
        // ]);
        // setStats(statsRes.data);
        // setDepartments(deptsRes.data);

      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return <div className="text-center p-8">Loading dashboard...</div>;
  }

  return (
    <div>
      {/* Top Stats Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard title="Total HODs" value={stats?.total_hods ?? 0} icon={<svg className="w-6 h-6 text-deep-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M12 14l9-5-9-5-9 5 9 5z"></path><path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-5.998 12.078 12.078 0 01.665-6.479L12 14z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-5.998 12.078 12.078 0 01.665-6.479L12 14z"></path></svg>} />
        <StatCard title="Total Faculty" value={stats?.total_faculty ?? 0} icon={<svg className="w-6 h-6 text-deep-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>} />
        <StatCard title="Total Students" value={stats?.total_students ?? 0} icon={<svg className="w-6 h-6 text-deep-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M15 21v-4a6 6 0 00-12 0v4"></path></svg>} />
        <StatCard title="Total Events" value={stats?.total_events ?? 0} icon={<svg className="w-6 h-6 text-deep-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>} />
      </div>

      {/* Departments Section */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-bold text-deep-blue mb-4">Departments</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {departments.map(dept => (
            <Link to={`/principal/departments/${dept.id}`} key={dept.id} className="block p-4 border rounded-lg hover:shadow-lg hover:border-deep-blue transition-shadow">
              <h3 className="font-semibold text-deep-blue">{dept.name}</h3>
              <p className="text-sm text-slate-gray">{dept.code}</p>
            </Link>
          ))}
        </div>
      </div>

      <CreateButton />
    </div>
  );
};

export default PrincipalDashboard;
