from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from database import get_database
from routers import auth, study_tasks, summaries, quizzes, chat, user, progress, upload
from middleware.auth import get_current_user
from models.user import User

# Load environment variables
load_dotenv()

# Global database connection
database = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global database
    database = await get_database()
    yield
    # Shutdown
    if database:
        database.client.close()

# Create FastAPI app
app = FastAPI(
    title="StudyBuddy API",
    description="Backend API for StudyBuddy MVP - AI-powered study assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly for production
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(study_tasks.router, prefix="/api/study-tasks", tags=["Study Tasks"])
app.include_router(summaries.router, prefix="/api/summaries", tags=["Summaries"])
app.include_router(quizzes.router, prefix="/api/quizzes", tags=["Quizzes"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])

@app.get("/")
async def root():
    return {
        "message": "StudyBuddy API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "OK",
        "database": "connected" if database else "disconnected",
        "version": "1.0.0"
    }

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "success": False,
        "error": exc.detail,
        "status_code": exc.status_code
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 3001)),
        reload=os.getenv("NODE_ENV", "development") == "development"
    )

