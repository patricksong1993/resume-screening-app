# Resume Screening Backend

FastAPI backend for the AI-powered resume screening application.

## Features

- **File Upload**: Accepts PDF, DOC, DOCX resume files
- **Job Description**: Processes job descriptions with resumes
- **AI Analysis**: Mock AI processing with detailed results
- **Validation**: File type and size validation
- **CORS Support**: Configured for frontend communication
- **API Documentation**: Auto-generated with FastAPI

## Setup

### Prerequisites

- Python 3.8+
- Poetry (for dependency management)

### Installation

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Activate virtual environment**:
   ```bash
   poetry shell
   ```

## Running the Server

### Development Mode
```bash
poetry run python run.py
```

### Production Mode
```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST `/api/upload-resume`
Upload a resume file with job description.

**Form Data:**
- `file`: Resume file (PDF, DOC, DOCX)
- `job_description`: Text description of the job

**Response:**
```json
{
  "status": "success",
  "message": "Resume processed successfully",
  "filename": "resume.pdf",
  "job_description": "Software Engineer position...",
  "analysis_result": "Resume Analysis Complete!...",
  "timestamp": "2024-01-01T12:00:00"
}
```

### GET `/api/health`
Health check endpoint.

### GET `/api/info`
API information and available endpoints.

## Development

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI application
├── tests/               # Test files
├── pyproject.toml       # Poetry configuration
├── run.py              # Startup script
└── README.md           # This file
```

### Adding New Endpoints
1. Add new route functions in `app/main.py`
2. Import required dependencies
3. Add tests in `tests/` directory
4. Update API documentation

### Testing
```bash
poetry run pytest
```

### Code Formatting
```bash
poetry run black .
poetry run flake8
```

## Configuration

The server runs on port 8000 by default. You can modify this in `run.py`.

CORS is configured to allow requests from:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

## Future Enhancements

- [ ] Real AI/ML integration
- [ ] Database storage
- [ ] File storage (S3, local)
- [ ] User authentication
- [ ] Rate limiting
- [ ] Logging and monitoring
