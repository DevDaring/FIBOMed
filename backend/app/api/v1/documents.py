"""Document Upload API endpoints - Using Agentic Document Processing"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from datetime import datetime
import uuid
import csv
import os

from ...services.document_agent import document_agent, DocumentType
from ...services.fibo_service import get_fibo_service
from ...config import settings
from ...core.exceptions import DocumentProcessingError
from ...database.csv_manager import csv_manager

router = APIRouter()


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(..., description="PDF or image file"),
    session_id: Optional[str] = Form(None),
    user_id: str = Form(..., description="User ID"),
):
    """
    Upload and process a medical document using 3-step AI agent pipeline.
    
    Pipeline:
    1. CLASSIFY: Determine if text report or medical image
    2. ANALYZE: Extract content and understand the document
    3. GENERATE: Create BOTH explanation AND FIBO visualization
    
    Returns both explanation and generated visualization for ALL document types.
    """
    try:
        # Validate file type
        allowed_types = ['application/pdf', 'image/png', 'image/jpeg', 'image/webp', 'image/gif']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: PDF, PNG, JPEG, WebP, GIF"
            )
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Read file content
        file_content = await file.read()
        
        # Process document through agent pipeline
        result = await document_agent.process_document(
            file_content=file_content,
            filename=file.filename,
            mime_type=file.content_type,
            session_id=session_id,
            user_id=user_id,
        )
        
        # Save to CSV
        await _save_document_record(result)
        
        # Build response
        response_data = {
            "doc_id": result.doc_id,
            "filename": result.filename,
            "file_type": result.file_type,
            "document_type": result.document_type.value,
            "extracted_text": result.extracted_text,
            "explanation": result.explanation,
            "fibo_prompt": result.fibo_prompt,
            "is_medical_image": result.document_type == DocumentType.MEDICAL_IMAGE,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "agent_steps": [
                {"step": s.step_name, "model": s.model_used, "timestamp": s.timestamp}
                for s in result.agent_steps
            ]
        }
        
        # ALWAYS generate FIBO visualization (for both text and image documents)
        visualization_url = None
        visualization_id = None
        try:
            fibo_svc = get_fibo_service()
            fibo_result = await fibo_svc.generate_visualization(
                prompt=result.fibo_prompt,
                aspect_ratio="1:1",
                session_id=session_id,
            )
            visualization_url = fibo_result.image_url
            visualization_id = fibo_result.visualization_id
            response_data["visualization"] = {
                "image_url": visualization_url,
                "visualization_id": visualization_id,
                "prompt_used": result.fibo_prompt[:200]
            }
        except Exception as e:
            response_data["visualization_error"] = str(e)
            response_data["visualization"] = None
        
        # Save document upload as chat message for history
        try:
            # Message 1: Document upload with extracted content
            doc_msg_id = str(uuid.uuid4())
            doc_response = f"Document Type: {result.document_type.value}\n\nExtracted Content:\n{result.extracted_text[:500]}"
            await csv_manager.save_chat_message(
                message_id=doc_msg_id,
                session_id=session_id,
                user_message=f"[DOC_UPLOAD:{result.filename}]",
                bot_response=doc_response,
            )
            
            # Message 2: AI Explanation
            if result.explanation:
                explain_msg_id = str(uuid.uuid4())
                await csv_manager.save_chat_message(
                    message_id=explain_msg_id,
                    session_id=session_id,
                    user_message="[AI_ANALYSIS]",
                    bot_response=result.explanation,
                )
            
            # Message 3: Visualization (if generated)
            if visualization_url:
                viz_msg_id = str(uuid.uuid4())
                await csv_manager.save_chat_message(
                    message_id=viz_msg_id,
                    session_id=session_id,
                    user_message=f"[VISUALIZATION:{visualization_id}]",
                    bot_response=f"Generated visualization: {visualization_url}",
                )
        except Exception as e:
            print(f"Warning: Failed to save document to chat history: {e}")
        
        return response_data
        
    except DocumentProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


async def _save_document_record(result):
    """Save document record to CSV"""
    csv_path = os.path.join(settings.CSV_DATA_PATH, "uploaded_documents.csv")
    
    # Ensure file exists with headers
    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'session_id', 'user_id', 'filename', 'file_type',
                'document_type', 'extracted_text', 'explanation', 'fibo_prompt', 'created_at'
            ])
    
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            result.doc_id,
            result.session_id,
            result.user_id,
            result.filename,
            result.file_type,
            result.document_type.value,
            result.extracted_text[:500],  # Truncate for CSV
            result.explanation[:500],
            result.fibo_prompt[:200],
            result.created_at,
        ])


@router.get("/documents/session/{session_id}")
async def get_session_documents(session_id: str):
    """Get all documents for a session"""
    try:
        csv_path = os.path.join(settings.CSV_DATA_PATH, "uploaded_documents.csv")
        documents = []
        
        if os.path.exists(csv_path):
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('session_id') == session_id:
                        documents.append(row)
        
        return {"session_id": session_id, "documents": documents}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")
