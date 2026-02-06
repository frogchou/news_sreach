from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from app.controller import news_controller

router = APIRouter()

class EmailRequest(BaseModel):
    email: EmailStr

@router.post("/send-news")
async def send_news(request: EmailRequest, background_tasks: BackgroundTasks):
    """
    Trigger sending the AI news summary to the specified email.
    """
    # Run in background to not block the response
    background_tasks.add_task(news_controller.run_news_cycle, request.email)
    return {"message": f"News sending process started for {request.email}"}
