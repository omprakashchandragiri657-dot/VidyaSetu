import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

interface PrincipalLayoutProps {
  children: React.ReactNode;
}

const PrincipalLayout: React.FC<PrincipalLayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen bg-soft-white">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-soft-white p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default PrincipalLayout;
