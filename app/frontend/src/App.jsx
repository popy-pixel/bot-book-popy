import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import AccountManager from './components/AccountManager';
import TaskCreator from './components/TaskCreator';
import LiveMonitor from './components/LiveMonitor';
import SettingsPanel from './components/SettingsPanel';

function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Navbar />
      <main className="container mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/accounts" element={<AccountManager />} />
          <Route path="/tasks" element={<TaskCreator />} />
          <Route path="/monitor" element={<LiveMonitor />} />
          <Route path="/settings" element={<SettingsPanel />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;