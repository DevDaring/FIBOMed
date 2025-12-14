"""User Service for Authentication and User Management"""
import csv
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from ..config import settings
from ..core.exceptions import UserNotFoundError, UnauthorizedError


@dataclass
class User:
    """User data class"""
    id: str
    email: str
    username: str
    role: str
    full_name: str
    is_active: bool


@dataclass
class DoctorProfile:
    """Doctor profile data"""
    user_id: str
    license_number: str
    specialization: str
    hospital: str
    years_experience: int
    department: str


@dataclass
class PatientProfile:
    """Patient profile data"""
    user_id: str
    date_of_birth: str
    blood_group: str
    medical_history: str
    emergency_contact: str
    assigned_doctor_id: str
    conditions: List[str]


class UserService:
    """Service for user management"""

    def __init__(self):
        self.users_csv = Path(settings.CSV_DATA_PATH) / "users.csv"
        self.doctors_csv = Path(settings.CSV_DATA_PATH) / "doctors.csv"
        self.patients_csv = Path(settings.CSV_DATA_PATH) / "patients.csv"
        self.technicians_csv = Path(settings.CSV_DATA_PATH) / "technicians.csv"

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            with open(self.users_csv, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['id'] == user_id:
                        return User(
                            id=row['id'],
                            email=row['email'],
                            username=row['username'],
                            role=row['role'],
                            full_name=row.get('full_name', row['username']),
                            is_active=row.get('is_active', 'true').lower() == 'true'
                        )
        except Exception:
            pass
        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            with open(self.users_csv, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['email'] == email:
                        return User(
                            id=row['id'],
                            email=row['email'],
                            username=row['username'],
                            role=row['role'],
                            full_name=row.get('full_name', row['username']),
                            is_active=row.get('is_active', 'true').lower() == 'true'
                        )
        except Exception:
            pass
        return None

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Note: For hackathon demo, using simple password check.
        In production, use proper password hashing.
        """
        # For demo purposes, accept any password for existing users
        # In production, verify password hash
        user = await self.get_user_by_email(email)
        if user and user.is_active:
            return user
        return None

    async def get_doctor_profile(self, user_id: str) -> Optional[DoctorProfile]:
        """Get doctor profile"""
        try:
            with open(self.doctors_csv, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['user_id'] == user_id:
                        return DoctorProfile(
                            user_id=row['user_id'],
                            license_number=row['license_number'],
                            specialization=row['specialization'],
                            hospital=row['hospital'],
                            years_experience=int(row.get('years_experience', 0)),
                            department=row.get('department', '')
                        )
        except Exception:
            pass
        return None

    async def get_patient_profile(self, user_id: str) -> Optional[PatientProfile]:
        """Get patient profile"""
        try:
            with open(self.patients_csv, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['user_id'] == user_id:
                        conditions = row.get('conditions', '').split('|') if row.get('conditions') else []
                        return PatientProfile(
                            user_id=row['user_id'],
                            date_of_birth=row.get('date_of_birth', ''),
                            blood_group=row.get('blood_group', ''),
                            medical_history=row.get('medical_history_summary', ''),
                            emergency_contact=row.get('emergency_contact', ''),
                            assigned_doctor_id=row.get('assigned_doctor_id', ''),
                            conditions=conditions
                        )
        except Exception:
            pass
        return None

    async def get_all_users_by_role(self, role: str) -> List[User]:
        """Get all users with a specific role"""
        users = []
        try:
            with open(self.users_csv, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['role'] == role:
                        users.append(User(
                            id=row['id'],
                            email=row['email'],
                            username=row['username'],
                            role=row['role'],
                            full_name=row.get('full_name', row['username']),
                            is_active=row.get('is_active', 'true').lower() == 'true'
                        ))
        except Exception:
            pass
        return users

    async def get_patients_for_doctor(self, doctor_id: str) -> List[PatientProfile]:
        """Get all patients assigned to a doctor"""
        patients = []
        try:
            with open(self.patients_csv, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('assigned_doctor_id') == doctor_id:
                        conditions = row.get('conditions', '').split('|') if row.get('conditions') else []
                        patients.append(PatientProfile(
                            user_id=row['user_id'],
                            date_of_birth=row.get('date_of_birth', ''),
                            blood_group=row.get('blood_group', ''),
                            medical_history=row.get('medical_history_summary', ''),
                            emergency_contact=row.get('emergency_contact', ''),
                            assigned_doctor_id=row.get('assigned_doctor_id', ''),
                            conditions=conditions
                        ))
        except Exception:
            pass
        return patients

    async def get_user_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get dashboard data for a user based on their role"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        dashboard = {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "full_name": user.full_name
            }
        }
        
        if user.role == "doctor":
            profile = await self.get_doctor_profile(user_id)
            patients = await self.get_patients_for_doctor(user_id)
            dashboard["profile"] = {
                "license_number": profile.license_number if profile else "",
                "specialization": profile.specialization if profile else "",
                "hospital": profile.hospital if profile else "",
                "years_experience": profile.years_experience if profile else 0
            }
            dashboard["patients_count"] = len(patients)
            dashboard["patients"] = [
                {"user_id": p.user_id, "conditions": p.conditions}
                for p in patients
            ]
            
        elif user.role == "patient":
            profile = await self.get_patient_profile(user_id)
            dashboard["profile"] = {
                "date_of_birth": profile.date_of_birth if profile else "",
                "blood_group": profile.blood_group if profile else "",
                "conditions": profile.conditions if profile else [],
                "assigned_doctor_id": profile.assigned_doctor_id if profile else ""
            }
            
        return dashboard


# Singleton instance
user_service: Optional[UserService] = None


def get_user_service() -> UserService:
    """Get or create the singleton user service instance"""
    global user_service
    if user_service is None:
        user_service = UserService()
    return user_service
