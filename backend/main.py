"""FIBOMed FastAPI Backend Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.config import settings
from app.api.v1 import chat, health

# Create FastAPI app
app = FastAPI(
    title="FIBOMed API",
    description="Medical Visual Storytelling Platform with Voice Chat",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs(settings.CSV_DATA_PATH, exist_ok=True)
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_PATH, "audio"), exist_ok=True)
os.makedirs(settings.GENERATED_PATH, exist_ok=True)
os.makedirs(os.path.join(settings.GENERATED_PATH, "audio"), exist_ok=True)

# Mount static files
if os.path.exists(settings.GENERATED_PATH):
    app.mount("/generated", StaticFiles(directory=settings.GENERATED_PATH), name="generated")

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FIBOMed API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
