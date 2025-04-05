# app/models/assessment.py
from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class Assessment(BaseModel):
    id: str
    name: str
    url: HttpUrl
    remote_testing_support: bool
    adaptive_irt_support: bool
    duration: str
    test_type: str
    description: Optional[str] = None
    
class JobDescription(BaseModel):
    text: Optional[str] = None
    url: Optional[HttpUrl] = None
    
class RecommendationResult(BaseModel):
    assessment: Assessment
    score: float
    relevance_explanation: str