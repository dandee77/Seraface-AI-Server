"""
Configuration settings for the Seraface AI Server
"""
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    """Application settings"""
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # Database Configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "seraface")
    PRODUCTS_COLLECTION: str = os.getenv("PRODUCTS_COLLECTION", "products_cache")
    
    # API Configuration
    API_VERSION: str = os.getenv("API_VERSION", "v1")
    API_PREFIX: str = f"/api/{API_VERSION}"
    
    # Application Info
    APP_TITLE: str = os.getenv("APP_TITLE", "Seraface AI Server")
    APP_DESCRIPTION: str = os.getenv("APP_DESCRIPTION", "API for skincare product management")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")

    def __init__(self):
        if env_path.exists():
            print("Environment variables loaded.")
        else:
            print("No .env file found, using default settings.")


settings = Settings()
