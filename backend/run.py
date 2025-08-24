#!/usr/bin/env python3
"""
Startup script for the Resume Screening Backend
"""
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting Resume Screening Backend (Flask)...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🏥 Health check at: http://localhost:8000/api/health")
    print("ℹ️  API info at: http://localhost:8000/api/info")
    print("🌐 Frontend at: http://localhost:8000/")
    print("\n" + "="*50)
    
    # The backend now serves both the API and the frontend
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True  # Enable debug mode for development
    )
