import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from jinja2 import Environment, FileSystemLoader
from app.services.tavily_service import TavilyService
from app.services.qwen_service import QwenService
from app.services.email_service import EmailService

class NewsController:
    def __init__(self):
        self.tavily_service = TavilyService()
        self.qwen_service = QwenService()
        self.email_service = EmailService()
        self.template_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'views/templates'))
        )
        self.executor = ThreadPoolExecutor()

    async def run_news_cycle(self, recipient_email: str):
        print("Starting news cycle...")
        
        # 1. Fetch News (Async)
        print("Fetching news from Tavily...")
        raw_articles = await self.tavily_service.search_ai_news()
        if not raw_articles:
            print("No articles found.")
            return {"status": "error", "message": "No articles found"}
        print(f"Found {len(raw_articles)} articles.")

        # 2. Summarize News (Sync -> Run in Thread)
        print("Summarizing news with Qwen...")
        loop = asyncio.get_event_loop()
        summarized_articles = await loop.run_in_executor(
            self.executor, 
            self.qwen_service.summarize_news, 
            raw_articles
        )
        
        if not summarized_articles:
            print("Failed to summarize articles.")
            return {"status": "error", "message": "Failed to summarize articles"}
        print("Summarization complete.")

        # 3. Render HTML (Sync, fast enough, but can be threaded)
        print("Rendering HTML...")
        template = self.template_env.get_template('newsletter.html')
        html_content = template.render(articles=summarized_articles)

        # 4. Send Email (Sync, network I/O -> Run in Thread)
        print(f"Sending email to {recipient_email}...")
        try:
            await loop.run_in_executor(
                self.executor,
                lambda: self.email_service.send_email(
                    to_email=recipient_email,
                    subject="每日 AI 新闻简报",
                    html_content=html_content
                )
            )
            print("News cycle completed successfully.")
            return {"status": "success", "message": "Email sent successfully"}
        except Exception as e:
            print(f"Failed to send email: {e}")
            return {"status": "error", "message": str(e)}

news_controller = NewsController()
