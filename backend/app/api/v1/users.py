"""Users API endpoints for authentication and user management"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from ...services.user_service import get_user_service
from ...core.exceptions import UserNotFoundError

router = APIRouter(prefix="/users", tags=["users"])


class LoginRequest(BaseModel):
    """Login request"""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Login response"""
    success: bool
    user_id: str
    email: str
    username: str
    role: str
    full_name: str
    message: str


class UserResponse(BaseModel):
    """User response"""
    id: str
    email: str
    username: str
    role: str
    full_name: str
    is_active: bool


class DoctorResponse(BaseModel):
    """Doctor profile response"""
    user_id: str
    license_number: str
    specialization: str
    hospital: str
    years_experience: int
    department: str


class PatientResponse(BaseModel):
    """Patient profile response"""
    user_id: str
    date_of_birth: str
    blood_group: str
    medical_history: str
    emergency_contact: str
    assigned_doctor_id: str
    conditions: List[str]


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return user info.
    
    For hackathon demo, accepts any password for existing users.
    """
    try:
        user_service = get_user_service()
        user = await user_service.authenticate(request.email, request.password)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail={"code": "AUTH_FAILED", "message": "Invalid email or password"}
            )
        
        return LoginResponse(
            success=True,
            user_id=user.id,
            email=user.email,
            username=user.username,
            role=user.role,
            full_name=user.full_name,
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "LOGIN_ERROR", "message": str(e)}
        )


@router.get("/me/{user_id}", response_model=UserResponse)
async def get_current_user(user_id: str):
    """Get current user info"""
    try:
        user_service = get_user_service()
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail={"code": "NOT_FOUND", "message": "User not found"}
            )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role,
            full_name=user.full_name,
            is_active=user.is_active
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "ERROR", "message": str(e)}
        )


@router.get("/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    """
    Get dashboard data for a user.
    
    Returns role-specific data including:
    - Doctor: Patient list, specialization info
    - Patient: Health profile, assigned doctor
    - Technician: Processing queue info
    """
    try:
        user_service = get_user_service()
        dashboard = await user_service.get_user_dashboard_data(user_id)
        return dashboard
        
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "ERROR", "message": str(e)}
        )


@router.get("/doctors", response_model=List[UserResponse])
async def list_doctors():
    """List all doctors"""
    try:
        user_service = get_user_service()
        doctors = await user_service.get_all_users_by_role("doctor")
        
        return [
            UserResponse(
                id=d.id,
                email=d.email,
                username=d.username,
                role=d.role,
                full_name=d.full_name,
                is_active=d.is_active
            )
            for d in doctors
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "ERROR", "message": str(e)}
        )


@router.get("/patients", response_model=List[UserResponse])
async def list_patients():
    """List all patients"""
    try:
        user_service = get_user_service()
        patients = await user_service.get_all_users_by_role("patient")
        
        return [
            UserResponse(
                id=p.id,
                email=p.email,
                username=p.username,
                role=p.role,
                full_name=p.full_name,
                is_active=p.is_active
            )
            for p in patients
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "ERROR", "message": str(e)}
        )


@router.get("/doctor/{user_id}/patients")
async def get_doctor_patients(user_id: str):
    """Get all patients assigned to a doctor"""
    try:
        user_service = get_user_service()
        
        # Verify user is a doctor
        user = await user_service.get_user_by_id(user_id)
        if not user or user.role != "doctor":
            raise HTTPException(
                status_code=404,
                detail={"code": "NOT_FOUND", "message": "Doctor not found"}
            )
        
        patients = await user_service.get_patients_for_doctor(user_id)
        
        # Get full user info for each patient
        result = []
        for p in patients:
            patient_user = await user_service.get_user_by_id(p.user_id)
            if patient_user:
                result.append({
                    "user_id": p.user_id,
                    "full_name": patient_user.full_name,
                    "email": patient_user.email,
                    "conditions": p.conditions,
                    "blood_group": p.blood_group,
                    "date_of_birth": p.date_of_birth
                })
        
        return {"doctor_id": user_id, "patients": result}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "ERROR", "message": str(e)}
        )
