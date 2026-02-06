from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TAVILY_API_KEY: str
    DASHSCOPE_API_KEY: str
    SMTP_SERVER: str
    SMTP_PORT: int = 465
    SMTP_USER: str
    SMTP_PASSWORD: str
    SENDER_EMAIL: str
    RECIPIENT_EMAIL: str = "kingfunhuang@163.com"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
