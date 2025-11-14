"""Chat API endpoints with voice support"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime
import uuid

from ...schemas.chat_schemas import (
    ChatMessageRequest,
    ChatResponse,
    SessionClearRequest,
)
from ...services.chat_service import chat_service
from ...database.csv_manager import csv_manager
from ...core.exceptions import VoiceProcessingError, GeminiError

router = APIRouter()


@router.post("/chat/text", response_model=ChatResponse)
async def chat_text(request: ChatMessageRequest):
    """
    Process a text chat message

    - Sends message to Gemini Flash
    - Optionally generates TTS audio response
    - Stores conversation in CSV database
    """
    try:
        # Process the message
        result = await chat_service.process_text_message(
            message=request.message,
            session_id=request.session_id,
            enable_tts=request.enable_tts,
            medical_context=request.medical_context,
        )

        # Save to database
        message_id = str(uuid.uuid4())
        await csv_manager.save_chat_message(
            message_id=message_id,
            session_id=result["session_id"],
            user_message=request.message,
            bot_response=result["response"],
            audio_url=result.get("audio_url"),
            language_code=request.language_code,
        )

        return ChatResponse(
            response=result["response"],
            audio_url=result.get("audio_url"),
            session_id=result["session_id"],
            timestamp=datetime.utcnow(),
        )

    except GeminiError as e:
        raise HTTPException(status_code=500, detail=f"AI response generation failed: {str(e)}")
    except VoiceProcessingError as e:
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.post("/chat/voice", response_model=ChatResponse)
async def chat_voice(
    audio: UploadFile = File(..., description="Audio file (WebM, OGG, WAV, etc.)"),
    session_id: Optional[str] = Form(None),
    enable_tts: bool = Form(True),
    medical_context: Optional[str] = Form(None),
    language_code: Optional[str] = Form(None),
):
    """
    Process a voice chat message

    - Converts speech to text (Google STT)
    - Sends text to Gemini Flash
    - Converts response to speech (Google TTS)
    - Stores conversation in CSV database
    """
    try:
        # Read audio file content
        audio_content = await audio.read()

        # Process the voice message
        result = await chat_service.process_voice_message(
            audio_content=audio_content,
            session_id=session_id,
            language_code=language_code,
            enable_tts=enable_tts,
            medical_context=medical_context,
        )

        # Save to database
        message_id = str(uuid.uuid4())
        await csv_manager.save_chat_message(
            message_id=message_id,
            session_id=result["session_id"],
            user_message=result["transcription"],
            bot_response=result["response"],
            transcription=result["transcription"],
            audio_url=result.get("audio_url"),
            language_code=language_code,
        )

        return ChatResponse(
            transcription=result["transcription"],
            response=result["response"],
            audio_url=result.get("audio_url"),
            session_id=result["session_id"],
            timestamp=datetime.utcnow(),
        )

    except VoiceProcessingError as e:
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")
    except GeminiError as e:
        raise HTTPException(status_code=500, detail=f"AI response generation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.post("/chat/session/clear")
async def clear_session(request: SessionClearRequest):
    """Clear a chat session"""
    try:
        chat_service.clear_session(request.session_id)
        return {"message": "Session cleared successfully", "session_id": request.session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear session: {str(e)}")


@router.get("/chat/session/{session_id}/history")
async def get_chat_history(session_id: str, limit: int = 50, offset: int = 0):
    """Get chat history for a session"""
    try:
        messages = await csv_manager.get_chat_history(session_id, limit, offset)
        return {"session_id": session_id, "messages": messages, "count": len(messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")
