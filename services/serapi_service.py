from serpapi import GoogleSearch

from core import APPSetting


def search_news_serpapi(query: str):

    params = {
        "engine": "google",
        "q": query,
        "tbm": "nws",      # news search
        "tbs": "qdr:w",    # past week
        "api_key": APPSetting.SERPAPI_KEY,
        "hl": "en",
        "gl": "us",
    }

    search = GoogleSearch(params)

    results = search.get_dict()

    news_results = results.get("news_results", [])

    articles = []

    for item in news_results:

        articles.append(
            {
                "title": item.get("title"),
                "url": item.get("link"),
                "source": item.get("source"),
                "date": item.get("published_at"),
                "content": item.get("snippet"),
                "raw_content": None,
            }
        )

    return articles