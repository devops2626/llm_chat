import os
import trafilatura
from serpapi import GoogleSearch

class SearchOrganizer:
    def __init__(self, search_api_key: str = None):
        self.search_api_key = search_api_key or os.getenv("SERPAPI_API_KEY")

    def web_search(self, query: str, num_results: int = 5) -> str:
        params = {
            "q": query,
            "api_key": self.search_api_key,
            "engine": "google",
            "num": num_results
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        organic = results.get("organic_results", [])

        formatted = []
        for item in organic[:num_results]:
            formatted.append(f"Title: {item.get('title')}\nSnippet: {item.get('snippet')}\nURL: {item.get('link')}\n")
        return "\n".join(formatted) if formatted else "No results found."

    def extract_content(self, url: str) -> str:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return "Could not fetch the URL."
        text = trafilatura.extract(downloaded)
        return text if text else "No extractable content."
