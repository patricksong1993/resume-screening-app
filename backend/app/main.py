from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import tempfile
from .pdf_extractor import extract_text_from_pdf, validate_pdf_file
from .qwen_analyzer import analyze_resume_job_match_qwen
from datetime import datetime
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
import logging
import traceback
import sys
import json
import random
import hashlib


# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('resume_screening.log')
    ]
)

# Create logger
logger = logging.getLogger(__name__)

# Get static files path
static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "public")

app = Flask(__name__, static_folder=static_path, static_url_path='/static')

# Enable Flask debug logging
app.logger.setLevel(logging.DEBUG)

# Add request logging middleware
@app.before_request
def log_request_info():
    logger.info(f"🔍 REQUEST: {request.method} {request.url}")
    logger.info(f"📋 Headers: {dict(request.headers)}")
    if request.method in ['POST', 'PUT', 'PATCH']:
        logger.info(f"📦 Content-Type: {request.content_type}")
        logger.info(f"📊 Content-Length: {request.content_length}")
        if request.files:
            logger.info(f"📎 Files: {[f.filename for f in request.files.getlist('file')]}")
        if request.form:
            form_data = dict(request.form)
            # Don't log full job description content, just length
            if 'job_description' in form_data:
                form_data['job_description'] = f"[{len(form_data['job_description'])} chars]"
            logger.info(f"📝 Form data: {form_data}")

@app.after_request
def log_response_info(response):
    logger.info(f"✅ RESPONSE: {response.status_code} - {response.content_length or 0} bytes")
    return response

# CORS configuration for frontend communication
# For production, you might want to be more specific about allowed origins

# Get allowed origins from environment or use defaults
allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',') if os.getenv('ALLOWED_ORIGINS') else [
    "http://localhost:8000", 
    "http://127.0.0.1:8000", 
    "http://localhost:3000", 
    "http://127.0.0.1:3000"
]

# Add your deployed frontend URL here
# Example: "https://your-frontend-domain.com"
# You can also set ALLOWED_ORIGINS environment variable

