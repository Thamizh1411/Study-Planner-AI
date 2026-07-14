import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load the backend-specific .env file when starting from the repo root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Study Planner AI"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkeychangeinproduction1234567890!")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./study_planner.db")
    
    # AI Keys and Configs
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "ollama")  # gemini, openai, anthropic, ollama
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4.1-mini") # or gpt-4.1-mini / llama3

    class Config:
        case_sensitive = True

settings = Settings()
