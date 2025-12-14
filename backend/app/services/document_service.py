"""Document Processing Service - Extract text from PDFs and images using Gemini"""
import os
import uuid
import base64
from typing import Optional, Dict, Any
from datetime import datetime
import google.generativeai as genai
from ..config import settings
from ..core.exceptions import DocumentProcessingError

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class DocumentService:
    """Service for processing uploaded documents (PDF/images)"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.upload_dir = os.path.join(settings.UPLOAD_PATH, "documents")
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def process_document(
        self,
        file_content: bytes,
        filename: str,
        mime_type: str,
        session_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Process uploaded document - extract text and determine if medical image
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            mime_type: MIME type of file
            session_id: Chat session ID
            user_id: User ID
            
        Returns:
            Dict with extracted_text, is_medical_image, file_path, etc.
        """
        try:
            # Generate unique ID and save file
            doc_id = str(uuid.uuid4())
            file_ext = os.path.splitext(filename)[1].lower()
            saved_filename = f"{doc_id}{file_ext}"
            file_path = os.path.join(self.upload_dir, saved_filename)
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Determine file type
            is_pdf = mime_type == 'application/pdf' or file_ext == '.pdf'
            is_image = mime_type.startswith('image/') or file_ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif']
            
            # Extract text using Gemini Vision
            extracted_text, is_medical_image = await self._extract_with_gemini(
                file_content, mime_type, is_pdf
            )
            
            return {
                "doc_id": doc_id,
                "filename": filename,
                "file_type": "pdf" if is_pdf else "image",
                "file_path": f"/uploads/documents/{saved_filename}",
                "extracted_text": extracted_text,
                "is_medical_image": is_medical_image,
                "session_id": session_id,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            raise DocumentProcessingError(f"Failed to process document: {str(e)}")
    
    async def _extract_with_gemini(
        self,
        file_content: bytes,
        mime_type: str,
        is_pdf: bool
    ) -> tuple[str, bool]:
        """Extract text from document using Gemini Vision"""
        try:
            # Encode file to base64
            file_b64 = base64.b64encode(file_content).decode('utf-8')
            
            # Create prompt for extraction
            extraction_prompt = """Analyze this document and provide:
1. Extract ALL text content from this document/image
2. Determine if this is a medical image (X-ray, CT scan, MRI, ultrasound, ECG, etc.)

Respond in this exact format:
EXTRACTED_TEXT:
[All extracted text here]

IS_MEDICAL_IMAGE: [yes/no]

MEDICAL_IMAGE_DESCRIPTION: [If yes, describe what the medical image shows in detail for visualization purposes]
"""
            
            # Use Gemini to analyze
            response = self.model.generate_content([
                extraction_prompt,
                {
                    "mime_type": mime_type if not is_pdf else "application/pdf",
                    "data": file_b64
                }
            ])
            
            result_text = response.text
            
            # Parse response
            extracted_text = ""
            is_medical_image = False
            
            if "EXTRACTED_TEXT:" in result_text:
                parts = result_text.split("IS_MEDICAL_IMAGE:")
                extracted_text = parts[0].replace("EXTRACTED_TEXT:", "").strip()
                
                if len(parts) > 1:
                    remaining = parts[1].strip()
                    is_medical_image = remaining.lower().startswith("yes")
                    
                    # If medical image, append description to extracted text
                    if is_medical_image and "MEDICAL_IMAGE_DESCRIPTION:" in remaining:
                        desc_part = remaining.split("MEDICAL_IMAGE_DESCRIPTION:")[1].strip()
                        extracted_text = f"{extracted_text}\n\nMedical Image Analysis: {desc_part}"
            else:
                extracted_text = result_text
            
            return extracted_text, is_medical_image
            
        except Exception as e:
            raise DocumentProcessingError(f"Gemini extraction failed: {str(e)}")
    
    async def get_gemini_explanation(self, text: str) -> str:
        """Get Gemini explanation for extracted medical text"""
        try:
            prompt = f"""You are a medical AI assistant. Explain the following medical report/text in simple terms that a patient can understand. 
Highlight key findings, any concerns, and recommended next steps.

Medical Text:
{text}

Provide a clear, compassionate explanation:"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            raise DocumentProcessingError(f"Failed to generate explanation: {str(e)}")


# Singleton instance
document_service = DocumentService()
