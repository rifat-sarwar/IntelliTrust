import os
import logging
from typing import Dict, Any, List
import re
import json
from datetime import datetime
import pytesseract
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """
    Analyzes document content and extracts structured information.
    """
    
    def __init__(self):
        # Define patterns for different types of information
        self.patterns = {
            'dates': [
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # DD/MM/YYYY or DD-MM-YYYY
                r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',   # YYYY/MM/DD or YYYY-MM-DD
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',  # Month DD, YYYY
                r'\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b'  # DD Month YYYY
            ],
            'emails': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            'phone_numbers': [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US format
                r'\b\+\d{1,3}[-.]?\d{1,4}[-.]?\d{1,4}[-.]?\d{1,4}\b',  # International
                r'\b\(\d{3}\) \d{3}-\d{4}\b'  # (XXX) XXX-XXXX
            ],
            'names': [
                r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
                r'\b[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+\b'  # First M. Last
            ],
            'addresses': [
                r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b'
            ],
            'academic_info': {
                'gpa': r'\bGPA[:\s]*(\d+\.\d+)\b',
                'credits': r'\b(\d+)\s*(?:credit|credits)\b',
                'grade': r'\b[A-F][+-]?\b',
                'course': r'\b[A-Z]{2,4}\s*\d{3,4}\b'  # Course codes like CS101
            },
            'financial_info': {
                'amount': r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
                'account': r'\b(?:Account|Acct)[:\s]*(\d+)\b',
                'balance': r'\b(?:Balance|Bal)[:\s]*(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\b'
            }
        }
    
    def analyze(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze document content and extract structured information.
        """
        try:
            results = {
                'extracted_entities': {},
                'content_quality_score': 0.0,
                'readability_score': 0.0,
                'information_density': 0.0,
                'key_phrases': [],
                'summary': '',
                'warnings': []
            }
            
            # Extract text content
            text_content = self._extract_text(file_path)
            if not text_content:
                results['warnings'].append("No text content could be extracted")
                return results
            
            # Extract entities
            entities = self._extract_entities(text_content)
            results['extracted_entities'] = entities
            
            # Analyze content quality
            quality_score = self._analyze_content_quality(text_content)
            results['content_quality_score'] = quality_score
            
            # Analyze readability
            readability_score = self._analyze_readability(text_content)
            results['readability_score'] = readability_score
            
            # Calculate information density
            info_density = self._calculate_information_density(text_content, entities)
            results['information_density'] = info_density
            
            # Extract key phrases
            key_phrases = self._extract_key_phrases(text_content)
            results['key_phrases'] = key_phrases
            
            # Generate summary
            summary = self._generate_summary(text_content, entities)
            results['summary'] = summary
            
            # Calculate overall score
            overall_score = (quality_score * 0.3) + (readability_score * 0.2) + (info_density * 0.5)
            results['score'] = overall_score
            
            return results
            
        except Exception as e:
            logger.error(f"Error in content analysis: {str(e)}")
            return {
                'extracted_entities': {},
                'content_quality_score': 0.0,
                'readability_score': 0.0,
                'information_density': 0.0,
                'key_phrases': [],
                'summary': '',
                'warnings': [f"Content analysis failed: {str(e)}"],
                'score': 0.0
            }
    
    def _extract_text(self, file_path: str) -> str:
        """
        Extract text content from document.
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                # Use OCR for images
                image = cv2.imread(file_path)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray)
                return text
            
            elif file_extension == '.pdf':
                # Extract text from PDF
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            
            elif file_extension in ['.docx', '.doc']:
                # Extract text from Word documents
                from docx import Document as DocxDocument
                doc = DocxDocument(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return ""
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract named entities and structured information from text.
        """
        try:
            entities = {
                'dates': [],
                'emails': [],
                'phone_numbers': [],
                'names': [],
                'addresses': [],
                'academic_info': {},
                'financial_info': {}
            }
            
            # Extract dates
            for pattern in self.patterns['dates']:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities['dates'].extend(matches)
            
            # Extract emails
            for pattern in self.patterns['emails']:
                matches = re.findall(pattern, text)
                entities['emails'].extend(matches)
            
            # Extract phone numbers
            for pattern in self.patterns['phone_numbers']:
                matches = re.findall(pattern, text)
                entities['phone_numbers'].extend(matches)
            
            # Extract names
            for pattern in self.patterns['names']:
                matches = re.findall(pattern, text)
                entities['names'].extend(matches)
            
            # Extract addresses
            for pattern in self.patterns['addresses']:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities['addresses'].extend(matches)
            
            # Extract academic information
            for info_type, pattern in self.patterns['academic_info'].items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    entities['academic_info'][info_type] = matches
            
            # Extract financial information
            for info_type, pattern in self.patterns['financial_info'].items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    entities['financial_info'][info_type] = matches
            
            # Remove duplicates
            for key in entities:
                if isinstance(entities[key], list):
                    entities[key] = list(set(entities[key]))
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return {}
    
    def _analyze_content_quality(self, text: str) -> float:
        """
        Analyze the quality of content.
        """
        try:
            score = 0.0
            
            # Check text length
            if len(text) > 100:
                score += 0.2
            
            # Check for proper sentence structure
            sentences = re.split(r'[.!?]+', text)
            if len(sentences) > 5:
                score += 0.2
            
            # Check for proper capitalization
            capitalized_words = len(re.findall(r'\b[A-Z][a-z]+\b', text))
            total_words = len(text.split())
            if total_words > 0:
                capitalization_ratio = capitalized_words / total_words
                if 0.05 < capitalization_ratio < 0.3:
                    score += 0.2
            
            # Check for numbers and dates
            numbers = len(re.findall(r'\d+', text))
            if numbers > 0:
                score += 0.2
            
            # Check for special characters (indicating structured content)
            special_chars = len(re.findall(r'[^\w\s]', text))
            if special_chars > 10:
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error analyzing content quality: {str(e)}")
            return 0.0
    
    def _analyze_readability(self, text: str) -> float:
        """
        Analyze text readability using basic metrics.
        """
        try:
            # Simple readability analysis
            words = text.split()
            sentences = re.split(r'[.!?]+', text)
            
            if len(words) == 0 or len(sentences) == 0:
                return 0.0
            
            # Average words per sentence
            avg_words_per_sentence = len(words) / len(sentences)
            
            # Calculate readability score
            if avg_words_per_sentence < 20:
                score = 0.9  # Good readability
            elif avg_words_per_sentence < 30:
                score = 0.7  # Moderate readability
            else:
                score = 0.5  # Poor readability
            
            return score
            
        except Exception as e:
            logger.error(f"Error analyzing readability: {str(e)}")
            return 0.0
    
    def _calculate_information_density(self, text: str, entities: Dict[str, Any]) -> float:
        """
        Calculate information density based on extracted entities.
        """
        try:
            total_entities = 0
            
            # Count all extracted entities
            for key, value in entities.items():
                if isinstance(value, list):
                    total_entities += len(value)
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, list):
                            total_entities += len(sub_value)
            
            # Calculate density based on text length and entity count
            text_length = len(text)
            if text_length > 0:
                density = total_entities / (text_length / 1000)  # Entities per 1000 characters
                return min(density / 10, 1.0)  # Normalize to 0-1
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating information density: {str(e)}")
            return 0.0
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """
        Extract key phrases from text.
        """
        try:
            # Simple key phrase extraction
            # In a real implementation, you would use more sophisticated NLP techniques
            
            # Remove common words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            
            # Split into sentences
            sentences = re.split(r'[.!?]+', text)
            
            key_phrases = []
            for sentence in sentences:
                words = sentence.split()
                # Filter out stop words and short words
                filtered_words = [word for word in words if word.lower() not in stop_words and len(word) > 3]
                
                if len(filtered_words) >= 3:
                    # Take phrases of 3-5 words
                    for i in range(len(filtered_words) - 2):
                        phrase = ' '.join(filtered_words[i:i+3])
                        if len(phrase) > 10:
                            key_phrases.append(phrase)
            
            # Return unique phrases, limited to top 10
            return list(set(key_phrases))[:10]
            
        except Exception as e:
            logger.error(f"Error extracting key phrases: {str(e)}")
            return []
    
    def _generate_summary(self, text: str, entities: Dict[str, Any]) -> str:
        """
        Generate a summary of the document content.
        """
        try:
            summary_parts = []
            
            # Add document type based on entities
            if entities.get('academic_info'):
                summary_parts.append("Academic document")
            elif entities.get('financial_info'):
                summary_parts.append("Financial document")
            elif entities.get('names') and entities.get('dates'):
                summary_parts.append("Personal document")
            
            # Add key information
            if entities.get('dates'):
                summary_parts.append(f"Contains {len(entities['dates'])} date(s)")
            
            if entities.get('names'):
                summary_parts.append(f"Contains {len(entities['names'])} name(s)")
            
            if entities.get('emails'):
                summary_parts.append(f"Contains {len(entities['emails'])} email(s)")
            
            # Add content quality indicator
            if len(text) > 500:
                summary_parts.append("Substantial content")
            elif len(text) > 100:
                summary_parts.append("Moderate content")
            else:
                summary_parts.append("Minimal content")
            
            return ". ".join(summary_parts) + "."
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Summary generation failed."
