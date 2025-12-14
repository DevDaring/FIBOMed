"""
Document Processing Agent - Agentic framework for medical document analysis
Uses 3-step AI pipeline:
1. Classify document type (text report vs medical image)
2. Decide processing action based on type
3. Generate explanation + FIBO visualization prompt
"""
import os
import uuid
import base64
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import google.generativeai as genai

from ..config import settings
from ..core.exceptions import DocumentProcessingError

# Configure Gemini with API key
genai.configure(api_key=settings.GEMINI_API_KEY)


class DocumentType(Enum):
    TEXT_REPORT = "text_report"
    MEDICAL_IMAGE = "medical_image"
    UNKNOWN = "unknown"


@dataclass
class AgentStep:
    """Represents a single step in the agent pipeline"""
    step_name: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    model_used: str
    timestamp: str


@dataclass
class DocumentAnalysisResult:
    """Final result from document analysis agent"""
    doc_id: str
    filename: str
    file_type: str
    document_type: DocumentType
    extracted_text: str
    explanation: str
    fibo_prompt: str
    fibo_parameters: Dict[str, Any]
    agent_steps: list
    session_id: str
    user_id: str
    created_at: str


class DocumentProcessingAgent:
    """
    Agentic document processor with 3-step AI pipeline.
    Always generates both explanation AND FIBO visualization.
    """
    
    def __init__(self):
        # Use Gemini 2.5 Flash model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.upload_dir = os.path.join(settings.UPLOAD_PATH, "documents")
        os.makedirs(self.upload_dir, exist_ok=True)
        self.agent_steps: list = []
    
    async def process_document(
        self,
        file_content: bytes,
        filename: str,
        mime_type: str,
        session_id: str,
        user_id: str,
    ) -> DocumentAnalysisResult:
        """
        Main entry point - processes document through 3-step AI pipeline.
        
        Pipeline:
        1. CLASSIFY: Determine if text report or medical image
        2. ANALYZE: Extract content and decide processing approach
        3. GENERATE: Create explanation + FIBO visualization prompt
        """
        self.agent_steps = []
        
        # Save file first
        doc_id = str(uuid.uuid4())
        file_ext = os.path.splitext(filename)[1].lower()
        saved_filename = f"{doc_id}{file_ext}"
        file_path = os.path.join(self.upload_dir, saved_filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Determine basic file type
        is_pdf = mime_type == 'application/pdf' or file_ext == '.pdf'
        is_image = mime_type.startswith('image/') or file_ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif']
        file_type = "pdf" if is_pdf else "image" if is_image else "unknown"
        
        try:
            # STEP 1: Classify document
            doc_type, classification_info = await self._step1_classify(
                file_content, mime_type, is_pdf
            )
            
            # STEP 2: Analyze and extract content
            extracted_text, analysis_info = await self._step2_analyze(
                file_content, mime_type, is_pdf, doc_type
            )
            
            # STEP 3: Generate explanation AND FIBO prompt (always both)
            explanation, fibo_prompt, fibo_params = await self._step3_generate(
                extracted_text, doc_type, analysis_info
            )
            
            return DocumentAnalysisResult(
                doc_id=doc_id,
                filename=filename,
                file_type=file_type,
                document_type=doc_type,
                extracted_text=extracted_text,
                explanation=explanation,
                fibo_prompt=fibo_prompt,
                fibo_parameters=fibo_params,
                agent_steps=self.agent_steps,
                session_id=session_id,
                user_id=user_id,
                created_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            raise DocumentProcessingError(f"Agent processing failed: {str(e)}")
    
    async def _step1_classify(
        self,
        file_content: bytes,
        mime_type: str,
        is_pdf: bool
    ) -> Tuple[DocumentType, Dict[str, Any]]:
        """
        STEP 1: Classify document type
        - Is it a text-based medical report (lab results, diagnosis, etc.)?
        - Is it a medical image (X-ray, CT, MRI, ultrasound, ECG)?
        """
        file_b64 = base64.b64encode(file_content).decode('utf-8')
        
        classify_prompt = """You are a medical document classifier. Analyze this document and classify it.

TASK: Determine if this is:
1. TEXT_REPORT - A text-based medical document (lab results, diagnosis report, prescription, medical notes, etc.)
2. MEDICAL_IMAGE - A medical imaging scan (X-ray, CT scan, MRI, ultrasound, ECG, pathology slide, etc.)

Respond ONLY with valid JSON:
{
    "document_type": "TEXT_REPORT" or "MEDICAL_IMAGE",
    "confidence": 0.0 to 1.0,
    "reasoning": "brief explanation of classification",
    "detected_elements": ["list", "of", "key", "elements", "found"]
}"""

        try:
            response = self.model.generate_content([
                classify_prompt,
                {"mime_type": mime_type if not is_pdf else "application/pdf", "data": file_b64}
            ])
            
            result_text = response.text.strip()
            # Extract JSON from response
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                classification = json.loads(result_text[json_start:json_end])
            else:
                classification = {"document_type": "TEXT_REPORT", "confidence": 0.5, "reasoning": "Default classification"}
            
            doc_type = DocumentType.MEDICAL_IMAGE if classification.get("document_type") == "MEDICAL_IMAGE" else DocumentType.TEXT_REPORT
            
            # Log step
            self.agent_steps.append(AgentStep(
                step_name="classify",
                input_data={"mime_type": mime_type, "is_pdf": is_pdf},
                output_data=classification,
                model_used="gemini-2.0-flash",
                timestamp=datetime.utcnow().isoformat()
            ))
            
            return doc_type, classification
            
        except Exception as e:
            # Default to text report on error
            return DocumentType.TEXT_REPORT, {"error": str(e)}
    
    async def _step2_analyze(
        self,
        file_content: bytes,
        mime_type: str,
        is_pdf: bool,
        doc_type: DocumentType
    ) -> Tuple[str, Dict[str, Any]]:
        """
        STEP 2: Analyze document and extract content
        - For TEXT_REPORT: Extract all text, identify medical terms, conditions
        - For MEDICAL_IMAGE: Describe what the image shows medically
        """
        file_b64 = base64.b64encode(file_content).decode('utf-8')
        
        if doc_type == DocumentType.MEDICAL_IMAGE:
            analyze_prompt = """You are a medical imaging expert. Analyze this medical image.

TASK: Provide detailed analysis of this medical image.

Respond with JSON:
{
    "image_type": "X-ray/CT/MRI/Ultrasound/ECG/Other",
    "body_region": "chest/abdomen/head/limb/heart/etc",
    "findings": ["list of medical findings"],
    "abnormalities": ["any abnormalities detected"],
    "severity": "normal/mild/moderate/severe",
    "description": "Detailed description of what the image shows for patient education",
    "medical_terms": ["relevant medical terminology"]
}"""
        else:
            analyze_prompt = """You are a medical document analyst. Extract and analyze this medical document.

TASK: Extract all text and identify key medical information.

Respond with JSON:
{
    "extracted_text": "Full text content from the document",
    "document_category": "lab_results/diagnosis/prescription/discharge_summary/other",
    "patient_info": "any patient identifiers (anonymized)",
    "conditions": ["medical conditions mentioned"],
    "findings": ["key findings or results"],
    "medications": ["any medications mentioned"],
    "recommendations": ["treatment recommendations if any"],
    "medical_terms": ["important medical terminology"]
}"""

        try:
            response = self.model.generate_content([
                analyze_prompt,
                {"mime_type": mime_type if not is_pdf else "application/pdf", "data": file_b64}
            ])
            
            result_text = response.text.strip()
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                analysis = json.loads(result_text[json_start:json_end])
            else:
                analysis = {"extracted_text": result_text, "error": "Could not parse JSON"}
            
            # Extract text based on document type
            if doc_type == DocumentType.MEDICAL_IMAGE:
                extracted_text = analysis.get("description", "") + "\n\nFindings: " + ", ".join(analysis.get("findings", []))
            else:
                extracted_text = analysis.get("extracted_text", result_text)
            
            # Log step
            self.agent_steps.append(AgentStep(
                step_name="analyze",
                input_data={"document_type": doc_type.value},
                output_data=analysis,
                model_used="gemini-2.0-flash",
                timestamp=datetime.utcnow().isoformat()
            ))
            
            return extracted_text, analysis
            
        except Exception as e:
            return f"Analysis error: {str(e)}", {"error": str(e)}
    
    async def _step3_generate(
        self,
        extracted_text: str,
        doc_type: DocumentType,
        analysis_info: Dict[str, Any]
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        STEP 3: Generate BOTH explanation AND FIBO visualization prompt
        This step ALWAYS produces both outputs regardless of document type.
        """
        generate_prompt = f"""You are a medical AI assistant helping patients understand their medical documents.

DOCUMENT TYPE: {doc_type.value}
EXTRACTED CONTENT: {extracted_text[:2000]}
ANALYSIS: {json.dumps(analysis_info, indent=2)[:1000]}

TASK: Generate TWO things:

1. PATIENT EXPLANATION: A clear, compassionate explanation of this medical document that a patient can understand. 
   - Use simple language
   - Explain medical terms
   - Highlight key findings
   - Mention any concerns or next steps

2. FIBO VISUALIZATION PROMPT: Create a SHORT, SIMPLE prompt for an educational anatomy illustration.
   
   CRITICAL RULES - THE PROMPT MUST FOLLOW THESE EXACTLY:
   - Maximum 30 words
   - ONLY describe healthy anatomy - NO medical conditions, NO abnormalities
   - Use ONLY these safe words: heart, lung, brain, kidney, liver, artery, vein, muscle, bone, organ
   - NEVER use: disease, stenosis, blockage, tumor, cancer, lesion, pathology, abnormal, damaged, blocked
   - Focus on: "anatomy diagram", "educational illustration", "medical diagram"
   - Style words: clean, soft colors, labeled, professional, educational
   
   GOOD EXAMPLES:
   - "Educational anatomy diagram of a healthy human heart showing chambers and coronary arteries, clean medical illustration style, soft colors"
   - "Professional medical illustration of human lungs and respiratory system, labeled anatomy diagram, soft blue tones"
   - "Clean educational diagram of the cardiovascular system showing heart and major blood vessels, professional medical style"
   
   BAD EXAMPLES (NEVER USE):
   - "Heart with blocked arteries" (blocked is forbidden)
   - "Coronary artery disease visualization" (disease is forbidden)
   - "Stenosis in the heart" (stenosis is forbidden)

Respond with JSON:
{{
    "explanation": "Patient-friendly explanation here...",
    "fibo_prompt": "Short safe anatomy illustration prompt - NO medical conditions, only healthy anatomy...",
    "visualization_focus": "main organ/body part",
    "organs_involved": ["list of organs/body parts"],
    "conditions_shown": [],
    "severity_level": "normal"
}}"""

        try:
            response = self.model.generate_content(generate_prompt)
            result_text = response.text.strip()
            
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                generation = json.loads(result_text[json_start:json_end])
            else:
                generation = {
                    "explanation": result_text,
                    "fibo_prompt": "Educational medical anatomy illustration, clean diagram style, soft colors, labeled parts",
                    "visualization_focus": "general",
                    "organs_involved": [],
                    "conditions_shown": [],
                    "severity_level": "unknown"
                }
            
            explanation = generation.get("explanation", "Unable to generate explanation")
            
            # IMPORTANT: Use hardcoded safe prompts instead of Gemini-generated ones
            # This guarantees the prompt will pass content moderation
            fibo_prompt = self._get_hardcoded_safe_prompt(extracted_text, analysis_info)
            
            # Build FIBO parameters
            fibo_params = self._build_fibo_parameters(generation, doc_type, analysis_info)
            
            # Log step
            self.agent_steps.append(AgentStep(
                step_name="generate",
                input_data={"doc_type": doc_type.value, "text_length": len(extracted_text)},
                output_data={"explanation_length": len(explanation), "fibo_prompt": fibo_prompt[:200]},
                model_used="gemini-2.0-flash",
                timestamp=datetime.utcnow().isoformat()
            ))
            
            return explanation, fibo_prompt, fibo_params
            
        except Exception as e:
            # Even on error, return a safe prompt
            safe_prompt = "Educational anatomy diagram of the human body, clean professional medical illustration, soft colors, labeled parts"
            return f"Error generating explanation: {str(e)}", safe_prompt, {}
    
    def _get_hardcoded_safe_prompt(self, extracted_text: str, analysis_info: Dict[str, Any]) -> str:
        """
        Get a hardcoded safe prompt based on detected content.
        These prompts are guaranteed to pass FIBO content moderation.
        """
        text_lower = extracted_text.lower()
        
        # Hardcoded safe prompts for different medical contexts
        safe_prompts = {
            # Cardiac/Heart
            "heart": "Educational anatomy diagram of a healthy human heart showing four chambers and coronary arteries, clean professional medical illustration style, soft warm colors, labeled anatomical parts",
            "cardiac": "Educational anatomy diagram of a healthy human heart showing four chambers and coronary arteries, clean professional medical illustration style, soft warm colors, labeled anatomical parts",
            "coronary": "Educational anatomy diagram of a healthy human heart showing coronary arteries and blood vessels, clean professional medical illustration style, soft colors, labeled parts",
            "echocardiogram": "Educational anatomy diagram of a healthy human heart showing four chambers valves and blood flow patterns, clean professional medical illustration style, soft colors",
            "echo": "Educational anatomy diagram of a healthy human heart showing four chambers valves and blood flow patterns, clean professional medical illustration style, soft colors",
            "atrium": "Educational anatomy diagram of a healthy human heart showing four chambers, clean professional medical illustration style, soft colors, labeled parts",
            "ventricle": "Educational anatomy diagram of a healthy human heart showing four chambers, clean professional medical illustration style, soft colors, labeled parts",
            "aorta": "Educational anatomy diagram of the human cardiovascular system showing heart and aorta, clean professional medical illustration style, soft colors",
            
            # Respiratory/Lung
            "lung": "Professional medical illustration of healthy human lungs and respiratory system, educational anatomy diagram, soft blue tones, labeled parts",
            "pulmonary": "Professional medical illustration of healthy human lungs and respiratory system, educational anatomy diagram, soft blue tones, labeled parts",
            "respiratory": "Professional medical illustration of healthy human lungs and respiratory system, educational anatomy diagram, soft blue tones, labeled parts",
            "bronchi": "Professional medical illustration of healthy human lungs showing bronchial tree, educational anatomy diagram, soft colors",
            "copd": "Professional medical illustration of healthy human lungs and respiratory system, educational anatomy diagram, soft blue tones, labeled parts",
            
            # Brain/Nervous
            "brain": "Clean educational diagram of the human brain showing major regions and structures, professional medical illustration style, soft colors, labeled anatomy",
            "neuro": "Clean educational diagram of the human brain showing major regions and structures, professional medical illustration style, soft colors, labeled anatomy",
            "cerebral": "Clean educational diagram of the human brain showing major regions and structures, professional medical illustration style, soft colors, labeled anatomy",
            
            # Digestive
            "liver": "Educational anatomy illustration of a healthy human liver, clean professional medical diagram style, soft colors, labeled parts",
            "stomach": "Educational anatomy illustration of the human digestive system, clean professional medical diagram style, soft colors, labeled parts",
            "intestine": "Educational anatomy illustration of the human digestive system, clean professional medical diagram style, soft colors, labeled parts",
            "digestive": "Educational anatomy illustration of the human digestive system, clean professional medical diagram style, soft colors, labeled parts",
            
            # Urinary
            "kidney": "Professional medical illustration of healthy human kidneys, educational anatomy diagram, soft colors, labeled parts",
            "renal": "Professional medical illustration of healthy human kidneys, educational anatomy diagram, soft colors, labeled parts",
            "bladder": "Professional medical illustration of the human urinary system, educational anatomy diagram, soft colors, labeled parts",
            
            # Blood/Vascular
            "blood": "Educational anatomy diagram of human circulatory system showing heart and blood vessels, clean professional medical illustration style, soft colors",
            "artery": "Educational anatomy diagram of human arteries and blood vessels, clean professional medical illustration style, soft colors, labeled parts",
            "vein": "Educational anatomy diagram of human veins and circulatory system, clean professional medical illustration style, soft colors, labeled parts",
            "vascular": "Educational anatomy diagram of human circulatory system, clean professional medical illustration style, soft colors, labeled parts",
            
            # Imaging types
            "x-ray": "Educational anatomy diagram of the human skeletal system, clean professional medical illustration style, soft colors, labeled parts",
            "xray": "Educational anatomy diagram of the human skeletal system, clean professional medical illustration style, soft colors, labeled parts",
            "ct": "Educational anatomy diagram of human internal organs, clean professional medical illustration style, soft colors, labeled parts",
            "mri": "Educational anatomy diagram of human internal organs, clean professional medical illustration style, soft colors, labeled parts",
            "ultrasound": "Educational anatomy diagram of human internal organs, clean professional medical illustration style, soft colors, labeled parts",
        }
        
        # Check for keywords in the text
        for keyword, prompt in safe_prompts.items():
            if keyword in text_lower:
                return prompt
        
        # Default safe prompt
        return "Educational anatomy diagram of the human body showing major organs, clean professional medical illustration style, soft colors, labeled anatomical parts"
    
    def _build_fibo_parameters(
        self,
        generation: Dict[str, Any],
        doc_type: DocumentType,
        analysis_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build structured FIBO parameters from generation output"""
        
        organs = generation.get("organs_involved", [])
        conditions = generation.get("conditions_shown", [])
        severity = generation.get("severity_level", "moderate")
        
        # Map severity to numeric
        severity_map = {"normal": 1, "mild": 3, "moderate": 5, "severe": 7, "critical": 9}
        severity_score = severity_map.get(severity.lower(), 5)
        
        # Determine organ system
        organ_system_map = {
            "heart": "cardiovascular", "coronary": "cardiovascular", "cardiac": "cardiovascular",
            "lung": "respiratory", "chest": "respiratory", "bronchi": "respiratory",
            "liver": "digestive", "stomach": "digestive", "intestine": "digestive",
            "kidney": "urinary", "bladder": "urinary",
            "brain": "nervous", "spine": "nervous",
            "pancreas": "endocrine", "thyroid": "endocrine"
        }
        
        primary_organ = organs[0] if organs else "body"
        primary_system = "general"
        for organ in organs:
            for key, system in organ_system_map.items():
                if key in organ.lower():
                    primary_system = system
                    primary_organ = organ
                    break
        
        return {
            "scene_type": "medical_visualization",
            "primary_subject": {
                "system": primary_system,
                "organ": primary_organ,
                "view": "anterior",
                "zoom_level": "focused"
            },
            "pathology": {
                "type": "condition_visualization",
                "severity": severity_score,
                "conditions": conditions
            },
            "style": {
                "complexity": "patient_friendly",
                "realism": "semi-realistic",
                "color_palette": "medical_standard",
                "annotations": True
            },
            "document_type": doc_type.value
        }


# Singleton instance
document_agent = DocumentProcessingAgent()
