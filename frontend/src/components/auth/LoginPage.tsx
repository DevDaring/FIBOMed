/**
 * Login Page Component with Test Credentials Display
 */
import { useState } from 'react';
import { TEST_CREDENTIALS, type User, type TestCredential } from '../../types/user.types';
import { userApi } from '../../api/user.api';
import './LoginPage.css';

interface LoginPageProps {
  onLogin: (user: User) => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const user = await userApi.login({ email, password });
      onLogin(user);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (credential: TestCredential) => {
    setEmail(credential.email);
    setPassword(credential.password);
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'doctor': return '#4CAF50';
      case 'patient': return '#2196F3';
      case 'technician': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  const getRoleImage = (role: string) => {
    switch (role) {
      case 'doctor': return '/assets/role-doctor.png';
      case 'patient': return '/assets/role-patient.png';
      case 'technician': return '/assets/role-technician.png';
      default: return '/assets/role-patient.png';
    }
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <img src="/assets/bg-medical.png" alt="" className="bg-image" onError={(e) => { e.currentTarget.style.display = 'none'; }} />
      </div>
      
      <div className="login-card">
        <div className="login-header">
          <img src="/assets/logo.png" alt="FIBOMed" className="login-logo" />
          <h1>FIBOMed</h1>
          <p>Medical Visual Storytelling Platform</p>
          <span className="powered-by">Powered by BRIA FIBO</span>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="test-credentials">
          <h3>Test Credentials (Demo)</h3>
          <p className="hint">Click any card to auto-fill credentials</p>
          
          <div className="credentials-grid">
            {TEST_CREDENTIALS.map((cred) => (
              <div
                key={cred.email}
                className="credential-card"
                onClick={() => handleQuickLogin(cred)}
                style={{ borderColor: getRoleColor(cred.role) }}
              >
                <div className="credential-icon">
                  <img src={getRoleImage(cred.role)} alt={cred.role} onError={(e) => { e.currentTarget.parentElement!.textContent = cred.role.charAt(0).toUpperCase(); }} />
                </div>
                <div className="credential-role" style={{ color: getRoleColor(cred.role) }}>
                  {cred.role.toUpperCase()}
                </div>
                <div className="credential-name">{cred.name}</div>
                <div className="credential-desc">{cred.description}</div>
                <div className="credential-email">{cred.email}</div>
                <div className="credential-password">Password: {cred.password}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="login-features">
        <h2>Platform Features</h2>
        <div className="features-grid">
          <div className="feature-item">
            <img src="/assets/feature-visualization.svg" alt="" className="feature-icon-img" onError={(e) => { e.currentTarget.style.display = 'none'; }} />
            <h4>AI Visualization</h4>
            <p>Transform medical reports into visual explanations</p>
          </div>
          <div className="feature-item">
            <img src="/assets/feature-voice.png" alt="" className="feature-icon-img" onError={(e) => { e.currentTarget.style.display = 'none'; }} />
            <h4>Voice Enabled</h4>
            <p>Speech-to-text and text-to-speech support</p>
          </div>
          <div className="feature-item">
            <img src="/assets/feature-analysis.svg" alt="" className="feature-icon-img" onError={(e) => { e.currentTarget.style.display = 'none'; }} />
            <h4>Smart Analysis</h4>
            <p>Gemini AI powered report analysis</p>
          </div>
          <div className="feature-item">
            <img src="/assets/feature-roles.svg" alt="" className="feature-icon-img" onError={(e) => { e.currentTarget.style.display = 'none'; }} />
            <h4>Multi-Role</h4>
            <p>Doctor, Patient, and Technician portals</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
