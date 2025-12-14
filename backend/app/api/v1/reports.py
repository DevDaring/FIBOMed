"""Medical Reports API endpoints"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from ...services.report_service import get_report_service, ProcessedReport
from ...services.fibo_service import get_fibo_service
from ...core.exceptions import ReportProcessingError

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportUploadResponse(BaseModel):
    """Response after uploading a report"""
    report_id: str
    message: str
    status: str


class ReportAnalysisResponse(BaseModel):
    """Response with report analysis"""
    report_id: str
    patient_id: str
    report_type: str
    conditions: List[str]
    severity: str
    organs: List[str]
    findings: List[str]
    summary: str
    visualization_prompt: str
    fibo_parameters: dict
    processed_at: str


class ReportListItem(BaseModel):
    """Report list item"""
    id: str
    patient_id: str
    doctor_id: str
    title: str
    report_type: str
    status: str
    created_at: str
    file_path: Optional[str] = None


class GenerateVisualizationRequest(BaseModel):
    """Request to generate visualization from report"""
    report_id: str
    complexity_level: str = "patient_friendly"
    aspect_ratio: str = "1:1"


class VisualizationFromReportResponse(BaseModel):
    """Response with generated visualization"""
    visualization_id: str
    image_url: str
    report_id: str
    prompt_used: str
    created_at: str


@router.post("/upload", response_model=ReportUploadResponse)
async def upload_report(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    uploaded_by_id: str = Form(...),
    report_type: str = Form(...)
):
    """
    Upload a medical report for processing.
    
    Supported formats: TXT, PDF, DOCX
    """
    try:
        report_service = get_report_service()
        
        # Read file content
        content = await file.read()
        
        # Upload and save
        report_id = await report_service.upload_report(
            file_content=content,
            filename=file.filename,
            patient_id=patient_id,
            uploaded_by_id=uploaded_by_id,
            report_type=report_type
        )
        
        return ReportUploadResponse(
            report_id=report_id,
            message="Report uploaded successfully. Processing will begin shortly.",
            status="pending"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "UPLOAD_FAILED", "message": str(e)}
        )


@router.post("/process/{report_id}", response_model=ReportAnalysisResponse)
async def process_report(report_id: str):
    """
    Process a medical report using Gemini AI analysis.
    
    This extracts medical entities, generates FIBO parameters,
    and creates a visualization prompt.
    """
    try:
        report_service = get_report_service()
        
        processed = await report_service.process_report(report_id)
        
        return ReportAnalysisResponse(
            report_id=processed.report_id,
            patient_id=processed.patient_id,
            report_type=processed.report_type,
            conditions=processed.analysis.conditions,
            severity=processed.analysis.severity,
            organs=processed.analysis.organs,
            findings=processed.analysis.findings,
            summary=processed.analysis.summary,
            visualization_prompt=processed.visualization_prompt,
            fibo_parameters=processed.analysis.fibo_parameters or {},
            processed_at=processed.created_at
        )
        
    except ReportProcessingError as e:
        raise HTTPException(
            status_code=400 if e.code == "REPORT_NOT_FOUND" else 500,
            detail={"code": e.code, "message": e.message}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "PROCESSING_FAILED", "message": str(e)}
        )


@router.get("/list", response_model=List[ReportListItem])
async def list_reports(patient_id: Optional[str] = None, user_id: Optional[str] = None):
    """
    List all reports, optionally filtered by patient ID or user ID.
    """
    try:
        report_service = get_report_service()
        
        # If user_id is provided, use it as patient_id filter
        filter_patient = patient_id or user_id
        reports = await report_service.get_all_reports(filter_patient)
        
        return [
            ReportListItem(
                id=r['id'],
                patient_id=r['patient_id'],
                doctor_id=r.get('uploaded_by_id', ''),
                title=r.get('analysis_result', f"{r['report_type'].title()} Report"),
                report_type=r['report_type'],
                status=r['processed_status'],
                created_at=r.get('created_at', r.get('upload_date', '')),
                file_path=r.get('file_path')
            )
            for r in reports
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "LIST_FAILED", "message": str(e)}
        )


@router.get("/{report_id}")
async def get_report(report_id: str):
    """
    Get a specific report with its analysis.
    """
    try:
        report_service = get_report_service()
        report = await report_service.get_report_with_analysis(report_id)
        
        if not report:
            raise HTTPException(
                status_code=404,
                detail={"code": "NOT_FOUND", "message": f"Report {report_id} not found"}
            )
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "RETRIEVAL_FAILED", "message": str(e)}
        )


@router.post("/generate-visualization", response_model=VisualizationFromReportResponse)
async def generate_visualization_from_report(request: GenerateVisualizationRequest):
    """
    Generate a FIBO visualization from a processed report.
    
    Uses the report's analysis to create an appropriate medical visualization.
    """
    try:
        report_service = get_report_service()
        fibo_service = get_fibo_service()
        
        # Get report with analysis
        report = await report_service.get_report_with_analysis(request.report_id)
        if not report:
            raise HTTPException(
                status_code=404,
                detail={"code": "NOT_FOUND", "message": f"Report {request.report_id} not found"}
            )
        
        if report['processed_status'] != 'completed':
            raise HTTPException(
                status_code=400,
                detail={"code": "NOT_PROCESSED", "message": "Report must be processed first"}
            )
        
        # Get FIBO parameters and generate prompt
        fibo_params = report.get('fibo_parameters_parsed', {})
        
        # Build visualization prompt from analysis
        analysis = report.get('gemini_analysis_parsed', {})
        organs = analysis.get('organs', ['body'])
        conditions = analysis.get('conditions', ['condition'])
        severity = analysis.get('severity', 'moderate')
        
        prompt = f"Medical visualization of {', '.join(organs)} showing {', '.join(conditions)} with {severity} severity, {request.complexity_level} style"
        
        # Generate visualization
        result = await fibo_service.generate_visualization(
            prompt=prompt,
            aspect_ratio=request.aspect_ratio
        )
        
        return VisualizationFromReportResponse(
            visualization_id=result.visualization_id,
            image_url=result.image_url,
            report_id=request.report_id,
            prompt_used=prompt,
            created_at=result.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "GENERATION_FAILED", "message": str(e)}
        )
