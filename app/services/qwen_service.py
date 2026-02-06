import json
import dashscope
from app.core.config import settings
from typing import List, Dict, Any

class QwenService:
    def __init__(self):
        dashscope.api_key = settings.DASHSCOPE_API_KEY

    def summarize_news(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not articles:
            return []
            
        # Prepare content for the model
        articles_text = ""
        for i, art in enumerate(articles):
            articles_text += f"{i+1}. Title: {art.get('title')}\n   URL: {art.get('url')}\n   Content: {art.get('content')}\n\n"
            
        prompt = (
            "You are a professional news editor for a Chinese audience. I will provide you with a list of recent AI news articles (mostly in English). "
            "Please analyze them, de-duplicate similar stories, and summarize the most important ones into **Chinese**. "
            "Return the result as a JSON string containing a list of objects. "
            "Each object must have the following keys: 'title' (a concise headline in Chinese), 'summary' (a brief paragraph in Chinese), 'source' (source name), and 'url' (original link). "
            "The JSON should be a list of these objects, nothing else. Do not wrap in markdown code blocks."
            f"\n\nArticles:\n{articles_text}"
        )

        try:
            # Using qwen-plus or qwen-max for better quality, or qwen-turbo for speed. 
            # Let's default to qwen-plus for a good balance.
            response = dashscope.Generation.call(
                model='qwen-plus', 
                prompt=prompt,
                result_format='message',
            )
            
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                # Clean up potential markdown formatting
                content = content.replace("```json", "").replace("```", "").strip()
                return json.loads(content)
            else:
                print(f"Qwen API Error: {response.code} - {response.message}")
                return []
        except Exception as e:
            print(f"Error summarizing news with Qwen: {e}")
            # Fallback: just return original titles if AI fails
            fallback = []
            for art in articles[:5]:
                fallback.append({
                    "title": art.get("title"),
                    "summary": art.get("content")[:200] + "...",
                    "source": "Unknown",
                    "url": art.get("url")
                })
            return fallback
