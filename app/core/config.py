"""Application Configuration

This module contains all configuration settings for the BNBGuard API.
"""

import os
from typing import List, Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_TITLE: str = "BNBGuard API"
    API_DESCRIPTION: str = "Automated risk analysis for BNB Chain tokens"
    API_VERSION: str = "1.0.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 3000
    API_WORKERS: int = 1
    
    # BSC Configuration
    BSCSCAN_API_KEY: str
    BSC_RPC_URL: str = "https://bsc-dataseed.binance.org"
    BSC_RPC_URL_BACKUP: str = "https://bsc-dataseed1.defibit.io"
    
    # PancakeSwap Configuration
    PANCAKESWAP_ROUTER_V2: str = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
    PANCAKESWAP_FACTORY_V2: str = "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Security Configuration
    CORS_ORIGINS: List[str] = ["*"]
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Cache Configuration
    CACHE_TTL: int = 300  # seconds
    CACHE_MAX_SIZE: int = 1000
    
    # Analysis Configuration
    MAX_ANALYSIS_TIME: int = 30  # seconds
    HONEYPOT_SIMULATION_AMOUNT: float = 0.01  # BNB
    
    # Database Configuration (for future use)
    DATABASE_URL: Optional[str] = None
    
    @validator("BSCSCAN_API_KEY")
    def validate_bscscan_api_key(cls, v):
        if not v:
            raise ValueError("BSCSCAN_API_KEY is required")
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {valid_levels}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env

# Global settings instance
settings = Settings()

# Legacy compatibility - keep the old variables for backward compatibility
BSCSCAN_API_KEY = settings.BSCSCAN_API_KEY
BSC_RPC_URL = settings.BSC_RPC_URL
