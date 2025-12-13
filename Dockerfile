# FIBOMed Dockerfile for GCP Cloud Run
# Multi-stage build: Node.js for frontend, Python for backend

# ============================================
# Stage 1: Build Frontend
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files first for better caching
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --silent

# Copy frontend source
COPY frontend/ ./

# Build the frontend for production
RUN npm run build

# ============================================
# Stage 2: Python Backend with Frontend Static Files
# ============================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    APP_ROOT=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy secrets directory (environment variables)
# Note: For production, use Cloud Run secrets or environment variables instead
COPY secrets/.env ./secrets/.env

# Copy initialization scripts
COPY scripts/ ./scripts/

# Create data directories for visualizations and storage
RUN mkdir -p \
    data/csv_files \
    data/generated/visualizations \
    data/generated/prompts \
    data/generated/audio \
    data/uploads/audio

# Copy CSV data files if they exist
COPY data/csv_files/ ./data/csv_files/

# Expose port 8000 for Cloud Run
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Set working directory to backend for running the app
WORKDIR /app/backend

# Run the FastAPI application with uvicorn
# Cloud Run sets PORT environment variable, default to 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
