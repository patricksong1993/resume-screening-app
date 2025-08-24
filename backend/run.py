#!/usr/bin/env python3
"""
Startup script for the Resume Screening Backend
"""
import uvicorn
from app.main import app
from app.deepseek_analyzer import DeepSeekAnalyzer

if __name__ == "__main__":
    print("🚀 Starting Resume Screening Backend...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🔍 Interactive API explorer at: http://localhost:8000/redoc")
    print("🏥 Health check at: http://localhost:8000/api/health")
    print("ℹ️  API info at: http://localhost:8000/api/info")
    print("\n" + "="*50)
    

    # The backend now serves both the API and the frontend

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
