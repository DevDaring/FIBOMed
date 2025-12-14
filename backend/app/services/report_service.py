"""Report Processing Service for Medical Report Analysis"""
import csv
import json
import os
import uuid
from pathlib import Path as PathLib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from ..config import settings, PROJECT_ROOT
from ..core.exceptions import ReportProcessingError
from ..integrations.google_gemini.client import GeminiClient


@dataclass
class ReportAnalysis:
    """Result from medical report analysis"""
    report_id: str
    patient_id: str
    conditions: List[str]
    severity: str
    organs: List[str]
    findings: List[str]
    treatment_plan: List[str]
    fibo_parameters: Dict[str, Any]
    summary: str


@dataclass
class ProcessedReport:
    """Processed report with analysis and visualization parameters"""
    report_id: str
    patient_id: str
    report_type: str
    file_path: str
    analysis: ReportAnalysis
    visualization_prompt: str
    created_at: str


class ReportService:
    """Service for processing medical reports"""

    def __init__(self):
        self.reports_csv = Path(settings.CSV_DATA_PATH) / "reports.csv"
        self.uploads_path = PROJECT_ROOT / "data" / "uploads" / "reports"
        self.gemini_client = GeminiClient()
        self._ensure_paths()

    def _ensure_paths(self):
        """Ensure required directories exist"""
        self.uploads_path.mkdir(parents=True, exist_ok=True)
        if not self.reports_csv.exists():
            self._create_reports_csv()

    def _create_reports_csv(self):
        """Create reports CSV with headers"""
        with open(self.reports_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'patient_id', 'uploaded_by_id', 'report_type', 'file_path',
                'upload_date', 'processed_status', 'analysis_result', 'gemini_analysis',
                'fibo_parameters', 'created_at'
            ])

    async def upload_report(
        self,
        file_content: bytes,
        filename: str,
        patient_id: str,
        uploaded_by_id: str,
        report_type: str
    ) -> str:
        """
        Upload and save a medical report.
        
        Returns:
            report_id: Unique identifier for the uploaded report
        """
        report_id = f"RPT{uuid.uuid4().hex[:8].upper()}"
        
        # Save file
        file_ext = Path(filename).suffix or '.txt'
        saved_filename = f"{report_id}{file_ext}"
        file_path = self.uploads_path / saved_filename
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Record in CSV
        with open(self.reports_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                report_id, patient_id, uploaded_by_id, report_type,
                str(file_path), datetime.utcnow().date().isoformat(),
                'pending', '', '', '', datetime.utcnow().isoformat()
            ])
        
        return report_id

    async def process_report(self, report_id: str) -> ProcessedReport:
        """
        Process a medical report using Gemini for analysis.
        
        Args:
            report_id: The report ID to process
            
        Returns:
            ProcessedReport with analysis and visualization parameters
        """
        # Get report from CSV
        report_data = await self._get_report(report_id)
        if not report_data:
            raise ReportProcessingError(
                message=f"Report not found: {report_id}",
                code="REPORT_NOT_FOUND"
            )
        
        # Read report content
        file_path = report_data['file_path']
        # Handle relative paths
        if not os.path.isabs(file_path):
            file_path = PROJECT_ROOT / file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
        except Exception as e:
            raise ReportProcessingError(
                message=f"Failed to read report file: {str(e)}",
                code="FILE_READ_ERROR"
            )
        
        # Analyze with Gemini
        analysis = await self._analyze_with_gemini(report_content, report_data['report_type'])
        
        # Generate FIBO parameters
        fibo_params = self._generate_fibo_parameters(analysis)
        
        # Generate visualization prompt
        viz_prompt = self._generate_visualization_prompt(analysis)
        
        # Update CSV with analysis
        await self._update_report_analysis(report_id, analysis, fibo_params)
        
        return ProcessedReport(
            report_id=report_id,
            patient_id=report_data['patient_id'],
            report_type=report_data['report_type'],
            file_path=file_path,
            analysis=analysis,
            visualization_prompt=viz_prompt,
            created_at=datetime.utcnow().isoformat()
        )

    async def _analyze_with_gemini(
        self, 
        report_content: str, 
        report_type: str
    ) -> ReportAnalysis:
        """Analyze medical report using Gemini"""
        
        analysis_prompt = f"""Analyze this medical report and extract structured information.
        
Report Type: {report_type}

Report Content:
{report_content}

Please provide a JSON response with the following structure:
{{
    "conditions": ["list of diagnosed conditions"],
    "severity": "mild/moderate/severe/critical",
    "organs": ["list of affected organs"],
    "findings": ["key clinical findings"],
    "treatment_plan": ["treatment recommendations"],
    "summary": "brief patient-friendly summary of the report"
}}

Focus on extracting medically accurate information that can be used to generate educational visualizations."""

        try:
            response = await self.gemini_client.generate_response(analysis_prompt)
            
            # Parse JSON from response
            # Try to extract JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis_data = json.loads(json_str)
            else:
                # Fallback if no JSON found
                analysis_data = {
                    "conditions": ["Unable to parse"],
                    "severity": "unknown",
                    "organs": [],
                    "findings": [response[:500]],
                    "treatment_plan": [],
                    "summary": response[:200]
                }
            
            return ReportAnalysis(
                report_id="",  # Will be set by caller
                patient_id="",  # Will be set by caller
                conditions=analysis_data.get("conditions", []),
                severity=analysis_data.get("severity", "unknown"),
                organs=analysis_data.get("organs", []),
                findings=analysis_data.get("findings", []),
                treatment_plan=analysis_data.get("treatment_plan", []),
                fibo_parameters={},  # Will be generated separately
                summary=analysis_data.get("summary", "")
            )
            
        except Exception as e:
            raise ReportProcessingError(
                message=f"Gemini analysis failed: {str(e)}",
                code="ANALYSIS_FAILED"
            )

    def _generate_fibo_parameters(self, analysis: ReportAnalysis) -> Dict[str, Any]:
        """Generate FIBO JSON parameters from analysis"""
        
        # Map organs to FIBO system types
        organ_system_map = {
            "heart": "cardiovascular",
            "coronary arteries": "cardiovascular",
            "lungs": "respiratory",
            "bronchi": "respiratory",
            "liver": "digestive",
            "kidney": "urinary",
            "kidneys": "urinary",
            "brain": "nervous",
            "pancreas": "endocrine",
            "stomach": "digestive",
            "intestine": "digestive"
        }
        
        # Determine primary organ and system
        primary_organ = analysis.organs[0] if analysis.organs else "body"
        primary_system = organ_system_map.get(primary_organ.lower(), "general")
        
        # Map severity to numeric scale
        severity_map = {
            "mild": 3,
            "moderate": 5,
            "severe": 7,
            "critical": 9,
            "unknown": 5
        }
        severity_score = severity_map.get(analysis.severity.lower(), 5)
        
        # Determine pathology type from conditions
        pathology_type = "general_condition"
        for condition in analysis.conditions:
            condition_lower = condition.lower()
            if "block" in condition_lower or "stenosis" in condition_lower:
                pathology_type = "blockage"
            elif "diabetes" in condition_lower:
                pathology_type = "metabolic_disorder"
            elif "emphysema" in condition_lower or "copd" in condition_lower:
                pathology_type = "emphysema"
            elif "tumor" in condition_lower or "cancer" in condition_lower:
                pathology_type = "tumor"
            elif "inflammation" in condition_lower:
                pathology_type = "inflammation"
        
        return {
            "scene_type": "medical_visualization",
            "primary_subject": {
                "system": primary_system,
                "organ": primary_organ,
                "view": "anterior",
                "zoom_level": "focused"
            },
            "pathology": {
                "type": pathology_type,
                "severity": severity_score,
                "conditions": analysis.conditions
            },
            "style": {
                "complexity": "patient_friendly",
                "realism": "semi-realistic",
                "color_palette": "medical_standard"
            },
            "background": {
                "type": "blurred_body_interior",
                "context": f"{primary_system}_cavity"
            },
            "annotations": {
                "enabled": True,
                "language": "en",
                "highlight_pathology": True
            }
        }

    def _generate_visualization_prompt(self, analysis: ReportAnalysis) -> str:
        """Generate a text prompt for FIBO visualization"""
        
        organs_str = ", ".join(analysis.organs) if analysis.organs else "affected area"
        conditions_str = ", ".join(analysis.conditions) if analysis.conditions else "medical condition"
        
        prompt = f"Medical visualization of {organs_str} showing {conditions_str}"
        
        if analysis.severity:
            prompt += f" with {analysis.severity} severity"
        
        if analysis.findings:
            key_finding = analysis.findings[0] if analysis.findings else ""
            if key_finding:
                prompt += f", highlighting {key_finding}"
        
        return prompt

    async def _get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get report data from CSV"""
        try:
            with open(self.reports_csv, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['id'] == report_id:
                        return row
        except Exception:
            pass
        return None

    async def _update_report_analysis(
        self, 
        report_id: str, 
        analysis: ReportAnalysis,
        fibo_params: Dict[str, Any]
    ):
        """Update report CSV with analysis results"""
        rows = []
        with open(self.reports_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['id'] == report_id:
                    row['processed_status'] = 'completed'
                    row['analysis_result'] = analysis.summary
                    row['gemini_analysis'] = json.dumps({
                        "conditions": analysis.conditions,
                        "severity": analysis.severity,
                        "organs": analysis.organs,
                        "findings": analysis.findings
                    })
                    row['fibo_parameters'] = json.dumps(fibo_params)
                rows.append(row)
        
        with open(self.reports_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    async def get_all_reports(self, patient_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all reports, optionally filtered by patient"""
        reports = []
        try:
            with open(self.reports_csv, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if patient_id is None or row['patient_id'] == patient_id:
                        reports.append(row)
        except Exception:
            pass
        return reports

    async def get_report_with_analysis(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get report with parsed analysis"""
        report = await self._get_report(report_id)
        if report:
            # Parse JSON fields
            if report.get('gemini_analysis'):
                try:
                    report['gemini_analysis_parsed'] = json.loads(report['gemini_analysis'])
                except:
                    report['gemini_analysis_parsed'] = {}
            if report.get('fibo_parameters'):
                try:
                    report['fibo_parameters_parsed'] = json.loads(report['fibo_parameters'])
                except:
                    report['fibo_parameters_parsed'] = {}
        return report


# Singleton instance
report_service: Optional[ReportService] = None


def get_report_service() -> ReportService:
    """Get or create the singleton report service instance"""
    global report_service
    if report_service is None:
        report_service = ReportService()
    return report_service
