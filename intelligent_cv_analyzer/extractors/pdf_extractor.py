"""
PDF Text Extractor
Phase 3: Core Application Implementation

This module handles text extraction from PDF files using pdfminer.six library.
It provides robust error handling and text cleaning for CV analysis.
"""

import os
import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path

try:
    from pdfminer.high_level import extract_text
    from pdfminer.layout import LAParams
    from pdfminer.pdfinterp import PDFResourceManager
    from pdfminer.converter import TextConverter
    from pdfminer.pdfinterp import PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from io import StringIO
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: pdfminer.six not available. PDF extraction will not work.")


class PDFExtractor:
    """
    PDF text extraction class with error handling and text cleaning.
    """
    
    def __init__(self):
        """Initialize the PDF extractor."""
        self.supported_extensions = ['.pdf']
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
    
    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        start_time = time.time()
        
        result = {
            'success': False,
            'text': '',
            'metadata': {},
            'error': None,
            'extraction_time': 0.0
        }
        
        try:
            # Validate file
            if not self._validate_file(file_path):
                result['error'] = "Invalid PDF file"
                return result
            
            # Check if PDF library is available
            if not PDF_AVAILABLE:
                result['error'] = "PDF extraction library not available"
                return result
            
            # Extract text using pdfminer
            text = extract_text(file_path)
            
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Get file metadata
            metadata = self._get_file_metadata(file_path)
            
            result.update({
                'success': True,
                'text': cleaned_text,
                'metadata': metadata,
                'extraction_time': time.time() - start_time
            })
            
        except Exception as e:
            result['error'] = f"PDF extraction failed: {str(e)}"
            result['extraction_time'] = time.time() - start_time
        
        return result
    
    def _validate_file(self, file_path: str) -> bool:
        """
        Validate PDF file before extraction.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            True if file is valid, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return False
            
            # Check file extension
            if not file_path.lower().endswith('.pdf'):
                return False
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return False
            
            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _clean_text(self, raw_text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            raw_text: Raw text extracted from PDF
            
        Returns:
            Cleaned and normalized text
        """
        if not raw_text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(raw_text.split())
        
        # Remove special characters that might interfere with matching
        # Keep alphanumeric, spaces, and common punctuation
        import re
        text = re.sub(r'[^\w\s\-.,;:!?()]', ' ', text)
        
        # Normalize multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing file metadata
        """
        metadata = {
            'filename': os.path.basename(file_path),
            'file_size': 0,
            'file_path': file_path,
            'extraction_timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            metadata['file_size'] = os.path.getsize(file_path)
        except Exception as e:
            logging.getLogger(__name__).warning("Failed to get PDF file size: %s", e, exc_info=True)
        
        return metadata
    
    def batch_extract(self, file_paths: list) -> Dict[str, Dict[str, Any]]:
        """
        Extract text from multiple PDF files.
        
        Args:
            file_paths: List of PDF file paths
            
        Returns:
            Dictionary mapping file paths to extraction results
        """
        results = {}
        
        for file_path in file_paths:
            results[file_path] = self.extract_text(file_path)
        
        return results
    
    def is_supported(self, file_path: str) -> bool:
        """
        Check if file is supported by this extractor.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is supported, False otherwise
        """
        return file_path.lower().endswith('.pdf')


# Example usage and testing
if __name__ == "__main__":
    # Test the PDF extractor
    extractor = PDFExtractor()
    
    print("=== PDF Extractor Test ===\n")
    
    # Test with sample file (if available)
    sample_file = "sample_cv.pdf"
    
    if os.path.exists(sample_file):
        print(f"Extracting text from: {sample_file}")
        result = extractor.extract_text(sample_file)
        
        if result['success']:
            print(f"✓ Extraction successful")
            print(f"  Text length: {len(result['text'])} characters")
            print(f"  Extraction time: {result['extraction_time']:.3f} seconds")
            print(f"  File size: {result['metadata']['file_size']} bytes")
            print(f"\nFirst 200 characters:")
            print(result['text'][:200] + "...")
        else:
            print(f"✗ Extraction failed: {result['error']}")
    else:
        print(f"Sample file '{sample_file}' not found.")
        print("Creating a test with mock data...")
        
        # Test validation
        test_files = [
            "nonexistent.pdf",
            "test.txt",  # Wrong extension
            "test.pdf"   # Valid extension
        ]
        
        for test_file in test_files:
            is_valid = extractor._validate_file(test_file)
            print(f"File '{test_file}': {'Valid' if is_valid else 'Invalid'}")
        
        # Test text cleaning
        sample_text = """
        This is a sample CV text with    multiple    spaces
        and special characters: @#$%^&*()
        It should be cleaned properly.
        """
        
        cleaned = extractor._clean_text(sample_text)
        print(f"\nOriginal text: {repr(sample_text)}")
        print(f"Cleaned text: {repr(cleaned)}")
