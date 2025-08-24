"""
Tests for the main FastAPI application
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_api_info():
    """Test the API info endpoint"""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Resume Screening API"
    assert data["version"] == "1.0.0"
    assert "/api/upload-resume" in data["endpoints"]

def test_upload_resume_missing_file():
    """Test upload endpoint with missing file"""
    response = client.post("/api/upload-resume", data={"job_description": "Test job"})
    assert response.status_code == 422  # Validation error

def test_upload_resume_missing_description():
    """Test upload endpoint with missing job description"""
    # Create a mock file
    files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
    response = client.post("/api/upload-resume", files=files)
    assert response.status_code == 422  # Validation error

def test_upload_resume_wrong_file_type():
    """Test upload endpoint with wrong file type"""
    files = {"file": ("test.txt", b"text content", "text/plain")}
    data = {"job_description": "Software Engineer position"}
    response = client.post("/api/upload-resume", files=files, data=data)
    assert response.status_code == 200  # API accepts but returns error
    data = response.json()
    assert data["status"] == "error"
    assert "not supported" in data["message"]

def test_upload_resume_success():
    """Test successful resume upload (mock PDF)"""
    # Create a mock PDF file with proper PDF header
    pdf_content = b'%PDF-1.4\n%fake pdf content for testing'
    files = {"file": ("test.pdf", pdf_content, "application/pdf")}
    data = {"job_description": "Software Engineer position with Python and React skills"}
    
    # Mock the PDF extraction functions
    with patch('app.main.extract_text_from_pdf') as mock_extract:
        mock_extract.return_value = {
            "text": "John Doe\nSoftware Engineer\nPython, React, Node.js\n5 years experience",
            "pages": 1,
            "error": None,
            "extraction_time": 0.1,
            "file_size": 1024
        }
        
        response = client.post("/api/upload-resume", files=files, data=data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Resume processed successfully" in data["message"]
        assert "extraction_data" in data
