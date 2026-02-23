from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI TODO API"
    app_version: str = "1.0.0"
    debug: bool = True

    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./todo.db"

    cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]

    class Config:
        env_file = '.env'
        case_sensitive = False
    
settings = Settings()