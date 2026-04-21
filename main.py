# ===============================================
# app/main.py (FastAPI Application)
# ===============================================
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.database import initialize_database, check_database_connection
from app.AD import router as work_router

# Initialize FastAPI app
app = FastAPI(
    title="Productivity Tracker API",
    description="A comprehensive productivity tracking system with AI analysis",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(work_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting Productivity Tracker API...")

    if not check_database_connection():
        print("❌ Failed to connect to database")
        raise HTTPException(status_code=500, detail="Database connection failed")

    success = initialize_database()
    if not success:
        print("❌ Failed to initialize database")
        raise HTTPException(status_code=500, detail="Database initialization failed")

    print("✅ Database initialized successfully")
    print("📊 Productivity Tracker API is ready!")


@app.get("/")
async def serve_frontend():
    """Serve the frontend application"""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {
        "message": "Productivity Tracker API",
        "status": "running",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Productivity Tracker API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
