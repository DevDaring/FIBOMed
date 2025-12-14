"""FIBOMed FastAPI Backend Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.config import settings
from app.api.v1 import chat, health, fibo, reports, users, documents

# Create FastAPI app
app = FastAPI(
    title="FIBOMed API",
    description="Medical Visual Storytelling Platform with Voice Chat",
    version="1.0.0",
)

# Path to frontend build (for Docker deployment)
FRONTEND_BUILD_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

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
os.makedirs(os.path.join(settings.GENERATED_PATH, "visualizations"), exist_ok=True)
os.makedirs(os.path.join(settings.GENERATED_PATH, "prompts"), exist_ok=True)

# Mount static files
if os.path.exists(settings.GENERATED_PATH):
    app.mount("/generated", StaticFiles(directory=settings.GENERATED_PATH), name="generated")

# Mount visualizations directory for static file serving (Requirement 2.4)
visualizations_path = os.path.join(settings.GENERATED_PATH, "visualizations")
if os.path.exists(visualizations_path):
    app.mount("/visualizations", StaticFiles(directory=visualizations_path), name="visualizations")

# Create additional directories for full project
os.makedirs(os.path.join(settings.UPLOAD_PATH, "reports"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_PATH, "medical_images"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_PATH, "prescriptions"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_PATH, "documents"), exist_ok=True)

# Include routers (must be before catch-all route)
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(fibo.router, prefix="/api/v1", tags=["fibo"])
app.include_router(reports.router, prefix="/api/v1", tags=["reports"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])


@app.get("/")
async def root():
    """Root endpoint - serves frontend in production or API info in development"""
    if os.path.exists(FRONTEND_BUILD_PATH):
        return FileResponse(os.path.join(FRONTEND_BUILD_PATH, "index.html"))
    return {
        "message": "FIBOMed API",
        "version": "1.0.0",
        "docs": "/docs",
    }


# Serve frontend static files in production (Docker deployment)
# This must be at the end to not interfere with API routes
if os.path.exists(FRONTEND_BUILD_PATH):
    # Mount static assets directory
    assets_path = os.path.join(FRONTEND_BUILD_PATH, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
