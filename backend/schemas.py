from pydantic import BaseModel
from typing import List, Optional


class GenerateContentRequest(BaseModel):
    topic: str
    grade_level: Optional[str] = None


class GenerateContentResponse(BaseModel):
    error: Optional[str] = None
    overview: Optional[str] = None
    key_points: Optional[List[str]] = None
    real_world_example: Optional[str] = None
    flashcards: Optional[List[str]] = None
    summary: Optional[str] = None


class GenerateImageRequest(BaseModel):
    topic: str
    grade_level: Optional[str] = None


class StoreVectorRequest(BaseModel):
    prompt: str
    explanation: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 3


class SearchResult(BaseModel):
    prompt: str
    explanation: str


class SearchResponse(BaseModel):
    results: List[SearchResult]
