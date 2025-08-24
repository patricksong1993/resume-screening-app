"""
Tests for PDF extraction functionality
"""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch, mock_open
from app.pdf_extractor import (
    extract_text_from_pdf, 
    validate_pdf_file, 
    get_pdf_summary
)

class TestPDFExtractor:
    """Test cases for PDF extraction functions"""
    
    def test_extract_text_from_pdf_file_not_found(self):
        """Test extraction with non-existent file"""
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("/nonexistent/file.pdf")
    
    def test_extract_text_from_pdf_invalid_file_type(self):
        """Test extraction with non-PDF file"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"This is a text file, not a PDF")
            temp_file_path = temp_file.name
        
        try:
            with pytest.raises(ValueError, match="File must be a PDF"):
                extract_text_from_pdf(temp_file_path)
        finally:
            os.unlink(temp_file_path)
    
    @patch('app.pdf_extractor.PyPDF2.PdfReader')
    def test_extract_text_from_pdf_success(self, mock_pdf_reader):
        """Test successful PDF text extraction"""
        # Mock PDF reader
        mock_reader = Mock()
        mock_reader.pages = [
            Mock(extract_text=lambda: "Page 1 content"),
            Mock(extract_text=lambda: "Page 2 content")
        ]
        mock_reader.metadata = {
            '/Title': 'Test Resume',
            '/Author': 'John Doe',
            '/Creator': 'Microsoft Word'
        }
        mock_pdf_reader.return_value = mock_reader
        
        # Mock file operations
        with patch('builtins.open', mock_open(read_data=b'fake pdf content')):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=1024):
                    result = extract_text_from_pdf("/fake/path.pdf")
        
        assert result["text"] == "--- Page 1 ---\nPage 1 content\n\n--- Page 2 ---\nPage 2 content"
        assert result["pages"] == 2
        assert result["file_size"] == 1024
        assert result["metadata"]["title"] == "Test Resume"
        assert result["metadata"]["author"] == "John Doe"
        assert result["error"] is None
        assert result["extraction_time"] is not None
    
    @patch('app.pdf_extractor.PyPDF2.PdfReader')
    def test_extract_text_from_pdf_with_errors(self, mock_pdf_reader):
        """Test PDF extraction with page errors"""
        # Mock PDF reader with one page that fails
        mock_reader = Mock()
        mock_reader.pages = [
            Mock(extract_text=lambda: "Page 1 content"),
            Mock(extract_text=lambda: _raise_exception("Extraction failed"))
        ]
        mock_reader.metadata = {}
        mock_pdf_reader.return_value = mock_reader
        
        def _raise_exception(msg):
            raise Exception(msg)
        
        # Mock file operations
        with patch('builtins.open', mock_open(read_data=b'fake pdf content')):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=1024):
                    result = extract_text_from_pdf("/fake/path.pdf")
        
        assert "Page 1 content" in result["text"]
        assert "Error extracting text" in result["text"]
        assert result["pages"] == 2
        assert result["error"] is None
    
    @patch('app.pdf_extractor.PyPDF2.PdfReader')
    def test_extract_text_from_pdf_invalid_pdf(self, mock_pdf_reader):
        """Test extraction with invalid PDF"""
        # Mock PDF reader to raise PdfReadError
        mock_pdf_reader.side_effect = Exception("Invalid PDF")
        
        with patch('builtins.open', mock_open(read_data=b'fake pdf content')):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=1024):
                    result = extract_text_from_pdf("/fake/path.pdf")
        
        assert result["error"] is not None
        assert "Error extracting text" in result["error"]
    
    def test_validate_pdf_file_not_exists(self):
        """Test PDF validation with non-existent file"""
        is_valid, error_msg = validate_pdf_file("/nonexistent/file.pdf")
        assert not is_valid
        assert "File does not exist" in error_msg
    
    def test_validate_pdf_file_wrong_extension(self):
        """Test PDF validation with wrong file extension"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_file.write(b"This is a text file")
            temp_file_path = temp_file.name
        
        try:
            is_valid, error_msg = validate_pdf_file(temp_file_path)
            assert not is_valid
            assert "File is not a PDF" in error_msg
        finally:
            os.unlink(temp_file_path)
    
    def test_validate_pdf_file_invalid_header(self):
        """Test PDF validation with invalid PDF header"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"This is not a PDF file")
            temp_file_path = temp_file.name
        
        try:
            is_valid, error_msg = validate_pdf_file(temp_file_path)
            assert not is_valid
            assert "invalid header" in error_msg
        finally:
            os.unlink(temp_file_path)
    
    @patch('app.pdf_extractor.PyPDF2.PdfReader')
    def test_validate_pdf_file_success(self, mock_pdf_reader):
        """Test successful PDF validation"""
        # Mock PDF reader
        mock_reader = Mock()
        mock_reader.pages = [Mock(), Mock()]  # 2 pages
        mock_pdf_reader.return_value = mock_reader
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b'%PDF-1.4\nfake content')
            temp_file_path = temp_file.name
        
        try:
            is_valid, error_msg = validate_pdf_file(temp_file_path)
            assert is_valid
            assert error_msg == ""
        finally:
            os.unlink(temp_file_path)
    
    @patch('app.pdf_extractor.PyPDF2.PdfReader')
    def test_validate_pdf_file_no_pages(self, mock_pdf_reader):
        """Test PDF validation with no pages"""
        # Mock PDF reader with no pages
        mock_reader = Mock()
        mock_reader.pages = []
        mock_pdf_reader.return_value = mock_reader
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b'%PDF-1.4\nfake content')
            temp_file_path = temp_file.name
        
        try:
            is_valid, error_msg = validate_pdf_file(temp_file_path)
            assert not is_valid
            assert "no pages" in error_msg
        finally:
            os.unlink(temp_file_path)
    
    def test_get_pdf_summary_file_not_found(self):
        """Test PDF summary with non-existent file"""
        with pytest.raises(FileNotFoundError):
            get_pdf_summary("/nonexistent/file.pdf")
    
    @patch('app.pdf_extractor.PyPDF2.PdfReader')
    def test_get_pdf_summary_success(self, mock_pdf_reader):
        """Test successful PDF summary generation"""
        # Mock PDF reader
        mock_reader = Mock()
        mock_reader.pages = [
            Mock(extract_text=lambda: "Sample text content"),
            Mock(extract_text=lambda: "More content")
        ]
        mock_reader.metadata = {
            '/Title': 'Test Document',
            '/Author': 'Jane Doe',
            '/Creator': 'Adobe Acrobat'
        }
        mock_pdf_reader.return_value = mock_reader
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b'fake pdf content')
            temp_file_path = temp_file.name
        
        try:
            summary = get_pdf_summary(temp_file_path)
            
            assert summary["filename"] == os.path.basename(temp_file_path)
            assert summary["pages"] == 2
            assert summary["has_text"] is True
            assert summary["metadata"]["title"] == "Test Document"
            assert summary["metadata"]["author"] == "Jane Doe"
            assert "error" not in summary
        finally:
            os.unlink(temp_file_path)
    
    @patch('app.pdf_extractor.PyPDF2.PdfReader')
    def test_get_pdf_summary_no_text(self, mock_pdf_reader):
        """Test PDF summary with no text content"""
        # Mock PDF reader with no text
        mock_reader = Mock()
        mock_reader.pages = [Mock(extract_text=lambda: "")]
        mock_reader.metadata = {}
        mock_pdf_reader.return_value = mock_reader
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b'fake pdf content')
            temp_file_path = temp_file.name
        
        try:
            summary = get_pdf_summary(temp_file_path)
            
            assert summary["pages"] == 1
            assert summary["has_text"] is False
        finally:
            os.unlink(temp_file_path)

class TestPDFExtractorIntegration:
    """Integration tests for PDF extraction"""
    
    def test_full_extraction_workflow(self):
        """Test the complete PDF extraction workflow"""
        # This would test with a real PDF file
        # For now, we'll test the function signatures and error handling
        assert callable(extract_text_from_pdf)
        assert callable(validate_pdf_file)
        assert callable(get_pdf_summary)
    
    def test_error_handling_consistency(self):
        """Test that error handling is consistent across functions"""
        # All functions should handle errors gracefully
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("/nonexistent/file.pdf")
        
        with pytest.raises(FileNotFoundError):
            get_pdf_summary("/nonexistent/file.pdf")
        
        # validate_pdf_file returns tuple instead of raising
        is_valid, error_msg = validate_pdf_file("/nonexistent/file.pdf")
        assert not is_valid
        assert isinstance(error_msg, str)
