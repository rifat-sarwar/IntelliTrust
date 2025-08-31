from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class AIAnalysisCreate(BaseModel):
    document_id: int
    analysis_type: str = "comprehensive"
    parameters: Optional[Dict[str, Any]] = None

class AIAnalysisResponse(BaseModel):
    document_id: int
    status: str
    message: Optional[str] = None
    analysis_results: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    is_authentic: Optional[bool] = None
    processing_time: Optional[float] = None
    created_at: Optional[datetime] = None

class AIAnalysisResult(BaseModel):
    id: int
    document_id: int
    analysis_type: str
    results: Dict[str, Any]
    confidence_score: float
    is_authentic: bool
    processing_time: float
    created_at: datetime

    class Config:
        from_attributes = True
