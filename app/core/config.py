"""Application configuration settings."""
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Union

class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = "BNBGuard API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for analyzing and auditing BSC token contracts"
    DEBUG: bool = False
    ENV: str = "production"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    API_KEY: str = "your-secret-api-key"  # Change in production
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost", "http://localhost:8000", "http://localhost:3000"]
    
    # Contact information
    CONTACT_NAME: str = "BNBGuard Support"
    CONTACT_EMAIL: str = "support@bnbguard.com"
    CONTACT_URL: str = "https://bnbguard.com/support"
    
    # License information
    LICENSE_NAME: str = "MIT"
    LICENSE_URL: str = "https://opensource.org/licenses/MIT"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Token analysis settings
    MAX_TOKENS_PER_DAY: int = 1000
    REQUEST_TIMEOUT: int = 30
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        if isinstance(v, list):
            return v
        return []
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()
