import os
import logging
from typing import Dict, Any, List
import cv2
import numpy as np
from PIL import Image
import hashlib
import json

logger = logging.getLogger(__name__)

class ForensicAnalyzer:
    """
    Performs forensic analysis on documents to detect tampering and authenticity.
    """
    
    def __init__(self):
        self.analysis_methods = [
            'metadata_analysis',
            'error_level_analysis',
            'noise_analysis',
            'compression_analysis',
            'format_consistency'
        ]
    
    def analyze(self, file_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive forensic analysis on a document.
        """
        try:
            results = {
                'overall_score': 0.0,
                'authenticity_score': 0.0,
                'tampering_detected': False,
                'analysis_details': {},
                'warnings': []
            }
            
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # Perform different analyses based on file type
            if file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                results = self._analyze_image_forensics(file_path, results)
            elif file_extension == '.pdf':
                results = self._analyze_pdf_forensics(file_path, results)
            else:
                results = self._analyze_generic_forensics(file_path, results)
            
            # Calculate overall score
            results['overall_score'] = self._calculate_overall_score(results)
            results['authenticity_score'] = results['overall_score']
            
            return results
            
        except Exception as e:
            logger.error(f"Error in forensic analysis: {str(e)}")
            return {
                'overall_score': 0.0,
                'authenticity_score': 0.0,
                'tampering_detected': True,
                'analysis_details': {'error': str(e)},
                'warnings': ['Analysis failed']
            }
    
    def _analyze_image_forensics(self, file_path: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform forensic analysis on image files.
        """
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError("Could not load image")
            
            analysis_details = {}
            
            # 1. Error Level Analysis (ELA)
            ela_score = self._error_level_analysis(file_path)
            analysis_details['error_level_analysis'] = {
                'score': ela_score,
                'description': 'Detects areas of the image that have been modified'
            }
            
            # 2. Noise Analysis
            noise_score = self._noise_analysis(image)
            analysis_details['noise_analysis'] = {
                'score': noise_score,
                'description': 'Analyzes noise patterns for inconsistencies'
            }
            
            # 3. Compression Analysis
            compression_score = self._compression_analysis(file_path)
            analysis_details['compression_analysis'] = {
                'score': compression_score,
                'description': 'Checks for multiple compression artifacts'
            }
            
            # 4. Metadata Analysis
            metadata_score = self._metadata_analysis(file_path)
            analysis_details['metadata_analysis'] = {
                'score': metadata_score,
                'description': 'Analyzes file metadata for inconsistencies'
            }
            
            # 5. Format Consistency
            format_score = self._format_consistency_analysis(file_path)
            analysis_details['format_consistency'] = {
                'score': format_score,
                'description': 'Checks for format inconsistencies'
            }
            
            results['analysis_details'] = analysis_details
            
            # Check for tampering indicators
            tampering_indicators = []
            if ela_score < 0.7:
                tampering_indicators.append("Potential modification detected in image")
            if noise_score < 0.6:
                tampering_indicators.append("Unusual noise patterns detected")
            if compression_score < 0.5:
                tampering_indicators.append("Multiple compression artifacts detected")
            
            if tampering_indicators:
                results['tampering_detected'] = True
                results['warnings'].extend(tampering_indicators)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in image forensic analysis: {str(e)}")
            results['warnings'].append(f"Image analysis failed: {str(e)}")
            return results
    
    def _analyze_pdf_forensics(self, file_path: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform forensic analysis on PDF files.
        """
        try:
            analysis_details = {}
            
            # 1. PDF Structure Analysis
            structure_score = self._pdf_structure_analysis(file_path)
            analysis_details['pdf_structure'] = {
                'score': structure_score,
                'description': 'Analyzes PDF internal structure'
            }
            
            # 2. Metadata Analysis
            metadata_score = self._metadata_analysis(file_path)
            analysis_details['metadata_analysis'] = {
                'score': metadata_score,
                'description': 'Analyzes PDF metadata'
            }
            
            # 3. Content Consistency
            content_score = self._pdf_content_consistency(file_path)
            analysis_details['content_consistency'] = {
                'score': content_score,
                'description': 'Checks content consistency'
            }
            
            results['analysis_details'] = analysis_details
            
            # Check for tampering indicators
            if structure_score < 0.7:
                results['tampering_detected'] = True
                results['warnings'].append("PDF structure anomalies detected")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in PDF forensic analysis: {str(e)}")
            results['warnings'].append(f"PDF analysis failed: {str(e)}")
            return results
    
    def _analyze_generic_forensics(self, file_path: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform generic forensic analysis for other file types.
        """
        try:
            analysis_details = {}
            
            # 1. File Integrity
            integrity_score = self._file_integrity_check(file_path)
            analysis_details['file_integrity'] = {
                'score': integrity_score,
                'description': 'Checks file integrity'
            }
            
            # 2. Metadata Analysis
            metadata_score = self._metadata_analysis(file_path)
            analysis_details['metadata_analysis'] = {
                'score': metadata_score,
                'description': 'Analyzes file metadata'
            }
            
            results['analysis_details'] = analysis_details
            
            return results
            
        except Exception as e:
            logger.error(f"Error in generic forensic analysis: {str(e)}")
            results['warnings'].append(f"Generic analysis failed: {str(e)}")
            return results
    
    def _error_level_analysis(self, file_path: str) -> float:
        """
        Perform Error Level Analysis on image.
        """
        try:
            # This is a simplified ELA implementation
            # In a real implementation, you would use more sophisticated ELA algorithms
            return 0.85  # Placeholder score
        except Exception as e:
            logger.error(f"Error in ELA: {str(e)}")
            return 0.0
    
    def _noise_analysis(self, image: np.ndarray) -> float:
        """
        Analyze noise patterns in image.
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply noise detection filter
            kernel = np.ones((3,3), np.float32) / 9
            filtered = cv2.filter2D(gray, -1, kernel)
            
            # Calculate noise level
            noise = cv2.absdiff(gray, filtered)
            noise_level = np.mean(noise)
            
            # Normalize score (lower noise = higher score for authentic documents)
            score = max(0, 1 - (noise_level / 255))
            
            return score
            
        except Exception as e:
            logger.error(f"Error in noise analysis: {str(e)}")
            return 0.0
    
    def _compression_analysis(self, file_path: str) -> float:
        """
        Analyze compression artifacts.
        """
        try:
            # This is a simplified implementation
            # In a real implementation, you would analyze compression patterns
            return 0.9  # Placeholder score
        except Exception as e:
            logger.error(f"Error in compression analysis: {str(e)}")
            return 0.0
    
    def _metadata_analysis(self, file_path: str) -> float:
        """
        Analyze file metadata for inconsistencies.
        """
        try:
            # Check file creation and modification times
            stat = os.stat(file_path)
            
            # Basic consistency check
            if stat.st_mtime > stat.st_ctime:
                return 0.7  # Modification time after creation time
            else:
                return 0.9  # Normal case
                
        except Exception as e:
            logger.error(f"Error in metadata analysis: {str(e)}")
            return 0.0
    
    def _format_consistency_analysis(self, file_path: str) -> float:
        """
        Check format consistency.
        """
        try:
            # This is a simplified implementation
            # In a real implementation, you would check format-specific consistency
            return 0.95  # Placeholder score
        except Exception as e:
            logger.error(f"Error in format consistency analysis: {str(e)}")
            return 0.0
    
    def _pdf_structure_analysis(self, file_path: str) -> float:
        """
        Analyze PDF internal structure.
        """
        try:
            # This is a simplified implementation
            # In a real implementation, you would analyze PDF structure
            return 0.9  # Placeholder score
        except Exception as e:
            logger.error(f"Error in PDF structure analysis: {str(e)}")
            return 0.0
    
    def _pdf_content_consistency(self, file_path: str) -> float:
        """
        Check PDF content consistency.
        """
        try:
            # This is a simplified implementation
            # In a real implementation, you would check content consistency
            return 0.85  # Placeholder score
        except Exception as e:
            logger.error(f"Error in PDF content consistency: {str(e)}")
            return 0.0
    
    def _file_integrity_check(self, file_path: str) -> float:
        """
        Check file integrity.
        """
        try:
            # Check if file can be read completely
            with open(file_path, 'rb') as f:
                f.read()
            return 0.95  # File is readable
        except Exception as e:
            logger.error(f"Error in file integrity check: {str(e)}")
            return 0.0
    
    def _calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """
        Calculate overall forensic analysis score.
        """
        try:
            details = results.get('analysis_details', {})
            if not details:
                return 0.0
            
            scores = []
            for method, data in details.items():
                if isinstance(data, dict) and 'score' in data:
                    scores.append(data['score'])
            
            if scores:
                return sum(scores) / len(scores)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating overall score: {str(e)}")
            return 0.0
