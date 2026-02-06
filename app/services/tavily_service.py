import httpx
from app.core.config import settings
from typing import List, Dict, Any

class TavilyService:
    BASE_URL = "https://api.tavily.com/search"

    async def search_ai_news(self) -> List[Dict[str, Any]]:
        payload = {
            "api_key": settings.TAVILY_API_KEY,
            "query": "Artificial Intelligence AI news latest breakthroughs technology",
            "search_depth": "advanced",
            "topic": "news",
            "days": 1,
            "include_images": True
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.BASE_URL, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
            except Exception as e:
                print(f"Error fetching news from Tavily: {e}")
                return []
