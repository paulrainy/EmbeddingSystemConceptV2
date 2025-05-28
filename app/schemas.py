from typing import List

from pydantic import BaseModel, Field


# ----- ingest -----
class TestCaseIn(BaseModel):
    direction: str
    section: str
    name: str
    steps: str
    expected: str


# ----- search -----
class SearchQuery(BaseModel):
    query: str = Field(..., min_length=3, example="Проверка авторизации")
    top_k: int = Field(10, ge=1, le=100)


class SearchHit(BaseModel):
    id: int
    score: float
    snippet: str


class SearchResponse(BaseModel):
    hits: List[SearchHit]
