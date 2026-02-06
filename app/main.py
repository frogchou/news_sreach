from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.api.routes import router
from app.controller import news_controller
from app.core.config import settings

# Scheduler setup
scheduler = AsyncIOScheduler()

async def scheduled_news_job():
    print("Running scheduled job: Sending news to default recipient.")
    await news_controller.run_news_cycle(settings.RECIPIENT_EMAIL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start scheduler
    # 'cron', hour=8, minute=0 means every day at 8:00 AM
    scheduler.add_job(scheduled_news_job, 'cron', hour=8, minute=0)
    scheduler.start()
    print("Scheduler started.")
    yield
    # Shutdown scheduler
    scheduler.shutdown()
    print("Scheduler shut down.")

app = FastAPI(title="AI News Bot", lifespan=lifespan)

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to AI News Bot API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
