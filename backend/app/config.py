"""Configuration Management"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4-turbo"
    
    # Database Configuration
    database_url: str = "sqlite:///./test.db"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT Configuration
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # WeChat Configuration
    wechat_appid: str = ""
    wechat_secret: str = ""
    wechat_mchid: str = ""
    
    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    debug: bool = True
    
    # File Upload Configuration
    max_upload_size: int = 10485760  # 10MB
    upload_dir: str = "./uploads"
    
    # AI Configuration
    ocr_model: str = "PaddleOCR"
    image_quality_threshold: float = 0.6
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()


if __name__ == "__main__":
    settings = get_settings()
    print(f"Database URL: {settings.database_url}")
    print(f"Server running on: {settings.server_host}:{settings.server_port}")
