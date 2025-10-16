from functools import lru_cache
from typing import Optional, List, Any
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = "Inventory Management System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 2000
    API_V1_STR: str = "/api/v1"
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    SIGNED_URL_EXPIRY_TIME: int = 3600
    NUMBER_OF_LOGIN_ATTEMPTS: int = 5
    LOGIN_ATTEMPTS_WINDOW_SECONDS: int = 60
    LOW_STOCK_QUANTITY: int = 10
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key")
    
    
    # CORS settings
    CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://dev.shopdirectpk.com",
        "https://www.dev.shopdirectpk.com",
        "http://beta.shopdirectpk.com",
        "https://beta.shopdirectpk.com"  # Adding both http and https for beta
    ]
    
    
    # Validations
    MIN_LENGTHS_CUSTOMER_DESCRIPTION: int = 5
    MAX_LENGTHS_CUSTOMER_DESCRIPTION: int = 1000
    
    
    
    # ------------------------------------------------------------
    # ------------------------------------------------------------
    # THIS IS FOR CRONJOB IF YOUR PROJECT REQUIREMENTS DOESN'T HAVE THE NEED THEN DELETE THE COMMENTED CODE BELOW
    # ------------------------------------------------------------
    # ------------------------------------------------------------
    
    # Scheduler jobs   
    # LOW_STOCK_WHATSAPP_MSG_JOB_HOUR: int = int(os.getenv("LOW_STOCK_JOB_HOUR", "6"))  # Default: 6 AM
    # LOW_STOCK_WHATSAPP_MSG_JOB_MINUTE: int = int(os.getenv("LOW_STOCK_JOB_MINUTE", "40"))  # Default: 40 minutes
    # SCHEDULER_TIMEZONE: str = os.getenv("SCHEDULER_TIMEZONE", "Asia/Karachi")  # Pakistan timezone
    # ENABLE_SCHEDULER: bool = os.getenv("ENABLE_SCHEDULER", "false").lower() == "true"
    
    
    
    # Rate limit for General API
    MAX_REQUEST_LIMIT_FOR_GENERAL_API: int = 100  # 100 requests
    WINDOW_FOR_GENERAL_API: int = 60
    
    # Rate limit for auth
    MAX_REQUEST_LIMIT_FOR_AUTH: int = 5  # 5 attempts
    WINDOW_FOR_AUTH_API: int = 300 
    
    # ThreadPooling
    MAX_THEADPOOLING_WORKERS: int = 10
    MAX_PROCESSPOOlEXECUTOR: int = 3    

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# This is needed for imports in other files
settings = get_settings()
