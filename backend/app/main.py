from fastapi import FastAPI, File, Form, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import os
from .pdf_extractor import extract_text_from_pdf, validate_pdf_file
from .deepseek_analyzer import analyze_resume_job_match
import time
app = FastAPI(
    title="Resume Screening API",
    description="AI-powered resume screening backend",
    version="1.0.0"
)

@app.get("/")
async def read_root():
    """Serve the main HTML file"""
    from fastapi.responses import FileResponse
    static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "public", "index.html")
    return FileResponse(static_path)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files from the parent directory's public folder
static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "public")
app.mount("/static", StaticFiles(directory=static_path, html=True), name="static")

@app.post("/api/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    mock: bool = Form(False)
):
    """
    Upload a resume file with job description for AI analysis
    """
    # Validate file type - focus on PDF for now
    if file.content_type != "application/pdf":
        return {
            "status": "error",
            "message": f"File type {file.content_type} not supported. Please upload PDF files only."
        }
    
    # Validate file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        return {
            "status": "error", 
            "message": "File too large. Maximum size is 10MB."
        }
    
    # Save uploaded file temporarily
    temp_dir = "/tmp"
    temp_path = os.path.join(temp_dir, f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
    
    try:
        # Save the uploaded file
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Validate PDF file
        is_valid, error_msg = validate_pdf_file(temp_path)
        if not is_valid:
            os.remove(temp_path)
            return {
                "status": "error",
                "message": f"Invalid PDF file: {error_msg}"
            }
        
        # Extract text from PDF
        extraction_result = extract_text_from_pdf(temp_path)
        
        if extraction_result.get("error"):
            os.remove(temp_path)
            return {
                "status": "error",
                "message": f"Failed to extract text from PDF: {extraction_result['error']}"
            }
        
        # Analyze the extracted text with DeepSeek AI
        extracted_text = extraction_result["text"]
        text_length = len(extracted_text)
        pages = extraction_result["pages"]
        
        # Basic text analysis
        words = extracted_text.split()
        word_count = len(words)

        # Call DeepSeek AI for intelligent analysis
        try:
            if not mock:
                ai_analysis = analyze_resume_job_match(job_description, extracted_text)
            else:
                ai_analysis = {'match_score': 35, 'reasoning': "The candidate has relevant software engineering experience at reputable tech companies (Stripe, Netflix) and demonstrates technical skills in modern development practices. However, there are significant gaps in meeting the specific requirements of this role. The resume shows no evidence of Python programming proficiency (a required qualification), no experience with financial services or trading environments, no mention of interest rate derivatives or yield curve construction knowledge, and no front-end technology experience with React/TypeScript or Python/ENAML. The candidate's experience appears to be primarily in data engineering rather than the trading desk application development focus required for this role. The lack of financial domain knowledge and specific technical stack alignment significantly reduces the match score.", 'strengths': ['Experience at reputable tech companies (Stripe, Netflix)', 'Background in developing scalable applications', 'Familiarity with modern development practices and cloud technologies', 'Experience with cross-functional collaboration', 'Knowledge of system performance optimization'], 'improvement_areas': ['No demonstrated Python programming experience (required qualification)', 'No financial services or trading environment experience', 'No knowledge of interest rate derivatives or yield curve construction', 'No front-end development experience with React/TypeScript or Python/ENAML', 'No evidence of trading desk interaction or support experience', 'Limited information about agile methodologies and CI/CD practices', 'No mention of quantitative research collaboration experience'], 'recommendation': 'Weak Match', 'summary': 'Candidate has strong general software engineering background but lacks the specific financial domain knowledge, Python expertise, and trading desk application experience required for this specialized role in rates marking and pricing.', 'timestamp': '2025-08-23T21:14:51.712759', 'error': None}

        except Exception as e:
            print(e)
            # Fallback to basic analysis if AI analysis fails
            analysis_result = "Failed to analyze"
        
        # Clean up temporary file
        os.remove(temp_path)
        
        response = {
            "status": "success",
            "message": "Resume processed successfully",
            "filename": file.filename,
            "job_description": job_description,
            "match_score": ai_analysis.get('match_score', 0),
            "summary": ai_analysis.get('summary', 'No summary available'),
            "strengths": ai_analysis.get('strengths', ['None identified']),
            "improvement_areas": ai_analysis.get('improvement_areas', ['None identified']),
            "reasoning": ai_analysis.get('reasoning', 'No reasoning provided'),
            "recommendation": ai_analysis.get('recommendation', 'Unable to determine'),
            "extraction_data": extraction_result,
            "timestamp": datetime.now().isoformat()
        }
        print(response['match_score'])
        print(response['summary'])
        return response


    except Exception as e:
        # Clean up temporary file on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return {
            "status": "error",
            "message": f"Error processing file: {str(e)}"
        }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "resume-screening-backend",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/analyze-resume")
async def analyze_resume_only(
    job_description: str = Form(...),
    resume_text: str = Form(...)
):
    """
    Analyze resume text against job description using DeepSeek AI
    (without file upload, just text analysis)
    """
    try:
        # Call DeepSeek AI for analysis
        ai_analysis = analyze_resume_job_match(job_description, resume_text)
        
        return {
            "status": "success",
            "message": "Resume analysis completed",
            "job_description": job_description,
            "resume_text_preview": resume_text[:200] + "..." if len(resume_text) > 200 else resume_text,
            "ai_analysis": ai_analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/info")
async def get_info():
    """Get API information"""
    return {
        "name": "Resume Screening API",
        "version": "1.0.0",
        "description": "AI-powered resume screening backend",
        "endpoints": [
            "/api/upload-resume",
            "/api/analyze-resume",
            "/api/health",
            "/api/info"
        ]
    }
