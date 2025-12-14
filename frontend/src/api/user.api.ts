/**
 * User API for FIBOMed
 */
import type { User, DashboardData, LoginCredentials, Report } from '../types/user.types';

// Use relative URL in production (same origin), localhost in development
const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
const BACKEND_BASE_URL = isProduction ? '' : 'http://localhost:8000';

export const userApi = {
  /**
   * Login user
   */
  async login(credentials: LoginCredentials): Promise<User> {
    const response = await fetch(`${BACKEND_BASE_URL}/api/v1/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }
    
    return response.json();
  },

  /**
   * Get user dashboard data
   */
  async getDashboard(userId: string): Promise<DashboardData> {
    const response = await fetch(`${BACKEND_BASE_URL}/api/v1/users/dashboard/${userId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch dashboard');
    }
    
    return response.json();
  },

  /**
   * Get all doctors
   */
  async getDoctors(): Promise<User[]> {
    const response = await fetch(`${BACKEND_BASE_URL}/api/v1/users/doctors`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch doctors');
    }
    
    return response.json();
  },

  /**
   * Get reports for a user
   */
  async getReports(userId?: string): Promise<Report[]> {
    const url = userId 
      ? `${BACKEND_BASE_URL}/api/v1/reports/list?user_id=${userId}`
      : `${BACKEND_BASE_URL}/api/v1/reports/list`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error('Failed to fetch reports');
    }
    
    return response.json();
  },

  /**
   * Analyze a report
   */
  async analyzeReport(reportId: string): Promise<{ analysis: string; visualizations: string[] }> {
    const response = await fetch(`${BACKEND_BASE_URL}/api/v1/reports/analyze/${reportId}`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      throw new Error('Failed to analyze report');
    }
    
    return response.json();
  }
};
