# Stock-News-Agent

A simple AI agent backend that routes natural language queries about US-listed companies to a browsing tool and returns recent news.

## Tech Stack

- FastAPI
- LangGraph
- OpenAI LLM
- Tavily Search API
- Docker

## Features

1. Accepts natural language queries about companies or ticker symbols
2. Uses an LLM to identify the referenced company or ticker
3. Routes the query to a search tool
4. Summarizes the retrieved news content using an LLM, with summaries focused on the identified company
5. Returns structured, recent news results in JSON format

## Pipeline
```
User Query
     ↓
understand_query (LLM extraction)
     ↓
router
     ↓
tavily search
     ↓
summarize
     ↓
structured output
```

## Run with Docker
1. Clone the repository

```
git clone https://github.com/yourusername/stock-news-agent.git
cd stock-news-agent
```

2. Create the environment file

```
cp .env.example .env
```

3. Add required API keys to .env

4. Build the Docker containers

```
docker compose build
```

5. Start the application

```
docker compose up
```

6. Open the API documentation

```
http://localhost:8000/stock-news/documentation
```

## To Use
Open the API documentation:

```
http://localhost:8000/stock-news/documentation
```

Or send a request with curl:

```
curl -X POST "http://localhost:8000/query" \
-H "Content-Type: application/json" \
-d '{"query":"What is the latest news on Nvidia?"}'
```

## API Endpoint
POST /query

Request:
```
{
  "query": "Give me recent updates on Apple stock."
}
```

Example response:
```
{
  "query": "Give me recent updates on Apple stock.",
  "tool_used": "tavily",
  "result": [
    {
      "title": "MediWound: BARDA Contract Reinstatement, Capacity Expansion, and EscharEx Pipeline Catalysts Support Long-Term Buy Thesis - TipRanks",
      "source": "tipranks.com",
      "date": "2026-03-06",
      "summary": "Apple Inc. (AAPL) has received a new 'street-high' price target from Wedbush, indicating positive sentiment among analysts regarding the stock's potential. This development highlights ongoing confidence in Apple's market performance."
    },
    {
      "title": "Nvidia and AMD Stock Dip as U.S. Drafts Global AI Chip Export Permits - TipRanks",
      "source": "tipranks.com",
      "date": "2026-03-06",
      "summary": "Apple Inc. (AAPL) recently received a new street-high price target from Wedbush, indicating positive sentiment among analysts. The article primarily discusses the impact of U.S. regulations on AI chip exports, but does not elaborate on how this may affect Apple directly."
    },
    {
      "title": "Sphere 3D Cuts Costs, Upgrades Fleet as It Prepares Merger With Cathedra Bitcoin - TipRanks",
      "source": "tipranks.com",
      "date": "2026-03-07",
      "summary": "Apple Inc. (AAPL) has received a new street-high price target from Wedbush, indicating positive sentiment among analysts regarding the stock's potential. This follows a trend of favorable analyst ratings for AAPL, reflecting confidence in the company's performance and market position."
    },
    {
      "title": "NVDA vs. AVGO: Why Investors Liked Broadcom’s Earnings More Than Nvidia’s - TipRanks",
      "source": "tipranks.com",
      "date": "2026-03-06",
      "summary": "Apple Inc. (AAPL) recently received a new street-high price target from Wedbush, indicating positive sentiment among analysts regarding the company's future performance. This development comes amid broader market reactions to earnings reports from other tech companies, highlighting AAPL's strong position in the market."
    },
    {
      "title": "Nvidia and AMD Stocks Drop after Report of New U.S. Rules Requiring Approval for AI Chip Exports - TipRanks",
      "source": "tipranks.com",
      "date": "2026-03-05",
      "summary": "Apple Inc. (AAPL) received a new street-high price target from Wedbush, indicating positive analyst sentiment towards the stock. The article primarily discusses the impact of new U.S. rules on AI chip exports affecting Nvidia and AMD, with no further details on Apple's performance or market position."
    }
  ]
}
```

## Screenshot Sample input/output

![Input example](assets/input.png)

![Output example](assets/output.png)
