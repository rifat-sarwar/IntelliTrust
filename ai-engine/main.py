import asyncio
import logging
import os
import sys
from typing import Dict, Any, List
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import redis
import json
import hashlib
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.document_analyzer import DocumentAnalyzer
from services.forensic_analyzer import ForensicAnalyzer
from services.template_validator import TemplateValidator
from services.content_analyzer import ContentAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# Initialize AI services
document_analyzer = DocumentAnalyzer()
forensic_analyzer = ForensicAnalyzer()
template_validator = TemplateValidator()
content_analyzer = ContentAnalyzer()

app = FastAPI(
    title="IntelliTrust AI Engine",
    description="AI-powered document analysis and verification engine",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "IntelliTrust AI Engine",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    """
    Analyze a document for authenticity and extract information.
    """
    try:
        # Read file content
        content = await file.read()
        file_hash = hashlib.sha256(content).hexdigest()
        
        logger.info(f"Analyzing document: {file.filename}, hash: {file_hash}")
        
        # Save file temporarily
        temp_path = f"/tmp/{file_hash}_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Perform analysis
        analysis_results = {}
        
        # 1. Document type detection
        doc_type = document_analyzer.detect_document_type(temp_path)
        analysis_results["document_type"] = doc_type
        
        # 2. Forensic analysis
        forensic_results = forensic_analyzer.analyze(temp_path)
        analysis_results["forensic_analysis"] = forensic_results
        
        # 3. Template validation
        template_results = template_validator.validate(temp_path, doc_type)
        analysis_results["template_validation"] = template_results
        
        # 4. Content analysis
        content_results = content_analyzer.analyze(temp_path)
        analysis_results["content_analysis"] = content_results
        
        # 5. Overall authenticity score
        authenticity_score = calculate_authenticity_score(analysis_results)
        analysis_results["authenticity_score"] = authenticity_score
        analysis_results["is_authentic"] = authenticity_score > 0.7
        
        # Store results in Redis
        redis_key = f"ai_analysis:{file_hash}"
        redis_client.setex(
            redis_key,
            3600,  # 1 hour expiry
            json.dumps(analysis_results)
        )
        
        # Clean up temp file
        os.remove(temp_path)
        
        return {
            "file_hash": file_hash,
            "filename": file.filename,
            "analysis_results": analysis_results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/analysis/{file_hash}")
async def get_analysis_results(file_hash: str):
    """
    Get analysis results for a document by its hash.
    """
    redis_key = f"ai_analysis:{file_hash}"
    results = redis_client.get(redis_key)
    
    if not results:
        raise HTTPException(status_code=404, detail="Analysis results not found")
    
    return {
        "file_hash": file_hash,
        "analysis_results": json.loads(results),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/batch-analyze")
async def batch_analyze_documents(files: List[UploadFile] = File(...)):
    """
    Analyze multiple documents in batch.
    """
    results = []
    
    for file in files:
        try:
            # Process each file
            content = await file.read()
            file_hash = hashlib.sha256(content).hexdigest()
            
            # Save file temporarily
            temp_path = f"/tmp/{file_hash}_{file.filename}"
            with open(temp_path, "wb") as f:
                f.write(content)
            
            # Perform analysis
            analysis_results = {}
            doc_type = document_analyzer.detect_document_type(temp_path)
            analysis_results["document_type"] = doc_type
            analysis_results["forensic_analysis"] = forensic_analyzer.analyze(temp_path)
            analysis_results["template_validation"] = template_validator.validate(temp_path, doc_type)
            analysis_results["content_analysis"] = content_analyzer.analyze(temp_path)
            
            authenticity_score = calculate_authenticity_score(analysis_results)
            analysis_results["authenticity_score"] = authenticity_score
            analysis_results["is_authentic"] = authenticity_score > 0.7
            
            results.append({
                "filename": file.filename,
                "file_hash": file_hash,
                "analysis_results": analysis_results
            })
            
            # Clean up temp file
            os.remove(temp_path)
            
        except Exception as e:
            logger.error(f"Error analyzing {file.filename}: {str(e)}")
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "batch_results": results,
        "total_files": len(files),
        "successful_analyses": len([r for r in results if "error" not in r]),
        "timestamp": datetime.utcnow().isoformat()
    }

def calculate_authenticity_score(analysis_results: Dict[str, Any]) -> float:
    """
    Calculate overall authenticity score based on analysis results.
    """
    score = 0.0
    weights = {
        "forensic_analysis": 0.4,
        "template_validation": 0.3,
        "content_analysis": 0.3
    }
    
    # Forensic analysis score
    if "forensic_analysis" in analysis_results:
        forensic_score = analysis_results["forensic_analysis"].get("score", 0.0)
        score += forensic_score * weights["forensic_analysis"]
    
    # Template validation score
    if "template_validation" in analysis_results:
        template_score = analysis_results["template_validation"].get("score", 0.0)
        score += template_score * weights["template_validation"]
    
    # Content analysis score
    if "content_analysis" in analysis_results:
        content_score = analysis_results["content_analysis"].get("score", 0.0)
        score += content_score * weights["content_analysis"]
    
    return min(score, 1.0)  # Ensure score doesn't exceed 1.0

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
