from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    question: str = Field(..., example="What government schemes can help with Citrus Canker?")
    session_id: Optional[str] = Field(None, example="user-123")

class Source(BaseModel):
    document: str
    page: Any

class QueryResponse(BaseModel):
    success: bool
    intent: str
    answer: str
    sources: List[Source]

class FeedbackRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    is_satisfied: bool
    correct_info: Optional[str] = None # Optional correction from user

class FeedbackResponse(BaseModel):
    success: bool
    message: str
