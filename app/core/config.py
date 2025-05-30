"""Application Configuration

This module contains all configuration settings for the BNBGuard API.
Handles pydantic-settings compatibility issues automatically.
"""

import os
from typing import List, Optional, Union

# Handle pydantic-settings import with fallback for compatibility
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    PYDANTIC_V2 = True
except ImportError:
    try:
        from pydantic import BaseSettings
        PYDANTIC_V2 = False
        SettingsConfigDict = None
    except ImportError:
        raise ImportError(
            "Neither pydantic-settings nor pydantic BaseSettings could be imported. "
            "Please install: pip install pydantic-settings==2.1.0"
        )

from pydantic import Field, validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables with automatic conflict resolution."""
    
    # API Configuration
    API_TITLE: str = "BNBGuard API"
    API_DESCRIPTION: str = "Automated risk analysis for BNB Chain tokens"
    API_VERSION: str = "1.0.0"
    API_HOST: str = Field(default="0.0.0.0", description="API host address")
    API_PORT: int = Field(default=3000, description="API port")
    API_WORKERS: int = Field(default=1, description="Number of workers")
    
    # BSC Configuration (required)
    BSCSCAN_API_KEY: str = Field(default="your_bscscan_api_key_here", description="BSCScan API key for contract verification")
    BSC_RPC_URL: str = Field(
        default="https://bsc-dataseed.binance.org",
        description="Primary BSC RPC URL"
    )
    BSC_RPC_URL_BACKUP: str = Field(
        default="https://bsc-dataseed1.defibit.io",
        description="Backup BSC RPC URL"
    )
    
    # PancakeSwap Configuration
    PANCAKESWAP_ROUTER_V2: str = Field(
        default="0x10ED43C718714eb63d5aA57B78B54704E256024E",
        description="PancakeSwap V2 Router address"
    )
    PANCAKESWAP_FACTORY_V2: str = Field(
        default="0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73",
        description="PancakeSwap V2 Factory address"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json/text)")
    
    # Security Configuration
    CORS_ORIGINS: str = Field(default="*", description="CORS allowed origins")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Rate limit requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")
    
    # Cache Configuration
    CACHE_TTL: int = Field(default=300, description="Cache TTL in seconds")
    CACHE_MAX_SIZE: int = Field(default=1000, description="Maximum cache size")
    
    # Analysis Configuration
    MAX_ANALYSIS_TIME: int = Field(default=30, description="Maximum analysis time in seconds")
    HONEYPOT_SIMULATION_AMOUNT: float = Field(
        default=0.01, 
        description="Amount in BNB for honeypot simulation"
    )
    
    # Advanced Analysis Settings
    ENABLE_ADVANCED_SCORING: bool = Field(default=True, description="Enable advanced scoring system")
    ENABLE_DETAILED_LOGGING: bool = Field(default=True, description="Enable detailed analysis logging")
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, value: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        value = value.upper()
        if value not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return value
    
    # Property to get CORS origins as list
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.CORS_ORIGINS, str):
            if self.CORS_ORIGINS == "*":
                return ["*"]
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    
    # Pydantic v2 configuration
    if PYDANTIC_V2 and SettingsConfigDict:
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=True,
            extra="ignore",  # Ignore extra fields to prevent validation errors
            validate_assignment=True
        )
    else:
        # Pydantic v1 configuration
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = True
            extra = "ignore"

# Create global settings instance with error handling
try:
    settings = Settings()
    print(f"✅ Configuração carregada: {settings.API_TITLE}")
except Exception as e:
    # Provide helpful error message for common issues
    if "BSCSCAN_API_KEY" in str(e):
        print("❌ BSCSCAN_API_KEY não configurada!")
        print("📝 Por favor:")
        print("1. Copie env.example para .env")
        print("2. Obtenha uma API key em https://bscscan.com/apis")
        print("3. Configure BSCSCAN_API_KEY no arquivo .env")
        # Don't raise, just use default
        settings = Settings(BSCSCAN_API_KEY="your_bscscan_api_key_here")
    else:
        print(f"❌ Erro na configuração: {e}")
        raise

# Export for compatibility
__all__ = ["settings", "Settings"]
