"""
PDF Text Extraction Module using PyPDF2
"""
import PyPDF2
import os
from typing import Dict, Optional, Tuple
from datetime import datetime

def extract_text_from_pdf(file_path: str) -> Dict[str, any]:
    """
    Extract all text from a PDF file using PyPDF2
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        Dict containing extracted text and metadata
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is not a valid PDF
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    if not file_path.lower().endswith('.pdf'):
        raise ValueError("File must be a PDF")
    
    result = {
        "text": "",
        "pages": 0,
        "metadata": {},
        "extraction_time": None,
        "file_size": 0,
        "error": None
    }
    
    try:
        # Get file size
        result["file_size"] = os.path.getsize(file_path)
        
        # Record extraction start time
        start_time = datetime.now()
        
        with open(file_path, 'rb') as file:
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Get number of pages
            result["pages"] = len(pdf_reader.pages)
            
            # Extract text from each page
            text_content = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
                    else:
                        text_content.append(f"--- Page {page_num + 1} ---\n[No text content]")
                except Exception as e:
                    text_content.append(f"--- Page {page_num + 1} ---\n[Error extracting text: {str(e)}]")
            
            # Combine all text
            result["text"] = "\n\n".join(text_content)
            
            # Extract metadata
            if pdf_reader.metadata:
                result["metadata"] = {
                    "title": pdf_reader.metadata.get('/Title', ''),
                    "author": pdf_reader.metadata.get('/Author', ''),
                    "subject": pdf_reader.metadata.get('/Subject', ''),
                    "creator": pdf_reader.metadata.get('/Creator', ''),
                    "producer": pdf_reader.metadata.get('/Producer', ''),
                    "creation_date": pdf_reader.metadata.get('/CreationDate', ''),
                    "modification_date": pdf_reader.metadata.get('/ModDate', '')
                }
            
            # Calculate extraction time
            end_time = datetime.now()
            result["extraction_time"] = (end_time - start_time).total_seconds()
            
    except PyPDF2.errors.PdfReadError as e:
        result["error"] = f"Invalid PDF file: {str(e)}"
    except Exception as e:
        result["error"] = f"Error extracting text: {str(e)}"
    
    return result

def validate_pdf_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate if a file is a valid PDF
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    if not file_path.lower().endswith('.pdf'):
        return False, "File is not a PDF"
    
    try:
        with open(file_path, 'rb') as file:
            # Try to read the PDF header
            header = file.read(4)
            if header != b'%PDF':
                return False, "File is not a valid PDF (invalid header)"
            
            # Try to create PDF reader
            file.seek(0)
            pdf_reader = PyPDF2.PdfReader(file)
            if len(pdf_reader.pages) == 0:
                return False, "PDF has no pages"
                
        return True, ""
        
    except Exception as e:
        return False, f"Error validating PDF: {str(e)}"

def get_pdf_summary(file_path: str) -> Dict[str, any]:
    """
    Get a summary of PDF content without full text extraction
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        Dict containing PDF summary information
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    summary = {
        "filename": os.path.basename(file_path),
        "file_size": os.path.getsize(file_path),
        "pages": 0,
        "has_text": False,
        "metadata": {}
    }
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            summary["pages"] = len(pdf_reader.pages)
            
            # Check if first page has text
            if summary["pages"] > 0:
                first_page = pdf_reader.pages[0]
                sample_text = first_page.extract_text()
                summary["has_text"] = len(sample_text.strip()) > 0
            
            # Get basic metadata
            if pdf_reader.metadata:
                summary["metadata"] = {
                    "title": pdf_reader.metadata.get('/Title', ''),
                    "author": pdf_reader.metadata.get('/Author', ''),
                    "creator": pdf_reader.metadata.get('/Creator', '')
                }
                
    except Exception as e:
        summary["error"] = str(e)
    
    return summary
