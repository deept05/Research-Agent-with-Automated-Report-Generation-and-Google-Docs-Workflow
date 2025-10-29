"""
Configuration management for the research agent application.
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "LangChain Research Agent"
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"
    
    # LangSmith
    langchain_tracing_v2: bool = True
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: str = ""
    langchain_project: str = "research-agent"
    
    # Google APIs
    google_application_credentials: str = ""
    google_docs_folder_id: str = ""
    
    # n8n Integration
    n8n_webhook_url: str = ""
    n8n_api_key: str = ""
    
    # Database
    database_url: str = "sqlite:///./research_agent.db"
    
    # Security
    api_secret_key: str = "your-secret-key-change-in-production"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Rate Limiting
    max_requests_per_minute: int = 10
    
    # Research Settings
    max_search_results: int = 10
    max_content_length: int = 50000
    citation_style: str = "APA"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()