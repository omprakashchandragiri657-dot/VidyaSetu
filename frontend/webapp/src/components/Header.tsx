import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-md p-4 flex justify-between items-center">
      <div>
        {/* Can be used for breadcrumbs or page titles later */}
      </div>
      <div className="flex items-center space-x-4">
        <div>
          <p className="font-semibold">Principal Name</p>
          <p className="text-sm text-slate-gray">Principal</p>
        </div>
        <div className="w-10 h-10 bg-slate-gray rounded-full">
          {/* Placeholder for profile picture */}
        </div>
        <div>
          {/* Placeholder for notifications icon */}
          <svg className="w-6 h-6 text-slate-gray" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 00-5-5.917V5a2 2 0 10-4 0v.083A6 6 0 004 11v3.159c0 .538-.214 1.055-.595 1.436L2 17h5m8 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
        </div>
      </div>
    </header>
  );
};

export default Header;
