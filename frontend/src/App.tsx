/**
 * Main App Component - FIBOMed
 * Medical Visual Storytelling Platform
 */
import { useState, useEffect } from 'react';
import LoginPage from './components/auth/LoginPage';
import DoctorDashboard from './components/dashboard/DoctorDashboard';
import PatientDashboard from './components/dashboard/PatientDashboard';
import TechnicianDashboard from './components/dashboard/TechnicianDashboard';
import type { User } from './types/user.types';
import './App.css';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored user session
    const storedUser = localStorage.getItem('fibomed_user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem('fibomed_user');
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (loggedInUser: User) => {
    setUser(loggedInUser);
    localStorage.setItem('fibomed_user', JSON.stringify(loggedInUser));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('fibomed_user');
  };

  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p>Loading FIBOMed...</p>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  // Render role-specific dashboard
  switch (user.role) {
    case 'doctor':
      return <DoctorDashboard user={user} onLogout={handleLogout} />;
    case 'patient':
      return <PatientDashboard user={user} onLogout={handleLogout} />;
    case 'technician':
      return <TechnicianDashboard user={user} onLogout={handleLogout} />;
    default:
      // For admin or unknown roles, show doctor dashboard
      return <DoctorDashboard user={user} onLogout={handleLogout} />;
  }
}

export default App;
