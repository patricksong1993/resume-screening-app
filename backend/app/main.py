from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import tempfile
from .pdf_extractor import extract_text_from_pdf, validate_pdf_file
from .deepseek_analyzer import analyze_resume_job_match
from datetime import datetime
import requests


# Get static files path
static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "public")

app = Flask(__name__, static_folder=static_path, static_url_path='/static')

# CORS configuration for frontend communication
CORS(app, origins=[
    "http://localhost:8000", 
    "http://127.0.0.1:8000", 
    "http://localhost:3000", 
    "http://127.0.0.1:3000"
])

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def read_root():
    """Serve the main HTML file"""
    index_path = os.path.join(static_path, "index.html")
    return send_file(index_path)



@app.route("/api/upload-resume", methods=["POST"])
def upload_resume():
    """
    Upload a resume file with job description for AI analysis
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No file uploaded"
            }), 400
        
        file = request.files['file']
        job_description = request.form.get('job_description', '')
        mock = request.form.get('mock', 'false').lower() == 'true'
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({
                "status": "error",
                "message": "No file selected"
            }), 400
        
        # Validate file type
        if not file.content_type == "application/pdf":
            return jsonify({
                "status": "error",
                "message": f"File type {file.content_type} not supported. Please upload PDF files only."
            }), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
        file.save(temp_path)
        
        # Validate PDF file
        is_valid, error_msg = validate_pdf_file(temp_path)
        if not is_valid:
            os.remove(temp_path)
            return jsonify({
                "status": "error",
                "message": f"Invalid PDF file: {error_msg}"
            }), 400
        
        # Extract text from PDF
        extraction_result = extract_text_from_pdf(temp_path)
        
        if extraction_result.get("error"):
            os.remove(temp_path)
            return jsonify({
                "status": "error",
                "message": f"Failed to extract text from PDF: {extraction_result['error']}"
            }), 500
        
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
                ai_analysis = {
                    'candidate_name': 'John Doe',
                    'match_score': 35, 
                    'reasoning': "The candidate has relevant software engineering experience at reputable tech companies (Stripe, Netflix) and demonstrates technical skills in modern development practices. However, there are significant gaps in meeting the specific requirements of this role. The resume shows no evidence of Python programming proficiency (a required qualification), no experience with financial services or trading environments, no mention of interest rate derivatives or yield curve construction knowledge, and no front-end technology experience with React/TypeScript or Python/ENAML. The candidate's experience appears to be primarily in data engineering rather than the trading desk application development focus required for this role. The lack of financial domain knowledge and specific technical stack alignment significantly reduces the match score.", 
                    'strengths': ['Experience at reputable tech companies (Stripe, Netflix)', 'Background in developing scalable applications', 'Familiarity with modern development practices and cloud technologies', 'Experience with cross-functional collaboration', 'Knowledge of system performance optimization'], 
                    'improvement_areas': ['No demonstrated Python programming experience (required qualification)', 'No financial services or trading environment experience', 'No knowledge of interest rate derivatives or yield curve construction', 'No front-end development experience with React/TypeScript or Python/ENAML', 'No evidence of trading desk interaction or support experience', 'Limited information about agile methodologies and CI/CD practices', 'No mention of quantitative research collaboration experience'], 
                    'recommendation': 'Weak Match', 
                    'summary': 'Candidate has strong general software engineering background but lacks the specific financial domain knowledge, Python expertise, and trading desk application experience required for this specialized role in rates marking and pricing.', 
                    'timestamp': '2025-08-23T21:14:51.712759', 
                    'error': None
                }

        except Exception as e:
            print(e)
            # Fallback to basic analysis if AI analysis fails
            ai_analysis = {
                'match_score': 0,
                'summary': 'Failed to analyze',
                'strengths': ['None identified'],
                'improvement_areas': ['None identified'],
                'reasoning': 'No reasoning provided',
                'recommendation': 'Unable to determine',
                'error': str(e)
            }
        
        # Clean up temporary file
        os.remove(temp_path)
        
        response = {
            "status": "success",
            "message": "Resume processed successfully",
            "filename": filename,
            "job_description": job_description,
            "candidate_name": ai_analysis.get('candidate_name', 'No candidate name provided'),
            "match_score": ai_analysis.get('match_score', 0),
            "summary": ai_analysis.get('summary', 'No summary available'),
            "strengths": ai_analysis.get('strengths', ['None identified']),
            "improvement_areas": ai_analysis.get('improvement_areas', ['None identified']),
            "reasoning": ai_analysis.get('reasoning', 'No reasoning provided'),
            "recommendation": ai_analysis.get('recommendation', 'Unable to determine'),
            "extraction_data": extraction_result,
            "timestamp": datetime.now().isoformat()
        }
        return jsonify(response)

    except Exception as e:
        # Clean up temporary file on error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({
            "status": "error",
            "message": f"Error processing file: {str(e)}"
        }), 500

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "resume-screening-backend",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/analyze-resume", methods=["POST"])
def analyze_resume_only():
    """
    Analyze resume text against job description using DeepSeek AI
    (without file upload, just text analysis)
    """
    try:
        data = request.get_json() if request.is_json else request.form
        job_description = data.get('job_description', '')
        resume_text = data.get('resume_text', '')
        
        if not job_description or not resume_text:
            return jsonify({
                "status": "error",
                "message": "Both job_description and resume_text are required"
            }), 400
        
        # Call DeepSeek AI for analysis
        ai_analysis = analyze_resume_job_match(job_description, resume_text)
        
        return jsonify({
            "status": "success",
            "message": "Resume analysis completed",
            "job_description": job_description,
            "resume_text_preview": resume_text[:200] + "..." if len(resume_text) > 200 else resume_text,
            "ai_analysis": ai_analysis,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/api/info", methods=["GET"])
def get_info():
    """Get API information"""
    return jsonify({
        "name": "Resume Screening API",
        "version": "1.0.0",
        "description": "Flask-powered resume screening backend",
        "endpoints": [
            "/api/upload-resume",
            "/api/analyze-resume",
            "/api/health",
            "/api/info"
        ]
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)