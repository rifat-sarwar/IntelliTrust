import httpx
import logging
import json
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIIntegrationService:
    def __init__(self):
        self.ai_engine_url = settings.AI_ENGINE_URL
        self.timeout = settings.DOCUMENT_PROCESSING_TIMEOUT

    async def analyze_document(self, file_url: str) -> Dict[str, Any]:
        """
        Send document to AI engine for analysis
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Download file from storage
                file_response = await client.get(file_url)
                file_response.raise_for_status()
                
                # Prepare file for AI engine
                files = {
                    'file': ('document.pdf', file_response.content, 'application/pdf')
                }
                
                # Send to AI engine
                response = await client.post(
                    f"{self.ai_engine_url}/analyze-document",
                    files=files
                )
                response.raise_for_status()
                
                analysis_results = response.json()
                logger.info(f"AI analysis completed successfully")
                
                return analysis_results
                
        except httpx.TimeoutException:
            logger.error("AI analysis timeout")
            raise Exception("AI analysis timed out")
        except httpx.HTTPStatusError as e:
            logger.error(f"AI engine HTTP error: {e.response.status_code}")
            raise Exception(f"AI engine error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            raise Exception(f"AI analysis failed: {str(e)}")

    async def get_analysis_results(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis results from AI engine
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ai_engine_url}/analysis/{file_hash}"
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting analysis results: {str(e)}")
            return None

    async def batch_analyze_documents(self, file_urls: list[str]) -> Dict[str, Any]:
        """
        Analyze multiple documents in batch
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
                # Download all files
                files = []
                for url in file_urls:
                    file_response = await client.get(url)
                    file_response.raise_for_status()
                    files.append(('files', file_response.content))
                
                # Send batch request to AI engine
                response = await client.post(
                    f"{self.ai_engine_url}/batch-analyze",
                    files=files
                )
                response.raise_for_status()
                
                batch_results = response.json()
                logger.info(f"Batch analysis completed for {len(file_urls)} documents")
                
                return batch_results
                
        except Exception as e:
            logger.error(f"Error in batch analysis: {str(e)}")
            raise Exception(f"Batch analysis failed: {str(e)}")

    async def health_check(self) -> bool:
        """
        Check if AI engine is healthy
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.ai_engine_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"AI engine health check failed: {str(e)}")
            return False
