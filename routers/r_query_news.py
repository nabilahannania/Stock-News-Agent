from fastapi import APIRouter

from schemas import QueryRequest, QueryResponse
from agents import run_agent

r_query_news = APIRouter()


@r_query_news.post("/query", response_model=QueryResponse)
def query_news(request: QueryRequest):
    result, tool_used = run_agent(request.query)
    return {"query": request.query, "tool_used": tool_used, "result": result}
