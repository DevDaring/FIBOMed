"""Application Configuration"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


def get_project_root() -> Path:
    """
    Get the project root directory reliably across all environments.
    
    Works in:
    - Local development (running from backend/ or project root)
    - Docker container (WORKDIR /app/backend, secrets at /app/secrets)
    - Any other deployment scenario
    """
    # Method 1: Check for APP_ROOT environment variable (can be set in Docker/Cloud Run)
    if os.environ.get("APP_ROOT"):
        return Path(os.environ["APP_ROOT"])
    
    # Method 2: Use __file__ to find project root
    # __file__ = /path/to/project/backend/app/config.py
    # parent.parent.parent = /path/to/project
    config_file = Path(__file__).resolve()
    project_root = config_file.parent.parent.parent
    
    # Verify this is the correct root by checking for expected structure
    if (project_root / "secrets").exists() or (project_root / "backend").exists():
        return project_root
    
    # Method 3: Fallback for Docker where WORKDIR is /app/backend
    # In this case, __file__ = /app/backend/app/config.py
    # parent.parent.parent = /app
    if project_root.name == "app" or (project_root / "secrets" / ".env").exists():
        return project_root
    
    # Method 4: Try current working directory's parent structure
    cwd = Path.cwd()
    if cwd.name == "backend" and (cwd.parent / "secrets").exists():
        return cwd.parent
    if (cwd / "secrets").exists():
        return cwd
    
    # Default: use the calculated path
    return project_root


def get_env_file_path() -> str:
    """
    Get the path to the .env file, checking multiple possible locations.
    
    Priority:
    1. ENV_FILE environment variable (explicit override)
    2. secrets/.env relative to project root
    3. .env in project root (fallback)
    """
    # Check for explicit ENV_FILE path
    if os.environ.get("ENV_FILE"):
        env_path = Path(os.environ["ENV_FILE"])
        if env_path.exists():
            return str(env_path)
    
    project_root = get_project_root()
    
    # Primary location: secrets/.env
    secrets_env = project_root / "secrets" / ".env"
    if secrets_env.exists():
        return str(secrets_env)
    
    # Fallback: .env in project root
    root_env = project_root / ".env"
    if root_env.exists():
        return str(root_env)
    
    # Return the expected path even if it doesn't exist
    # (pydantic-settings will handle the missing file gracefully)
    return str(secrets_env)


# Calculate paths once at module load
PROJECT_ROOT = get_project_root()
SECRETS_ENV_PATH = get_env_file_path()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    GEMINI_API_KEY: str
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    FIBO_PROD_API_KEY: str

    # Server Configuration
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"
    SECRET_KEY: str = "default-secret-key"
    JWT_SECRET: str = "default-jwt-secret"

    # File Paths - use project root relative paths
    CSV_DATA_PATH: str = str(PROJECT_ROOT / "data" / "csv_files")
    UPLOAD_PATH: str = str(PROJECT_ROOT / "data" / "uploads")
    GENERATED_PATH: str = str(PROJECT_ROOT / "data" / "generated")

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
    GEMINI_MODEL_NAME: str = "gemini-1.5-flash"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 2048

    # FIBO API Settings
    FIBO_API_BASE_URL: str = "https://engine.prod.bria-api.com/v2"
    FIBO_TIMEOUT: int = 120
    FIBO_DEFAULT_ASPECT_RATIO: str = "1:1"
    FIBO_SYNC_MODE: bool = True

    class Config:
        env_file = SECRETS_ENV_PATH
        case_sensitive = True
        extra = "ignore"  # Allow extra env variables not defined in Settings


settings = Settings()
