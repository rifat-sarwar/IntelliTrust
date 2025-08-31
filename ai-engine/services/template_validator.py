import os
import logging
from typing import Dict, Any, List
import cv2
import numpy as np
from PIL import Image
import json

logger = logging.getLogger(__name__)

class TemplateValidator:
    """
    Validates document templates and formats against known patterns.
    """
    
    def __init__(self):
        # Load template patterns (in a real implementation, these would be more sophisticated)
        self.template_patterns = {
            'academic_degree': {
                'required_fields': ['university', 'degree', 'student', 'date'],
                'layout_patterns': ['header', 'body', 'signature'],
                'confidence_threshold': 0.7
            },
            'transcript': {
                'required_fields': ['course', 'grade', 'credit', 'gpa'],
                'layout_patterns': ['table', 'header', 'footer'],
                'confidence_threshold': 0.6
            },
            'id_document': {
                'required_fields': ['name', 'date', 'number', 'photo'],
                'layout_patterns': ['photo_area', 'text_fields'],
                'confidence_threshold': 0.8
            },
            'medical_record': {
                'required_fields': ['patient', 'doctor', 'diagnosis', 'date'],
                'layout_patterns': ['header', 'body', 'signature'],
                'confidence_threshold': 0.7
            },
            'financial_document': {
                'required_fields': ['account', 'balance', 'transaction', 'date'],
                'layout_patterns': ['header', 'table', 'footer'],
                'confidence_threshold': 0.6
            }
        }
    
    def validate(self, file_path: str, document_type: str) -> Dict[str, Any]:
        """
        Validate document template against known patterns.
        """
        try:
            results = {
                'is_valid': False,
                'score': 0.0,
                'matched_fields': [],
                'missing_fields': [],
                'layout_score': 0.0,
                'content_score': 0.0,
                'warnings': []
            }
            
            # Get template pattern for document type
            template = self.template_patterns.get(document_type, {})
            if not template:
                results['warnings'].append(f"No template pattern found for {document_type}")
                return results
            
            # Extract text content
            text_content = self._extract_text(file_path)
            
            # Validate required fields
            field_results = self._validate_required_fields(text_content, template.get('required_fields', []))
            results['matched_fields'] = field_results['matched']
            results['missing_fields'] = field_results['missing']
            results['content_score'] = field_results['score']
            
            # Validate layout patterns
            layout_results = self._validate_layout(file_path, template.get('layout_patterns', []))
            results['layout_score'] = layout_results['score']
            
            # Calculate overall score
            overall_score = (results['content_score'] * 0.6) + (results['layout_score'] * 0.4)
            results['score'] = overall_score
            
            # Determine if document is valid
            threshold = template.get('confidence_threshold', 0.7)
            results['is_valid'] = overall_score >= threshold
            
            if not results['is_valid']:
                results['warnings'].append(f"Document score {overall_score:.2f} below threshold {threshold}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in template validation: {str(e)}")
            return {
                'is_valid': False,
                'score': 0.0,
                'matched_fields': [],
                'missing_fields': [],
                'layout_score': 0.0,
                'content_score': 0.0,
                'warnings': [f"Validation failed: {str(e)}"]
            }
    
    def _extract_text(self, file_path: str) -> str:
        """
        Extract text content from document.
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                # Use OCR for images
                import pytesseract
                image = cv2.imread(file_path)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray)
                return text.lower()
            
            elif file_extension == '.pdf':
                # Extract text from PDF
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text.lower()
            
            elif file_extension in ['.docx', '.doc']:
                # Extract text from Word documents
                from docx import Document as DocxDocument
                doc = DocxDocument(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text.lower()
            
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return ""
    
    def _validate_required_fields(self, text_content: str, required_fields: List[str]) -> Dict[str, Any]:
        """
        Validate that required fields are present in the document.
        """
        try:
            matched_fields = []
            missing_fields = []
            
            for field in required_fields:
                if field in text_content:
                    matched_fields.append(field)
                else:
                    missing_fields.append(field)
            
            # Calculate score based on matched fields
            if required_fields:
                score = len(matched_fields) / len(required_fields)
            else:
                score = 0.0
            
            return {
                'matched': matched_fields,
                'missing': missing_fields,
                'score': score
            }
            
        except Exception as e:
            logger.error(f"Error validating required fields: {str(e)}")
            return {
                'matched': [],
                'missing': required_fields,
                'score': 0.0
            }
    
    def _validate_layout(self, file_path: str, layout_patterns: List[str]) -> Dict[str, Any]:
        """
        Validate document layout patterns.
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                return self._validate_image_layout(file_path, layout_patterns)
            else:
                # For non-image files, use a simplified layout validation
                return self._validate_generic_layout(file_path, layout_patterns)
                
        except Exception as e:
            logger.error(f"Error validating layout: {str(e)}")
            return {'score': 0.0}
    
    def _validate_image_layout(self, file_path: str, layout_patterns: List[str]) -> Dict[str, Any]:
        """
        Validate layout patterns in image documents.
        """
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                return {'score': 0.0}
            
            height, width = image.shape[:2]
            score = 0.0
            detected_patterns = []
            
            # Simple layout validation based on image characteristics
            # In a real implementation, you would use more sophisticated computer vision techniques
            
            # Check for header area (top 20% of image)
            header_region = image[0:int(height*0.2), :]
            if self._has_text_content(header_region):
                detected_patterns.append('header')
                score += 0.3
            
            # Check for body area (middle 60% of image)
            body_region = image[int(height*0.2):int(height*0.8), :]
            if self._has_text_content(body_region):
                detected_patterns.append('body')
                score += 0.4
            
            # Check for footer area (bottom 20% of image)
            footer_region = image[int(height*0.8):, :]
            if self._has_text_content(footer_region):
                detected_patterns.append('footer')
                score += 0.3
            
            # Check for table-like structures
            if self._detect_table_structure(image):
                detected_patterns.append('table')
                score += 0.2
            
            # Check for signature areas
            if self._detect_signature_area(image):
                detected_patterns.append('signature')
                score += 0.2
            
            return {
                'score': min(score, 1.0),
                'detected_patterns': detected_patterns
            }
            
        except Exception as e:
            logger.error(f"Error in image layout validation: {str(e)}")
            return {'score': 0.0}
    
    def _validate_generic_layout(self, file_path: str, layout_patterns: List[str]) -> Dict[str, Any]:
        """
        Validate layout for non-image documents.
        """
        try:
            # Simplified layout validation for PDF and Word documents
            # In a real implementation, you would analyze document structure more thoroughly
            
            score = 0.0
            detected_patterns = []
            
            # Basic validation based on file characteristics
            if os.path.getsize(file_path) > 1000:  # Document has content
                score += 0.5
                detected_patterns.append('content')
            
            # For now, return a basic score
            return {
                'score': 0.7,  # Placeholder score
                'detected_patterns': ['generic_document']
            }
            
        except Exception as e:
            logger.error(f"Error in generic layout validation: {str(e)}")
            return {'score': 0.0}
    
    def _has_text_content(self, image_region: np.ndarray) -> bool:
        """
        Check if image region contains text content.
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image_region, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Count edge pixels
            edge_pixels = np.sum(edges > 0)
            total_pixels = edges.shape[0] * edges.shape[1]
            
            # If more than 1% of pixels are edges, likely has content
            return (edge_pixels / total_pixels) > 0.01
            
        except Exception as e:
            logger.error(f"Error checking text content: {str(e)}")
            return False
    
    def _detect_table_structure(self, image: np.ndarray) -> bool:
        """
        Detect table-like structures in image.
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply morphological operations to detect lines
            kernel = np.ones((1, 50), np.uint8)  # Horizontal lines
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            
            kernel = np.ones((50, 1), np.uint8)  # Vertical lines
            vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            
            # Combine horizontal and vertical lines
            table_structure = cv2.add(horizontal_lines, vertical_lines)
            
            # Count table structure pixels
            table_pixels = np.sum(table_structure > 0)
            total_pixels = table_structure.shape[0] * table_structure.shape[1]
            
            # If more than 0.5% of pixels are table structure, likely has tables
            return (table_pixels / total_pixels) > 0.005
            
        except Exception as e:
            logger.error(f"Error detecting table structure: {str(e)}")
            return False
    
    def _detect_signature_area(self, image: np.ndarray) -> bool:
        """
        Detect signature areas in image.
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Look for areas with high contrast and curved features
            # This is a simplified implementation
            # In a real implementation, you would use more sophisticated signature detection
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply edge detection
            edges = cv2.Canny(blurred, 30, 100)
            
            # Look for curved lines (potential signatures)
            # This is a very basic approach
            return np.sum(edges > 0) > 1000  # Arbitrary threshold
            
        except Exception as e:
            logger.error(f"Error detecting signature area: {str(e)}")
            return False
