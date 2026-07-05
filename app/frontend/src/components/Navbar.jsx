import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Users, Send, Monitor, Settings, Shield } from 'lucide-react';

const navItems = [
  { path: '/', icon: Home, label: 'Dashboard' },
  { path: '/accounts', icon: Users, label: 'Accounts' },
  { path: '/tasks', icon: Send, label: 'Tasks' },
  { path: '/monitor', icon: Monitor, label: 'Monitor' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export default function Navbar() {
  const location = useLocation();

  return (
    <nav className="bg-gray-800 border-b border-gray-700">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2 text-xl font-bold">
            <Shield className="w-6 h-6 text-blue-400" />
            <span>BOT-BOOK-POPY</span>
          </Link>
          
          <div className="flex items-center gap-1">
            {navItems.map(({ path, icon: Icon, label }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                  location.pathname === path
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{label}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}