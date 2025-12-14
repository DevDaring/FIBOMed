/**
 * Doctor Dashboard Component
 */
import { useState, useEffect } from 'react';
import type { User, DashboardData, Report } from '../../types/user.types';
import { userApi } from '../../api/user.api';
import ChatInterface from '../chat/ChatInterface';
import './Dashboard.css';

// Use relative URL in production (same origin), localhost in development
const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
const API_BASE = isProduction ? '/api/v1' : 'http://localhost:8000/api/v1';

// Patient details interface for modal
interface PatientDetails {
  user_id: string;
  full_name: string;
  conditions: string[];
  blood_group: string;
  date_of_birth: string;
  reports: Report[];
  visualizations: Array<{
    id: string;
    title: string;
    image_url: string;
    created_at: string;
  }>;
}

// Dummy visualization data for demo
const DUMMY_VISUALIZATIONS: Record<string, Array<{ id: string; title: string; image_url: string; created_at: string }>> = {
  'PAT001': [
    { id: 'VIZ001', title: 'Cardiac Artery Visualization', image_url: '/assets/viz-cardiac-1.png', created_at: '2025-12-10' },
    { id: 'VIZ002', title: 'Heart Chamber Analysis', image_url: '/assets/viz-cardiac-2.png', created_at: '2025-12-08' },
  ],
  'PAT002': [
    { id: 'VIZ003', title: 'Pancreas Function Visualization', image_url: '/assets/viz-diabetes-1.png', created_at: '2025-12-08' },
  ],
  'PAT003': [
    { id: 'VIZ004', title: 'Lung Tissue Analysis', image_url: '/assets/viz-pulmonary-1.png', created_at: '2025-12-05' },
  ],
};

// Dummy patient full names
const PATIENT_NAMES: Record<string, string> = {
  'PAT001': 'Koushik Deb',
  'PAT002': 'Priya Patel',
  'PAT003': 'Mohammed Ali',
};

// Dummy patient data
const PATIENT_DATA: Record<string, { blood_group: string; date_of_birth: string }> = {
  'PAT001': { blood_group: 'O+', date_of_birth: '1970-06-15' },
  'PAT002': { blood_group: 'A+', date_of_birth: '1983-03-22' },
  'PAT003': { blood_group: 'B+', date_of_birth: '1967-08-10' },
};

interface DoctorDashboardProps {
  user: User;
  onLogout: () => void;
}

