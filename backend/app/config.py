"""Application Configuration"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    GEMINI_API_KEY: str
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # Server Configuration
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"
    SECRET_KEY: str
    JWT_SECRET: str

    # File Paths
    CSV_DATA_PATH: str = "./data/csv_files"
    UPLOAD_PATH: str = "./data/uploads"
    GENERATED_PATH: str = "./data/generated"

    # Feature Flags
    ENABLE_VOICE_CHAT: bool = True
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB

    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    # Google Cloud Speech Settings
    GOOGLE_SPEECH_LANGUAGE_CODE: str = "en-US"
    GOOGLE_TTS_LANGUAGE_CODE: str = "en-US"
    GOOGLE_TTS_VOICE_NAME: str = "en-US-Neural2-F"

    # Gemini Settings
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 2048

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
