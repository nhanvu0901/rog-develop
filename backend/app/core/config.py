from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Document Processing API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # static folder
    # WEB_FOLDER: str = "/Users/nhanvu/Documents/Learn code/rog-develop/frontend/build"
    WEB_FOLDER: str =r"D:\Python hoc\Tài liệu khóa học\Tài liệu khóa học\Training_RAG\rag-develop\frontend\build"
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # File upload settings
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {"pdf", "docx", "pptx", "xlsx", "csv", "txt"}

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 