""""""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    document_id: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = None
    chunks_count: Optional[int] = None
    error: Optional[str] = None


class ChatRequest(BaseModel):
    question: str = Field(..., description="User question", min_length=1, max_length=1000)
    document_id: Optional[str] = Field(None, description="Restrict retrieval to this document id")


class ChatResponse(BaseModel):
    success: bool
    answer: str
    question: str
    sources: List[Dict[str, Any]] = []
    timestamp: str
    error: Optional[str] = None


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size: int
    upload_time: str
    chunks_count: Optional[int] = None


class DocumentListResponse(BaseModel):
    success: bool
    documents: List[DocumentInfo] = []
    total_count: int = 0
    error: Optional[str] = None


class SearchRequest(BaseModel):
    query: str = Field(..., description="Query", min_length=1, max_length=500)
    limit: int = Field(default=5, description="Number of results", ge=1, le=20)


class SearchResponse(BaseModel):
    success: bool
    results: List[Dict[str, Any]] = []
    query: str
    total_results: int = 0
    error: Optional[str] = None


class StatsResponse(BaseModel):
    success: bool
    total_documents: int = 0
    document_types: Dict[str, int] = {}
    vector_db_size: int = 0
    last_updated: str
    error: Optional[str] = None


class FeedbackRequest(BaseModel):
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="AI answer")
    rating: int = Field(..., description="Rating (1-5)", ge=1, le=5)
    comment: Optional[str] = Field(None, description="Comment", max_length=500)


class FeedbackResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    rag_service_status: str
    vector_db_status: str
    openai_status: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    timestamp: str
