from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.api.routes import router
from app.controller import news_controller
from app.core.config import settings
import os
from zoneinfo import ZoneInfo

# Scheduler setup
scheduler = AsyncIOScheduler()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "views/templates"))

async def scheduled_news_job():
    print(f"Running scheduled job: Sending news to {settings.RECIPIENT_EMAIL}")
    await news_controller.run_news_cycle(settings.RECIPIENT_EMAIL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start scheduler
    # 'cron', hour=8, minute=0 means every day at 8:00 AM (Asia/Shanghai)
    try:
        scheduler.add_job(scheduled_news_job, 'cron', hour=8, minute=0, timezone=ZoneInfo("Asia/Shanghai"))
        scheduler.start()
        print("Scheduler started. Job scheduled for 08:00 Asia/Shanghai daily.")
    except Exception as e:
        print(f"Error starting scheduler: {e}")
    
    yield
    # Shutdown scheduler
    scheduler.shutdown()
    print("Scheduler shut down.")

app = FastAPI(title="AI News Bot", lifespan=lifespan)

app.include_router(router, prefix="/api")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
