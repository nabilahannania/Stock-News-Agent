from pydantic import BaseModel
from typing import List, Optional


class QueryRequest(BaseModel):
    query: str


class NewsItem(BaseModel):
    title: str
    source: str
    date: str
    summary: Optional[str]


class QueryResponse(BaseModel):
    query: str
    tool_used: str
    result: List[NewsItem]
