"""
Pydantic models for request/response schemas.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ResearchStatus(str, Enum):
    """Research job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchRequest(BaseModel):
    """Research query request."""
    query: str = Field(..., min_length=5, max_length=500, description="Research query")
    user_id: Optional[str] = Field(None, description="User identifier")
    max_results: Optional[int] = Field(10, ge=1, le=20, description="Maximum search results")
    include_citations: bool = Field(True, description="Include citations in report")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What are the latest developments in quantum computing?",
                "user_id": "user123",
                "max_results": 10,
                "include_citations": True
            }
        }


class Citation(BaseModel):
    """Citation information."""
    source: str
    url: Optional[str] = None
    title: Optional[str] = None
    accessed_date: str
    snippet: Optional[str] = None


class ResearchResult(BaseModel):
    """Individual research result."""
    title: str
    url: str
    snippet: str
    relevance_score: Optional[float] = None
    content: Optional[str] = None


class ResearchResponse(BaseModel):
    """Research job response."""
    job_id: str
    status: ResearchStatus
    query: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    google_doc_url: Optional[str] = None
    summary: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": "abc123",
                "status": "completed",
                "query": "Quantum computing developments",
                "created_at": "2025-01-01T12:00:00",
                "completed_at": "2025-01-01T12:05:00",
                "google_doc_url": "https://docs.google.com/document/d/...",
                "summary": "Recent developments in quantum computing include..."
            }
        }


class ResearchReport(BaseModel):
    """Complete research report."""
    title: str
    query: str
    executive_summary: str
    sections: List[Dict[str, Any]]
    citations: List[Citation]
    generated_at: datetime
    metadata: Dict[str, Any] = {}


class JobStatusResponse(BaseModel):
    """Job status check response."""
    job_id: str
    status: ResearchStatus
    progress: Optional[str] = None
    google_doc_url: Optional[str] = None
    error_message: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    services: Dict[str, bool] = {}