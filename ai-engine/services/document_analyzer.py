import os
import logging
from typing import Dict, Any, List
import cv2
import numpy as np
from PIL import Image
import pytesseract
import PyPDF2
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    """
    Analyzes documents to detect type and extract basic information.
    """
    
    def __init__(self):
        self.supported_types = {
            'pdf': self._analyze_pdf,
            'docx': self._analyze_docx,
            'image': self._analyze_image
        }
        
        # Document type patterns
        self.type_patterns = {
            'academic_degree': [
                'degree', 'bachelor', 'master', 'doctorate', 'phd', 'university', 'college',
                'graduation', 'diploma', 'certificate'
            ],
            'transcript': [
                'transcript', 'grade', 'gpa', 'credit', 'course', 'semester', 'academic record'
            ],
            'id_document': [
                'passport', 'driver license', 'national id', 'identity card', 'ssn', 'social security'
            ],
            'medical_record': [
                'medical', 'health', 'patient', 'diagnosis', 'treatment', 'prescription', 'doctor'
            ],
            'financial_document': [
                'bank', 'financial', 'account', 'transaction', 'statement', 'balance', 'credit'
            ]
        }
    
    def detect_document_type(self, file_path: str) -> Dict[str, Any]:
        """
        Detect the type of document and extract basic information.
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # Determine file type
            if file_extension == '.pdf':
                return self._analyze_pdf(file_path)
            elif file_extension in ['.docx', '.doc']:
                return self._analyze_docx(file_path)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                return self._analyze_image(file_path)
            else:
                return {
                    'detected_type': 'unknown',
                    'confidence': 0.0,
                    'extracted_text': '',
                    'metadata': {}
                }
                
        except Exception as e:
            logger.error(f"Error detecting document type: {str(e)}")
            return {
                'detected_type': 'error',
                'confidence': 0.0,
                'extracted_text': '',
                'metadata': {'error': str(e)}
            }
    
    def _analyze_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze PDF documents.
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                # Extract metadata
                metadata = {}
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                        'modification_date': pdf_reader.metadata.get('/ModDate', '')
                    }
                
                # Detect document type
                doc_type = self._classify_document_type(text)
                
                return {
                    'detected_type': doc_type['type'],
                    'confidence': doc_type['confidence'],
                    'extracted_text': text,
                    'metadata': metadata,
                    'page_count': len(pdf_reader.pages),
                    'file_type': 'pdf'
                }
                
        except Exception as e:
            logger.error(f"Error analyzing PDF: {str(e)}")
            return {
                'detected_type': 'error',
                'confidence': 0.0,
                'extracted_text': '',
                'metadata': {'error': str(e)},
                'file_type': 'pdf'
            }
    
    def _analyze_docx(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze DOCX documents.
        """
        try:
            doc = DocxDocument(file_path)
            
            # Extract text
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Extract metadata
            metadata = {
                'title': doc.core_properties.title or '',
                'author': doc.core_properties.author or '',
                'subject': doc.core_properties.subject or '',
                'keywords': doc.core_properties.keywords or '',
                'created': str(doc.core_properties.created) if doc.core_properties.created else '',
                'modified': str(doc.core_properties.modified) if doc.core_properties.modified else ''
            }
            
            # Detect document type
            doc_type = self._classify_document_type(text)
            
            return {
                'detected_type': doc_type['type'],
                'confidence': doc_type['confidence'],
                'extracted_text': text,
                'metadata': metadata,
                'file_type': 'docx'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing DOCX: {str(e)}")
            return {
                'detected_type': 'error',
                'confidence': 0.0,
                'extracted_text': '',
                'metadata': {'error': str(e)},
                'file_type': 'docx'
            }
    
    def _analyze_image(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze image documents using OCR.
        """
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError("Could not load image")
            
            # Convert to grayscale for OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(gray)
            
            # Get image metadata
            height, width, channels = image.shape
            metadata = {
                'width': width,
                'height': height,
                'channels': channels,
                'file_size': os.path.getsize(file_path)
            }
            
            # Detect document type
            doc_type = self._classify_document_type(text)
            
            return {
                'detected_type': doc_type['type'],
                'confidence': doc_type['confidence'],
                'extracted_text': text,
                'metadata': metadata,
                'file_type': 'image'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return {
                'detected_type': 'error',
                'confidence': 0.0,
                'extracted_text': '',
                'metadata': {'error': str(e)},
                'file_type': 'image'
            }
    
    def _classify_document_type(self, text: str) -> Dict[str, Any]:
        """
        Classify document type based on extracted text.
        """
        text_lower = text.lower()
        scores = {}
        
        # Calculate scores for each document type
        for doc_type, patterns in self.type_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    score += 1
            scores[doc_type] = score / len(patterns)
        
        # Find the best match
        if scores:
            best_type = max(scores, key=scores.get)
            best_score = scores[best_type]
            
            if best_score > 0.1:  # Threshold for classification
                return {
                    'type': best_type,
                    'confidence': best_score
                }
        
        return {
            'type': 'unknown',
            'confidence': 0.0
        }
