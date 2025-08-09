from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Vera API"
    APP_DESCRIPTION: str = "A FastAPI backend for the Vera project"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    
    # OpenAI Settings
    OPENAI_API_KEY: str = ""
    
    # LangSmith Settings
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_PROJECT: str = "Vera"
    LANGSMITH_API_KEY: str = ""
    
    # Qdrant Configuration
    QDRANT_MODE: str = "local"  # Options: "memory", "local", "docker", "cloud"
    QDRANT_PATH: str = "./qdrant_storage"  # For local mode
    QDRANT_HOST: str = "localhost"  # For docker mode
    QDRANT_PORT: int = 6333  # For docker mode
    QDRANT_URL: Optional[str] = None  # For cloud mode
    QDRANT_API_KEY: Optional[str] = None  # For cloud mode
    
    # Cloudflare R2 Storage Configuration
    R2_ACCOUNT_ID: Optional[str] = None
    R2_ACCESS_KEY_ID: Optional[str] = None
    R2_SECRET_ACCESS_KEY: Optional[str] = None
    R2_BUCKET_NAME: str = "510k-pdfs"
    R2_PUBLIC_URL_BASE: Optional[str] = None  # Optional custom domain for R2 bucket
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Local frontend
        "http://127.0.0.1:3000",
        "https://*.vercel.app",   # Vercel preview deployments
        "https://vera.vercel.app"  # Production frontend (update this with your actual domain)
    ]
    ALLOWED_METHODS: List[str] = ["*"]
    ALLOWED_HEADERS: List[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True

    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache to prevent multiple reads of environment variables
    """
    return Settings() 