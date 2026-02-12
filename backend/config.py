from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    BETTER_AUTH_SECRET: str
    BETTER_AUTH_URL: str
    GEMINI_API_KEY: str = ""
    OPENROUTER_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()