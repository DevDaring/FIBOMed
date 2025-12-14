/**
 * User Types for FIBOMed
 */

export type UserRole = 'doctor' | 'patient' | 'technician' | 'admin';

export interface User {
  id: string;
  email: string;
  username: string;
  role: UserRole;
  full_name: string;
  is_active: boolean;
}

export interface DoctorProfile {
  license_number: string;
  specialization: string;
  hospital: string;
  years_experience: number;
  department?: string;
}

export interface PatientProfile {
  date_of_birth: string;
  blood_group: string;
  conditions: string[];
  assigned_doctor_id: string;
  medical_history?: string;
}

export interface TechnicianProfile {
  certification: string;
  expertise_areas: string[];
  department: string;
}

export interface DashboardData {
  user: User;
  profile?: DoctorProfile | PatientProfile | TechnicianProfile;
  patients_count?: number;
  patients?: Array<{ user_id: string; conditions: string[] }>;
  reports?: Report[];
  visualizations?: Visualization[];
}

export interface Report {
  id: string;
  patient_id: string;
  doctor_id: string;
  title: string;
  report_type: string;
  status: string;
  created_at: string;
  file_path?: string | null;
}

export interface Visualization {
  id: string;
  report_id: string;
  image_url: string;
  prompt: string;
  created_at: string;
  quality_score?: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface TestCredential {
  role: UserRole;
  email: string;
  password: string;
  name: string;
  description: string;
}

export const TEST_CREDENTIALS: TestCredential[] = [
  {
    role: 'doctor',
    email: 'dr.anita@fibomed.com',
    password: 'demo123',
    name: 'Dr. Anita Sharma',
    description: 'Cardiologist - 15 years experience'
  },
  {
    role: 'patient',
    email: 'koushik.deb@email.com',
    password: 'demo123',
    name: 'Koushik Deb',
    description: 'Cardiac patient under Dr. Anita'
  },
  {
    role: 'technician',
    email: 'tech.ravi@fibomed.com',
    password: 'demo123',
    name: 'Ravi Technician',
    description: 'Medical imaging specialist'
  }
];
