import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar: React.FC = () => {
  return (
    <div className="w-64 h-screen bg-deep-blue text-white flex flex-col">
      <div className="p-4 border-b border-blue-800">
        <h1 className="text-2xl font-bold">VidyaSetu</h1>
        <p className="text-sm text-blue-300">Principal Dashboard – Empowering Institutional Management</p>
      </div>
      <nav className="flex-grow">
        <ul>
          <li>
            <NavLink to="/principal/dashboard" className={({ isActive }) =>
              `block p-4 hover:bg-blue-700 ${isActive ? 'bg-blue-600' : ''}`
            }>
              Dashboard
            </NavLink>
          </li>
          <li>
            <NavLink to="/principal/departments" className={({ isActive }) =>
              `block p-4 hover:bg-blue-700 ${isActive ? 'bg-blue-600' : ''}`
            }>
              Departments
            </NavLink>
          </li>
          <li>
            <NavLink to="/principal/events" className={({ isActive }) =>
              `block p-4 hover:bg-blue-700 ${isActive ? 'bg-blue-600' : ''}`
            }>
              Events
            </NavLink>
          </li>
          <li>
            <NavLink to="/principal/faculty" className={({ isActive }) =>
              `block p-4 hover:bg-blue-700 ${isActive ? 'bg-blue-600' : ''}`
            }>
              Faculty
            </NavLink>
          </li>
          <li>
            <NavLink to="/principal/students" className={({ isActive }) =>
              `block p-4 hover:bg-blue-700 ${isActive ? 'bg-blue-600' : ''}`
            }>
              Students
            </NavLink>
          </li>
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;
