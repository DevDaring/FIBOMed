/**
 * Patient Dashboard Component
 */
import { useState, useEffect } from 'react';
import type { User, DashboardData, Report } from '../../types/user.types';
import { userApi } from '../../api/user.api';
import ChatInterface from '../chat/ChatInterface';
import './Dashboard.css';

interface PatientDashboardProps {
  user: User;
  onLogout: () => void;
}

const PatientDashboard: React.FC<PatientDashboardProps> = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'reports' | 'visualizations' | 'chat'>('overview');
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);

  useEffect(() => {
    loadDashboard();
  }, [user.id]);

  const loadDashboard = async () => {
    try {
      const [dashData, reportsData] = await Promise.all([
        userApi.getDashboard(user.id),
        userApi.getReports(user.id)
      ]);
      console.log('=== PATIENT DASHBOARD LOADED ===');
      console.log('Dashboard data:', dashData);
      console.log('Reports data:', reportsData);
      // Log each report's doctor_id to verify it's being returned
      reportsData.forEach((r: any) => {
        console.log(`Report ${r.id}: doctor_id=${r.doctor_id}, patient_id=${r.patient_id}`);
      });
      setDashboard(dashData);
      setReports(reportsData);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const profile = dashboard?.profile as { blood_group?: string; conditions?: string[]; assigned_doctor_id?: string } | undefined;

  // Handle View Visual button click - switch to visualizations tab with report context
  const handleViewVisual = (report: Report) => {
    console.log('handleViewVisual called with report:', report);
    console.log('Report doctor_id:', report.doctor_id);
    console.log('Session ID will be:', `viz-${report.doctor_id}-${report.id}`);
    setSelectedReport(report);
    setActiveTab('visualizations');
  };

  return (
    <div className="dashboard patient-dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <div className="logo-container">
            <img src="/assets/logo.png" alt="FIBOMed" className="header-logo" />
            <h1>FIBOMed</h1>
          </div>
          <span className="role-badge patient">PATIENT PORTAL</span>
        </div>
        <div className="header-right">
          <span className="user-info">
            <img src="/assets/role-patient.png" alt="" className="user-icon" />
            {user.full_name}
          </span>
          <button onClick={onLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <nav className="dashboard-nav">
        <button className={activeTab === 'overview' ? 'active' : ''} onClick={() => setActiveTab('overview')}>
          My Health
        </button>
        <button className={activeTab === 'reports' ? 'active' : ''} onClick={() => setActiveTab('reports')}>
          My Reports
        </button>
        <button className={activeTab === 'visualizations' ? 'active' : ''} onClick={() => setActiveTab('visualizations')}>
          Visual Explanations
        </button>
        <button className={activeTab === 'chat' ? 'active' : ''} onClick={() => setActiveTab('chat')}>
          Ask AI
        </button>
      </nav>

      <main className="dashboard-content">
        {loading ? (
          <div className="loading">Loading your health data...</div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <div className="overview-tab">
                <div className="health-summary">
                  <h2>Health Summary</h2>
                  <div className="health-cards">
                    <div className="health-card">
                      <span className="stat-icon">🩸</span>
                      <span className="health-label">Blood Group</span>
                      <span className="health-value">{profile?.blood_group || 'N/A'}</span>
                    </div>
                    <div className="health-card">
                      <span className="stat-icon">👨‍⚕️</span>
                      <span className="health-label">Assigned Doctor</span>
                      <span className="health-value">{profile?.assigned_doctor_id || 'N/A'}</span>
                    </div>
                    <div className="health-card">
                      <span className="stat-icon">📋</span>
                      <span className="health-label">Reports</span>
                      <span className="health-value">{reports.length}</span>
                    </div>
                  </div>
                </div>

                {profile?.conditions && profile.conditions.length > 0 && (
                  <div className="conditions-section">
                    <h3>Current Conditions</h3>
                    <div className="conditions-list">
                      {profile.conditions.map((condition, i) => (
                        <div key={i} className="condition-item">
                          <span className="condition-name">{condition}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="info-card">
                  <h3>Understanding Your Health</h3>
                  <p>
                    FIBOMed helps you understand your medical reports through visual explanations.
                    Use the "Visual Explanations" tab to see your conditions illustrated clearly,
                    or chat with our AI assistant for any questions.
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'reports' && (
              <div className="reports-tab">
                <h2>My Medical Reports</h2>
                <div className="reports-list">
                  {reports.length === 0 ? (
                    <div className="empty-state">
                      <p>No reports available yet.</p>
                    </div>
                  ) : (
                    reports.map((report) => (
                      <div key={report.id} className="report-card patient-report">
                        <div className="report-icon">
                          <img src="/assets/feature-analysis.svg" alt="Report" style={{width: '30px', height: '30px'}} />
                        </div>
                        <div className="report-info">
                          <h4>{report.title}</h4>
                          <p>Type: {report.report_type}</p>
                          <p>Date: {new Date(report.created_at).toLocaleDateString()}</p>
                          <span className={`status-badge ${report.status}`}>{report.status}</span>
                        </div>
                        <div className="report-actions">
                          <button 
                            className="action-btn primary"
                            onClick={() => handleViewVisual(report)}
                          >
                            View Visual
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            {activeTab === 'visualizations' && (() => {
              const sessionIdForChat = selectedReport ? `viz-${selectedReport.doctor_id}-${selectedReport.id}` : undefined;
              console.log('=== PATIENT VISUALIZATIONS TAB ===');
              console.log('selectedReport:', selectedReport);
              console.log('selectedReport.doctor_id:', selectedReport?.doctor_id);
              console.log('selectedReport.id:', selectedReport?.id);
              console.log('Computed sessionIdForChat:', sessionIdForChat);
              return (
              <div className="visualize-tab">
                <h2>Visual Health Explanations</h2>
                <p className="tab-description">
                  {selectedReport 
                    ? "View the visualization your doctor created for your report."
                    : "Select a report from 'My Reports' tab and click 'View Visual' to see your doctor's analysis."}
                </p>
                {selectedReport && (
                  <div className="selected-report-info">
                    <p>Viewing visualization for: <strong>{selectedReport.title}</strong></p>
                    <p style={{fontSize: '0.85rem', color: '#666', marginTop: '4px'}}>
                      Created by: Dr. {selectedReport.doctor_id === 'DOC001' ? 'Anita Sharma' : 
                                       selectedReport.doctor_id === 'DOC002' ? 'Vikram Singh' : 
                                       selectedReport.doctor_id === 'DOC003' ? 'Sunita Reddy' : selectedReport.doctor_id}
                    </p>
                    <p style={{fontSize: '0.75rem', color: '#999', marginTop: '4px'}}>
                      Session: {sessionIdForChat}
                    </p>
                    <button 
                      className="action-btn small" 
                      onClick={() => setSelectedReport(null)}
                      style={{marginTop: '8px'}}
                    >
                      Clear Selection
                    </button>
                  </div>
                )}
                {!selectedReport && (
                  <div className="info-card" style={{marginBottom: '20px', padding: '15px', background: '#fff3cd', borderRadius: '8px'}}>
                    <p style={{margin: 0, color: '#856404'}}>
                      💡 To view your doctor's analysis, go to "My Reports" tab and click "View Visual" on any report.
                    </p>
                  </div>
                )}
                <ChatInterface 
                  userId={user.id} 
                  sessionId={sessionIdForChat}
                  key={selectedReport ? `patient-viz-${selectedReport.doctor_id}-${selectedReport.id}` : 'patient-viz-default'}
                />
              </div>
              );
            })()}

            {activeTab === 'chat' && (
              <div className="chat-tab">
                <h2>Health Assistant</h2>
                <p className="tab-description">
                  Ask any questions about your health, medications, or medical terms.
                </p>
                <ChatInterface userId={user.id} />
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
};

export default PatientDashboard;
