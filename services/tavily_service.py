from tavily import TavilyClient

from core import APPSetting


client = TavilyClient(api_key=APPSetting.TAVILY_API_KEY)


def search_news(query: str):
    results = client.search(query=query, topic="news", days=7)

    return results["results"]