const DoctorDashboard: React.FC<DoctorDashboardProps> = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'patients' | 'reports' | 'visualize' | 'chat'>('overview');
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [analyzing, setAnalyzing] = useState<string | null>(null);
  const [selectedPatient, setSelectedPatient] = useState<PatientDetails | null>(null);
  const [showPatientModal, setShowPatientModal] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, [user.id]);

  const loadDashboard = async () => {
    try {
      const [dashData, reportsData] = await Promise.all([
        userApi.getDashboard(user.id),
        userApi.getReports()
      ]);
      setDashboard(dashData);
      setReports(reportsData);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async (report: Report) => {
    setAnalyzing(report.id);
    try {
      // Process the report with Gemini AI
      const response = await fetch(`${API_BASE}/reports/process/${report.id}`, {
        method: 'POST'
      });
      if (response.ok) {
        // Refresh reports list
        const reportsData = await userApi.getReports();
        setReports(reportsData);
        alert(`Report "${report.title}" analyzed successfully!`);
      }
    } catch (err) {
      console.error('Analysis failed:', err);
      alert('Analysis failed. Please try again.');
    } finally {
      setAnalyzing(null);
    }
  };

  const handleVisualize = (report: Report) => {
    setSelectedReport(report);
    setActiveTab('visualize');
  };

  const handleViewPatientDetails = (patientId: string, conditions: string[]) => {
    // Get patient reports
    const patientReports = reports.filter(r => r.patient_id === patientId);
    
    // Get dummy visualizations for this patient
    const visualizations = DUMMY_VISUALIZATIONS[patientId] || [];
    
    const patientDetails: PatientDetails = {
      user_id: patientId,
      full_name: PATIENT_NAMES[patientId] || patientId,
      conditions: conditions,
      blood_group: PATIENT_DATA[patientId]?.blood_group || 'Unknown',
      date_of_birth: PATIENT_DATA[patientId]?.date_of_birth || 'Unknown',
      reports: patientReports,
      visualizations: visualizations,
    };
    
    setSelectedPatient(patientDetails);
    setShowPatientModal(true);
  };

  const closePatientModal = () => {
    setShowPatientModal(false);
    setSelectedPatient(null);
  };

  const profile = dashboard?.profile as { specialization?: string; hospital?: string; years_experience?: number } | undefined;

  return (
    <div className="dashboard doctor-dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <div className="logo-container">
            <img src="/assets/logo.png" alt="FIBOMed" className="header-logo" />
            <h1>FIBOMed</h1>
          </div>
          <span className="role-badge doctor">DOCTOR PORTAL</span>
        </div>
        <div className="header-right">
          <span className="user-info">
            <img src="/assets/role-doctor.png" alt="" className="user-icon" />
            {user.full_name}
            {profile?.specialization && <span className="specialization"> • {profile.specialization}</span>}
          </span>
          <button onClick={onLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button className={activeTab === 'overview' ? 'active' : ''} onClick={() => setActiveTab('overview')}>
          Overview
        </button>
        <button className={activeTab === 'patients' ? 'active' : ''} onClick={() => setActiveTab('patients')}>
          My Patients
        </button>
        <button className={activeTab === 'reports' ? 'active' : ''} onClick={() => setActiveTab('reports')}>
          Reports
        </button>
        <button className={activeTab === 'visualize' ? 'active' : ''} onClick={() => setActiveTab('visualize')}>
          Visualize
        </button>
        <button className={activeTab === 'chat' ? 'active' : ''} onClick={() => setActiveTab('chat')}>
          AI Chat
        </button>
      </nav>

      <main className="dashboard-content">
        {loading ? (
          <div className="loading">Loading dashboard...</div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <div className="overview-tab">
                <div className="stats-grid">
                  <div className="stat-card">
                    <span className="stat-icon">👥</span>
                    <span className="stat-value">{dashboard?.patients_count || 0}</span>
                    <span className="stat-label">Active Patients</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-icon">📋</span>
                    <span className="stat-value">{reports.length}</span>
                    <span className="stat-label">Total Reports</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-icon">🎨</span>
                    <span className="stat-value">{reports.filter(r => r.status === 'completed').length}</span>
                    <span className="stat-label">Visualizations</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-icon">⏳</span>
                    <span className="stat-value">{reports.filter(r => r.status === 'pending').length}</span>
                    <span className="stat-label">Pending Review</span>
                  </div>
                </div>

                <div className="info-cards">
                  <div className="info-card">
                    <h3>Profile</h3>
                    <p><strong>Hospital:</strong> {profile?.hospital || 'N/A'}</p>
                    <p><strong>Specialization:</strong> {profile?.specialization || 'N/A'}</p>
                    <p><strong>Experience:</strong> {profile?.years_experience || 0} years</p>
                  </div>
                  <div className="info-card">
                    <h3>Recent Activity</h3>
                    <ul className="activity-list">
                      <li>Generated cardiac visualization for PAT001</li>
                      <li>Reviewed diabetes report for PAT002</li>
                      <li>Updated treatment plan for PAT003</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'patients' && (
              <div className="patients-tab">
                <h2>My Patients</h2>
                <div className="patients-grid">
                  {dashboard?.patients?.map((patient) => (
                    <div key={patient.user_id} className="patient-card">
                      <div className="patient-avatar">
                        <img src="/assets/role-patient.png" alt="" />
                      </div>
                      <div className="patient-info">
                        <h4>{PATIENT_NAMES[patient.user_id] || patient.user_id}</h4>
                        <p className="patient-id">{patient.user_id}</p>
                        <div className="conditions">
                          {patient.conditions.map((c, i) => (
                            <span key={i} className="condition-tag">{c}</span>
                          ))}
                        </div>
                      </div>
                      <button 
                        className="view-btn"
                        onClick={() => handleViewPatientDetails(patient.user_id, patient.conditions)}
                      >
                        View Details
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'reports' && (
              <div className="reports-tab">
                <h2>Medical Reports</h2>
                <div className="reports-list">
                  {reports.map((report) => (
                    <div key={report.id} className="report-card">
                      <div className="report-icon">
                        📄
                      </div>
                      <div className="report-info">
                        <h4>{report.title}</h4>
                        <p>Patient: {report.patient_id} • Type: {report.report_type}</p>
                        <span className={`status-badge ${report.status}`}>{report.status}</span>
                      </div>
                      <div className="report-actions">
                        <button 
                          className="action-btn" 
                          onClick={() => handleAnalyze(report)}
                          disabled={analyzing === report.id}
                        >
                          {analyzing === report.id ? 'Analyzing...' : 'Analyze'}
                        </button>
                        <button 
                          className="action-btn primary"
                          onClick={() => handleVisualize(report)}
                        >
                          Visualize
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'visualize' && (() => {
              const doctorSessionId = selectedReport ? `viz-${user.id}-${selectedReport.id}` : `viz-${user.id}`;
              console.log('=== DOCTOR VISUALIZE TAB ===');
              console.log('Selected report:', selectedReport);
              console.log('Doctor user.id:', user.id);
              console.log('Session ID for ChatInterface:', doctorSessionId);
              return (
              <div className="visualize-tab">
                <h2>Medical Visualization</h2>
                {selectedReport && (
                  <div className="selected-report-info">
                    <p>For: <strong>{selectedReport.title}</strong></p>
                    <p style={{fontSize: '0.8rem', color: '#666'}}>Session: {doctorSessionId}</p>
                  </div>
                )}
                <ChatInterface 
                  key={`viz-${selectedReport?.id || 'default'}`}
                  initialPrompt={selectedReport ? `Generate a medical visualization for ${selectedReport.report_type} showing ${selectedReport.title}` : undefined} 
                  userId={user.id}
                  sessionId={doctorSessionId}
                />
              </div>
              );
            })()}

            {activeTab === 'chat' && (() => {
              const chatSessionId = `chat-${user.id}`;
              console.log('=== DOCTOR AI CHAT TAB ===');
              console.log('Chat session ID:', chatSessionId);
              return (
              <div className="chat-tab">
                <h2>AI Assistant</h2>
                <p style={{fontSize: '0.8rem', color: '#666', marginBottom: '10px'}}>Session: {chatSessionId}</p>
                <ChatInterface 
                  key={`chat-${user.id}`}
                  userId={user.id} 
                  sessionId={chatSessionId}
                />
              </div>
              );
            })()}
          </>
        )}
      </main>

      {/* Patient Details Modal */}
      {showPatientModal && selectedPatient && (
        <div className="modal-overlay" onClick={closePatientModal}>
          <div className="modal-content patient-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closePatientModal}>×</button>
            
            <div className="modal-header">
              <img src="/assets/role-patient.png" alt="" className="modal-avatar" />
              <div>
                <h2>{selectedPatient.full_name}</h2>
                <p className="patient-id-modal">{selectedPatient.user_id}</p>
              </div>
            </div>

            <div className="modal-body">
              <div className="patient-details-grid">
                <div className="detail-card">
                  <span className="detail-label">Blood Group</span>
                  <span className="detail-value">{selectedPatient.blood_group}</span>
                </div>
                <div className="detail-card">
                  <span className="detail-label">Date of Birth</span>
                  <span className="detail-value">{selectedPatient.date_of_birth}</span>
                </div>
                <div className="detail-card">
                  <span className="detail-label">Reports</span>
                  <span className="detail-value">{selectedPatient.reports.length}</span>
                </div>
                <div className="detail-card">
                  <span className="detail-label">Visualizations</span>
                  <span className="detail-value">{selectedPatient.visualizations.length}</span>
                </div>
              </div>

              <div className="conditions-section">
                <h3>Medical Conditions</h3>
                <div className="conditions-list">
                  {selectedPatient.conditions.map((condition, i) => (
                    <div key={i} className="condition-item">
                      <span className="condition-name">{condition}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="reports-section">
                <h3>Medical Reports</h3>
                {selectedPatient.reports.length === 0 ? (
                  <p className="no-data">No reports available</p>
                ) : (
                  <div className="mini-reports-list">
                    {selectedPatient.reports.map((report) => (
                      <div key={report.id} className="mini-report-card">
                        <div className="mini-report-icon">📄</div>
                        <div className="mini-report-info">
                          <h4>{report.title}</h4>
                          <p>Type: {report.report_type} • Status: {report.status}</p>
                        </div>
                        <button 
                          className="action-btn primary small"
                          onClick={() => {
                            closePatientModal();
                            handleVisualize(report);
                          }}
                        >
                          Visualize
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="visualizations-section">
                <h3>Previous Visualizations</h3>
                {selectedPatient.visualizations.length === 0 ? (
                  <p className="no-data">No visualizations generated yet</p>
                ) : (
                  <div className="viz-gallery">
                    {selectedPatient.visualizations.map((viz) => (
                      <div key={viz.id} className="viz-card">
                        <div className="viz-placeholder">
                          <span className="viz-icon">🎨</span>
                          <span className="viz-title">{viz.title}</span>
                        </div>
                        <p className="viz-date">Created: {viz.created_at}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DoctorDashboard;
