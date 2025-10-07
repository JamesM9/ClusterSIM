from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    agent_api_key: str = "agent-registration-key"
    
    # Database
    database_url: str = "sqlite:///./controller.db"
    # For production: "postgresql://user:password@localhost/dbname"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Agent settings
    agent_timeout: int = 30
    agent_verify_ssl: bool = False  # Set to True in production
    
    class Config:
        env_file = ".env"


settings = Settings()