CORS(app, 
     origins=allowed_origins,
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf'}

# Response cache configuration
CACHE_FOLDER = os.path.join(os.path.dirname(__file__), 'response_cache')
CACHE_FILE = os.path.join(CACHE_FOLDER, 'resume_responses.json')

# Ensure cache folder exists
os.makedirs(CACHE_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_cached_responses():
    """Load cached responses from file"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                responses = json.load(f)
                logger.debug(f"📂 Loaded {len(responses)} cached responses")
                return responses
        else:
            logger.debug("📂 No cache file found, starting with empty cache")
            return []
    except Exception as e:
        logger.error(f"❌ Error loading cached responses: {str(e)}")
        return []

def save_response_to_cache(response_data):
    """Save a successful response to cache"""
    try:
        # Load existing responses
        cached_responses = load_cached_responses()
        
        # Create a cache entry
        cache_entry = {
            'id': hashlib.md5(f"{response_data.get('candidate_name', '')}{response_data.get('filename', '')}{datetime.now().isoformat()}".encode()).hexdigest()[:8],
            'timestamp': datetime.now().isoformat(),
            'candidate_name': response_data.get('candidate_name', 'Unknown Candidate'),
            'filename': response_data.get('filename', 'unknown.pdf'),
            'match_score': response_data.get('match_score', 0),
            'summary': response_data.get('summary', 'No summary available'),
            'strengths': response_data.get('strengths', ['None identified']),
            'improvement_areas': response_data.get('improvement_areas', ['None identified']),
            'reasoning': response_data.get('reasoning', 'No reasoning provided'),
            'recommendation': response_data.get('recommendation', 'Unable to determine'),
            'processing_time': response_data.get('processing_time'),
            'processing_time_ms': response_data.get('processing_time_ms'),
        }
        
        # Add to cache
        cached_responses.append(cache_entry)
        
        # Keep only the last 100 responses to prevent file from growing too large
        if len(cached_responses) > 100:
            cached_responses = cached_responses[-100:]
        
        # Save back to file
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cached_responses, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved response to cache - Total cached: {len(cached_responses)}")
        logger.debug(f"💾 Cached entry: {cache_entry['candidate_name']} - {cache_entry['match_score']}%")
        
    except Exception as e:
        logger.error(f"❌ Error saving response to cache: {str(e)}")
        logger.error(traceback.format_exc())

def get_random_cached_response(filename):
    """Get a random cached response for mock mode"""
    try:
        cached_responses = load_cached_responses()
        
        if not cached_responses:
            logger.warning("⚠️ No cached responses available for mock mode")
            return None
        
        # Select a random response
        selected_response = random.choice(cached_responses)
        
        # Modify it to use the current filename and add some randomization
        mock_response = selected_response.copy()
        mock_response['filename'] = filename
        mock_response['timestamp'] = datetime.now().isoformat()
        
        # Add some variation to the score (±5 points)
        original_score = mock_response['match_score']
        variation = random.randint(-5, 5)
        mock_response['match_score'] = max(0, min(100, original_score + variation))
        
        # Add mock identifier to candidate name
        mock_response['candidate_name'] = f"Mock-{mock_response['candidate_name']}"
        
        logger.info(f"🎭 Using cached response for mock mode: {mock_response['candidate_name']} - {mock_response['match_score']}%")
        logger.debug(f"🎭 Original response ID: {selected_response.get('id', 'Unknown')}")
        
        return mock_response
        
    except Exception as e:
        logger.error(f"❌ Error getting random cached response: {str(e)}")
        logger.error(traceback.format_exc())
        return None

@app.route("/")
def read_root():
    """Serve the main HTML file"""
    index_path = os.path.join(static_path, "index.html")
    return send_file(index_path)



def process_single_file(file, job_description, mock=False):
    """
    Process a single resume file
    """
    thread_id = threading.current_thread().ident
    logger.info(f"🚀 [Thread-{thread_id}] Starting processing file: {file.filename}")
    
    try:
        logger.debug(f"📋 [Thread-{thread_id}] File details - Name: {file.filename}, Content-Type: {file.content_type}, Size: {file.content_length}")
        
        # Validate file type
        logger.debug(f"🔍 [Thread-{thread_id}] Validating file type...")
        if not file.content_type == "application/pdf":
            logger.warning(f"❌ [Thread-{thread_id}] Invalid file type: {file.content_type}")
            return {
                "status": "error",
                "message": f"File type {file.content_type} not supported. Please upload PDF files only.",
                "filename": file.filename
            }
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{threading.current_thread().ident}_{filename}")
        logger.debug(f"💾 [Thread-{thread_id}] Saving file to: {temp_path}")
        file.save(temp_path)
        logger.info(f"✅ [Thread-{thread_id}] File saved successfully")
        
        # Validate PDF file
        logger.debug(f"🔍 [Thread-{thread_id}] Validating PDF structure...")
        is_valid, error_msg = validate_pdf_file(temp_path)
        if not is_valid:
            logger.error(f"❌ [Thread-{thread_id}] PDF validation failed: {error_msg}")
            os.remove(temp_path)
            return {
                "status": "error",
                "message": f"Invalid PDF file: {error_msg}",
                "filename": filename
            }
        logger.info(f"✅ [Thread-{thread_id}] PDF validation passed")
        
        # Extract text from PDF
        logger.debug(f"📄 [Thread-{thread_id}] Extracting text from PDF...")
        extraction_result = extract_text_from_pdf(temp_path)
        
        if extraction_result.get("error"):
            logger.error(f"❌ [Thread-{thread_id}] Text extraction failed: {extraction_result['error']}")
            os.remove(temp_path)
            return {
                "status": "error",
                "message": f"Failed to extract text from PDF: {extraction_result['error']}",
                "filename": filename
            }
        
        # Analyze the extracted text with AI
        extracted_text = extraction_result["text"]
        text_length = len(extracted_text)
        logger.info(f"✅ [Thread-{thread_id}] Text extracted successfully - {text_length} characters")
        
        # Call AI for intelligent analysis
        try:
            if not mock:
                logger.info(f"🤖 [Thread-{thread_id}] Starting AI analysis with Qwen...")
                logger.debug(f"📊 [Thread-{thread_id}] Job description length: {len(job_description)} chars")
                logger.debug(f"📊 [Thread-{thread_id}] Resume text length: {text_length} chars")
                
                ai_analysis = analyze_resume_job_match_qwen(job_description, extracted_text)
                
                logger.info(f"✅ [Thread-{thread_id}] AI analysis completed successfully")
                logger.debug(f"📊 [Thread-{thread_id}] Analysis result - Candidate: {ai_analysis.get('candidate_name', 'Unknown')}, Score: {ai_analysis.get('match_score', 0)}")
            else:
                logger.info(f"🎭 [Thread-{thread_id}] Mock mode - attempting to use cached response")
                
                # Try to get a cached response first
                cached_response = get_random_cached_response(filename)
                
                if cached_response:
                    logger.info(f"✅ [Thread-{thread_id}] Using cached response: {cached_response['candidate_name']}")
                    ai_analysis = cached_response
                else:
                    logger.warning(f"⚠️ [Thread-{thread_id}] No cached responses available, using fallback mock data")
                    # Fallback mock data if no cache available
                    ai_analysis = {
                        'candidate_name': f'Test Candidate {filename}',
                        'match_score': 75 + (hash(filename) % 25), # Random score between 75-99
                        'reasoning': f"Mock analysis for {filename}",
                        'strengths': ['Mock strength 1', 'Mock strength 2'],
                        'improvement_areas': ['Mock improvement 1', 'Mock improvement 2'],
                        'recommendation': 'Strong Match',
                        'summary': f'Mock summary for {filename}',
                        'timestamp': datetime.now().isoformat(),
                        'error': None
                    }

        except Exception as e:
            logger.error(f"❌ [Thread-{thread_id}] AI analysis failed: {str(e)}")
            logger.error(f"🔍 [Thread-{thread_id}] Full traceback:")
            logger.error(traceback.format_exc())
            
            # Fallback to basic analysis if AI analysis fails
            ai_analysis = {
                'candidate_name': f'Unknown - {filename}',
                'match_score': 0,
                'summary': 'Failed to analyze',
                'strengths': ['None identified'],
                'improvement_areas': ['None identified'],
                'reasoning': 'No reasoning provided',
                'recommendation': 'Unable to determine',
                'error': str(e)
            }
        
        # Clean up temporary file
        logger.debug(f"🗑️ [Thread-{thread_id}] Cleaning up temporary file: {temp_path}")
        os.remove(temp_path)
        logger.info(f"✅ [Thread-{thread_id}] File processing completed successfully for: {filename}")
        
        result = {
            "status": "success",
            "filename": filename,
            "candidate_name": ai_analysis.get('candidate_name', f'No name - {filename}'),
            "match_score": ai_analysis.get('match_score', 0),
            "summary": ai_analysis.get('summary', 'No summary available'),
            "strengths": ai_analysis.get('strengths', ['None identified']),
            "improvement_areas": ai_analysis.get('improvement_areas', ['None identified']),
            "reasoning": ai_analysis.get('reasoning', 'No reasoning provided'),
            "recommendation": ai_analysis.get('recommendation', 'Unable to determine'),
            "timestamp": datetime.now().isoformat(),
            "processing_time": ai_analysis.get('processing_time'),
            "processing_time_ms": ai_analysis.get('processing_time_ms'),
            "timing_breakdown": ai_analysis.get('timing_breakdown'),
        }
        
        # Save successful real analysis results to cache (not mock results)
        if not mock and not ai_analysis.get('error'):
            logger.debug(f"💾 [Thread-{thread_id}] Saving successful result to cache")
            save_response_to_cache(result)
        elif mock:
            logger.debug(f"🎭 [Thread-{thread_id}] Mock result - not saving to cache")
        
        logger.debug(f"📊 [Thread-{thread_id}] Returning result: {result['candidate_name']} - {result['match_score']}%")
        return result

    except Exception as e:
        logger.error(f"❌ [Thread-{thread_id}] Unexpected error processing file {file.filename}: {str(e)}")
        logger.error(f"🔍 [Thread-{thread_id}] Full traceback:")
        logger.error(traceback.format_exc())
        
        # Clean up temporary file on error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            logger.debug(f"🗑️ [Thread-{thread_id}] Cleaning up temporary file after error: {temp_path}")
            os.remove(temp_path)
            
        return {
            "status": "error",
            "message": f"Error processing file: {str(e)}",
            "filename": file.filename
        }

@app.route("/api/upload-resume", methods=["POST"])
def upload_resume():
    """
    Upload resume files with job description for AI analysis
    Supports both single and multiple file uploads
    """
    logger.info("🚀 Starting upload_resume endpoint")
    
    try:
        # Check if files were uploaded
        if 'file' not in request.files:
            logger.warning("❌ No file field in request")
            return jsonify({
                "status": "error",
                "message": "No file uploaded"
            }), 400
        
        files = request.files.getlist('file')
        job_description = request.form.get('job_description', '')
        mock = request.form.get('mock', 'false').lower() == 'true'
        # mock = True
        
        logger.info(f"📊 Request details - Files: {len(files)}, Job desc length: {len(job_description)}, Mock: {mock}")
        logger.debug(f"📎 File names: {[f.filename for f in files]}")
        
        # Check if files were selected
        if not files or all(file.filename == '' for file in files):
            logger.warning("❌ No files selected or all filenames empty")
            return jsonify({
                "status": "error",
                "message": "No file selected"
            }), 400
        
        # Process files concurrently using ThreadPoolExecutor
        max_workers = min(len(files), 5)
        logger.info(f"🔄 Starting concurrent processing with {max_workers} workers for {len(files)} files")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all file processing tasks
            logger.debug("📋 Submitting all file processing tasks to thread pool")
            future_to_file = {
                executor.submit(process_single_file, file, job_description, mock): file 
                for file in files
            }
            
            logger.info(f"✅ All {len(files)} tasks submitted to thread pool")
            
            # Collect results as they complete
            results = []
            completed_count = 0
            for future in future_to_file:
                try:
                    result = future.result()
                    results.append(result)
                    completed_count += 1
                    logger.info(f"✅ Task {completed_count}/{len(files)} completed: {result.get('filename', 'Unknown')} - {result.get('status', 'Unknown')}")
                except Exception as e:
                    file = future_to_file[future]
                    completed_count += 1
                    logger.error(f"❌ Task {completed_count}/{len(files)} failed: {file.filename} - {str(e)}")
                    logger.error(f"🔍 Full traceback:")
                    logger.error(traceback.format_exc())
                    
                    results.append({
                        "status": "error",
                        "message": f"Error processing file: {str(e)}",
                        "filename": file.filename
                    })
        
        logger.info(f"🏁 All concurrent processing completed - {len(results)} results collected")
        
        # Separate successful and failed results
        successful_results = [r for r in results if r["status"] == "success"]
        failed_results = [r for r in results if r["status"] == "error"]
        
        logger.info(f"📊 Processing summary - Success: {len(successful_results)}, Failed: {len(failed_results)}")
        
        if not successful_results:
            logger.error("❌ All files failed to process")
            return jsonify({
                "status": "error",
                "message": "All files failed to process",
                "failed_files": failed_results
            }), 400
        
        # Sort successful results by match score (highest first)
        logger.debug("📊 Sorting results by match score")
        successful_results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        top_candidate = successful_results[0] if successful_results else None
        if top_candidate:
            logger.info(f"🏆 Top candidate: {top_candidate['candidate_name']} with {top_candidate['match_score']}% match")
        
        # Prepare response
        response = {
            "status": "success",
            "message": f"Processed {len(successful_results)} file(s) successfully",
            "total_files": len(files),
            "successful_files": len(successful_results),
            "failed_files": len(failed_results),
            "job_description": job_description,
            "results": successful_results,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add failed files info if any
        if failed_results:
            response["failed_results"] = failed_results
            logger.warning(f"⚠️ {len(failed_results)} files failed: {[f['filename'] for f in failed_results]}")
        
        # For backward compatibility, if only one file, return single result format
        if len(successful_results) == 1 and len(failed_results) == 0:
            logger.debug("📋 Single file result - using backward compatibility format")
            result = successful_results[0]
            response.update({
                "filename": result["filename"],
                "candidate_name": result["candidate_name"],
                "match_score": result["match_score"],
                "summary": result["summary"],
                "strengths": result["strengths"],
                "improvement_areas": result["improvement_areas"],
                "reasoning": result["reasoning"],
                "recommendation": result["recommendation"],
                "processing_time": result.get("processing_time"),
                "processing_time_ms": result.get("processing_time_ms"),
                "timing_breakdown": result.get("timing_breakdown"),
            })
        
        logger.info(f"✅ upload_resume endpoint completed successfully")
        logger.debug(f"📊 Response size: {len(str(response))} characters")
        
        return jsonify(response)

    except Exception as e:
        logger.error(f"❌ Unexpected error in upload_resume endpoint: {str(e)}")
        logger.error(f"🔍 Full traceback:")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "status": "error",
            "message": f"Error processing files: {str(e)}"
        }), 500

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    logger.debug("🏥 Health check endpoint called")
    return jsonify({
        "status": "healthy", 
        "service": "resume-screening-backend",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/info", methods=["GET"])
def get_info():
    """Get API information"""
    logger.debug("ℹ️ Info endpoint called")
    return jsonify({
        "name": "Resume Screening API",
        "version": "1.0.0",
        "description": "Flask-powered resume screening backend",
        "endpoints": [
            "/api/upload-resume",
            "/api/health",
            "/api/info",
            "/api/cache-status"
        ]
    })

@app.route("/api/cache-status", methods=["GET"])
def get_cache_status():
    """Get cache status and statistics"""
    logger.debug("📂 Cache status endpoint called")
    
    try:
        cached_responses = load_cached_responses()
        
        # Calculate some statistics
        if cached_responses:
            scores = [r.get('match_score', 0) for r in cached_responses]
            avg_score = sum(scores) / len(scores)
            
            # Count by recommendation types
            recommendations = {}
            for response in cached_responses:
                rec = response.get('recommendation', 'Unknown')
                recommendations[rec] = recommendations.get(rec, 0) + 1
        else:
            avg_score = 0
            recommendations = {}
        
        return jsonify({
            "status": "success",
            "cache_file": CACHE_FILE,
            "total_cached_responses": len(cached_responses),
            "average_match_score": round(avg_score, 2) if cached_responses else 0,
            "recommendations_breakdown": recommendations,
            "latest_responses": cached_responses[-5:] if cached_responses else [],  # Last 5 responses
            "cache_file_exists": os.path.exists(CACHE_FILE),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting cache status: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error getting cache status: {str(e)}"
        }), 500

if __name__ == "__main__":
    logger.info("🚀 Starting Resume Screening Backend Server")
    logger.info("📍 Server configuration:")
    logger.info(f"   - Host: 0.0.0.0")
    logger.info(f"   - Port: 8000")
    logger.info(f"   - Debug: True")
    logger.info(f"   - Static path: {static_path}")
    logger.info(f"   - Upload folder: {UPLOAD_FOLDER}")
    logger.info(f"   - Max content length: {app.config.get('MAX_CONTENT_LENGTH', 'Not set')}")
    logger.info(f"   - Cache folder: {CACHE_FOLDER}")
    logger.info(f"   - Cache file: {CACHE_FILE}")
    
    # Load and display cache status
    try:
        cached_responses = load_cached_responses()
        logger.info(f"📂 Cache status: {len(cached_responses)} responses cached")
        if cached_responses:
            logger.info(f"📊 Latest cached response: {cached_responses[-1].get('candidate_name', 'Unknown')} - {cached_responses[-1].get('match_score', 0)}%")
    except Exception as e:
        logger.warning(f"⚠️ Could not load cache status: {str(e)}")
    
    logger.info("🎯 Server ready to accept requests")
    logger.info("💡 Use mock=true parameter to use cached responses for testing")
    
    app.run(debug=True, host="0.0.0.0", port=8000)