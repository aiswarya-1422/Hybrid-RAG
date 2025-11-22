# api/schemas.py

from pydantic import BaseModel
from typing import List, Optional


class QueryRequest(BaseModel):
    question: str


class SourceChunk(BaseModel):
    text: str
    chapter: str
    page: int
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    retrieval_latency_ms: float
    generation_latency_ms: float
    applied_chapter_filter: Optional[str] = None

