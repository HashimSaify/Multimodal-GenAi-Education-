from pydantic import BaseModel
from typing import List, Optional


class GenerateContentRequest(BaseModel):
    topic: str
    grade_level: Optional[str] = None


class GenerateContentResponse(BaseModel):
    overview: str
    key_points: List[str]
    real_world_example: str
    flashcards: List[str]
    summary: str


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
