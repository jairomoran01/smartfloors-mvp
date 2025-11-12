from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://admin:admin@localhost:5432/smartfloors"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # API Keys
    GEMINI_API_KEY: Optional[str] = None
    
    # App Settings
    APP_NAME: str = "SmartFloors API"
    APP_VERSION: str = "0.0.1"
    DEBUG: bool = False
    
    # Prediction Settings
    PREDICTION_HORIZON_MINUTES: int = 60
    PREDICTION_WINDOW_HOURS: int = 4
    
    # Alert Settings
    ALERT_POLLING_INTERVAL_SECONDS: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

