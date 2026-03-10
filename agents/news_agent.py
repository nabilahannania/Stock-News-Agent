from typing import TypedDict, Optional, List
import json
import re
from urllib.parse import urlparse
from datetime import datetime

from langgraph.graph import StateGraph, END

from services import search_news, summarize_text

# from llm import llm_gpt
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

    # response = llm_gpt.invoke(prompt)

    # content = response.content

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


def router(state: AgentState):
    logger.info(f"Routing tool for company: {state['company']}")

    if state["company"]:
        return {"tool": "tavily"}

    return {"tool": "tavily"}


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


def extract_source(url: str) -> str:
    try:
        domain = urlparse(url).netloc
        return domain.replace("www.", "")
    except:
        return "unknown"


def format_date(date_str: str):
    if not date_str:
        return None

    try:
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT")
        return dt.strftime("%Y-%m-%d")
    except Exception:
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

        results.append(
            {
                "title": title,
                "source": extract_source(r.get("url", "")),
                "date": format_date(date),
                "summary": summary,
            }
        )

    return {"result": results}


builder = StateGraph(AgentState)

builder.add_node("understand_query", understand_query)
builder.add_node("router", router)
builder.add_node("tavily_tool", tavily_tool)
builder.add_node("format_results", format_results)

builder.set_entry_point("understand_query")

builder.add_edge("understand_query", "router")

builder.add_conditional_edges(
    "router", lambda state: state["tool"], {"tavily": "tavily_tool"}
)

builder.add_edge("tavily_tool", "format_results")

builder.add_edge("format_results", END)

graph = builder.compile()


def run_agent(query: str):

    result = graph.invoke({"query": query})

    return result["result"]
