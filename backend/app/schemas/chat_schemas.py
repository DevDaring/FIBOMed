"""Chat-related Pydantic schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatMessageRequest(BaseModel):
    """Request schema for text chat message"""

    message: str = Field(..., description="User's message text")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    enable_tts: bool = Field(True, description="Enable text-to-speech for response")
    medical_context: Optional[str] = Field(None, description="Additional medical context")
    language_code: Optional[str] = Field(None, description="Language code (e.g., 'en-US', 'hi-IN')")


class VoiceChatRequest(BaseModel):
    """Request schema for voice chat (multipart form data)"""

    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    enable_tts: bool = Field(True, description="Enable text-to-speech for response")
    medical_context: Optional[str] = Field(None, description="Additional medical context")
    language_code: Optional[str] = Field(None, description="Language code for STT")


class ChatResponse(BaseModel):
    """Response schema for chat"""

    transcription: Optional[str] = Field(None, description="Transcribed user input (for voice)")
    response: str = Field(..., description="Bot's response text")
    audio_url: Optional[str] = Field(None, description="URL to generated audio response")
    session_id: str = Field(..., description="Session ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class SessionClearRequest(BaseModel):
    """Request to clear a chat session"""

    session_id: str = Field(..., description="Session ID to clear")


class ChatHistoryRequest(BaseModel):
    """Request to get chat history"""

    session_id: str = Field(..., description="Session ID")
    limit: Optional[int] = Field(50, description="Number of messages to retrieve")
    offset: Optional[int] = Field(0, description="Offset for pagination")


class ChatMessageDB(BaseModel):
    """Chat message for database storage"""

    id: str
    session_id: str
    user_message: str
    bot_response: str
    transcription: Optional[str] = None
    audio_url: Optional[str] = None
    timestamp: datetime
    language_code: Optional[str] = None
