"""
Shared configuration settings for the TDS Project.
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Student Configuration
    student_secret: str = ""
    student_email: str = ""
    
    # GitHub Configuration
    github_token: str = ""
    github_username: str = ""
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_provider: str = "openai"  # openai or anthropic
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Database Configuration
    database_url: str = "sqlite:///./tds_project.db"
    
    # Evaluation API Configuration
    evaluation_api_url: str = ""
    evaluation_api_host: str = "0.0.0.0"
    evaluation_api_port: int = 8001
    
    # Playwright Configuration
    headless: bool = True
    timeout: int = 15000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
