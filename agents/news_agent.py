from typing import TypedDict, Optional, List
import json
import re
from urllib.parse import urlparse
from datetime import datetime

from langgraph.graph import StateGraph, END

from services import search_news, summarize_text, search_news_serpapi

from llm import client
from core import logger


class AgentState(TypedDict):

    query: str
    company: Optional[str]
    ticker: Optional[str]

    tool: Optional[str]

    raw_results: Optional[list]
    result: Optional[List[dict]]


def clean_json(text: str) -> str:
    # remove ```json ``` or ``` blocks
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()


def understand_query(state: AgentState):
    logger.info(f"User query received: {state['query']}")

    prompt = f"""
Extract the company name and ticker symbol from the query.

Query: {state['query']}

Return JSON format:

{{
"company": "...",
"ticker": "..."
}}
"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You extract stock companies and tickers."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    content = response.choices[0].message.content

    logger.info(f"GPT Response: {content}")

    try:
        parsed = json.loads(clean_json(content))
    except:
        logger.warning("Failed to parse JSON from LLM")
        parsed = {"company": state["query"], "ticker": None}

    logger.info(
        f"Parsed company: {parsed.get('company')}, ticker: {parsed.get('ticker')}"
    )

    return {"company": parsed.get("company"), "ticker": parsed.get("ticker")}

def choose_tool(state: AgentState):

    prompt = f"""
You are an AI agent choosing the best search tool.

Available tools:

1. tavily
- Best for recent news
- Optimized for AI

2. serpapi
- Google search
- Better for general information

User query:
{state["query"]}

Return JSON:

{{
"tool": "tavily" or "serpapi"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You decide which search tool is best."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    content = response.choices[0].message.content
    logger.info(f"GPT Response: {content}")

    try:
        parsed = json.loads(content)
        tool = parsed.get("tool", "tavily")
    except:
        logger.warning("Failed to parse JSON from LLM")
        tool = "tavily"

    return {"tool": tool}


def tavily_tool(state: AgentState):
    company = state.get("company")
    ticker = state.get("ticker")
    if ticker:
        query = f"{company} {ticker} stock news"
    else:
        query = f"{company} stock news"

    logger.info(f"Calling Tavily search for: {query}")

    news = search_news(query)

    logger.info(f"Tavily returned {len(news)} results")
    # logger.info(news)

    for i, item in enumerate(news):
        logger.info(f"Result {i+1}: {item['title']} | {item['url']}")

    return {"raw_results": news}

def serpapi_tool(state: AgentState):
    company = state.get("company")
    ticker = state.get("ticker")
    if ticker:
        query = f"{company} {ticker} stock news"
    else:
        query = f"{company} stock news"

    logger.info(f"Calling SerpAPI search for: {query}")

    news = search_news_serpapi(query)

    logger.info(f"SerpAPI returned {len(news)} results")
    # logger.info(news)

    for i, item in enumerate(news):
        logger.info(f"Result {i+1}: {item['title']} | {item['url']}")

    return {"raw_results": news}


def extract_source(url: str) -> str:
    try:
        domain = urlparse(url).netloc
        return domain.replace("www.", "")
    except:
        return "unknown"
    
    
def format_date(date_str: str):
    if not date_str:
        return None

    formats = [
        "%a, %d %b %Y %H:%M:%S GMT",   # Wed, 04 Mar 2026 12:50:57 GMT
        "%Y-%m-%d %H:%M:%S UTC",       # 2026-03-04 12:50:57 UTC
        "%Y-%m-%dT%H:%M:%S",           # ISO basic
        "%Y-%m-%d"                     # already formatted
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return date_str


def format_results(state: AgentState):
    company = state.get("company")
    ticker = state.get("ticker")

    results = []

    for r in state.get("raw_results", []):
        title = r.get("title", "")
        content = r.get("content", "")
        date = r.get("published_date") or r.get("date")
        summary = summarize_text(title, content, company, ticker)

        source = r.get("source", extract_source(r.get("url", "")))

        results.append(
            {
                "title": title,
                "source": source,
                "date": format_date(date),
                "summary": summary,
            }
        )

    return {"result": results}


builder = StateGraph(AgentState)

builder.add_node("understand_query", understand_query)
builder.add_node("choose_tool", choose_tool)
builder.add_node("tavily_tool", tavily_tool)
builder.add_node("serpapi_tool", serpapi_tool)
builder.add_node("format_results", format_results)

builder.set_entry_point("understand_query")

builder.add_edge("understand_query", "choose_tool")

builder.add_conditional_edges(
    "choose_tool", lambda state: state["tool"], {"tavily": "tavily_tool", "serpapi": "serpapi_tool"}
)

builder.add_edge("tavily_tool", "format_results")
builder.add_edge("serpapi_tool", "format_results")

builder.add_edge("format_results", END)

graph = builder.compile()


def run_agent(query: str):

    result = graph.invoke({"query": query})

    return result["result"], result["tool"]
