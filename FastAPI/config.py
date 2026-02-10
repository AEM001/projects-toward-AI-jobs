from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional

class Settings(BaseSettings):

    database_url:str=Field(default="sqlite:///./test.db",description="Database URL")

    # API settings
    api_title: str = Field(default="Simple Todo API", description="API title")
    api_version: str = Field(default="1.0.0", description="API version")
    api_description: str = Field(default="A production-ready TODO management API built with FastAPI", description="API description")
    debug_mode: bool = Field(default=False, description="Enable debug mode")

    # CORS settings
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:8080"], description="Allowed CORS origins")
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials in CORS")
    cors_allow_methods: List[str] = Field(default=["*"], description="Allowed CORS methods")
    cors_allow_headers: List[str] = Field(default=["*"], description="Allowed CORS headers")

    # Server settings
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
 
# Create global settings instance
settings = Settings()