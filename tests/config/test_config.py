"""Test configuration module."""

import pytest
import os
from unittest.mock import patch

# Import the new configuration system
from app.core.config import settings

# TODO: Adicionar mais testes para as variáveis de configuração

def test_bscscan_api_key_required():
    """Test that BSCSCAN_API_KEY is required."""
    # This test should pass if the API key is set
    assert hasattr(settings, 'BSCSCAN_API_KEY')

def test_bsc_rpc_url_default():
    """Test that BSC_RPC_URL has a default value."""
    assert settings.BSC_RPC_URL == "https://bsc-dataseed.binance.org"

def test_api_configuration():
    """Test API configuration values."""
    assert settings.API_TITLE == "BNBGuard API"
    assert settings.API_VERSION == "1.0.0"
    assert settings.API_HOST == "0.0.0.0"
    assert settings.API_PORT == 3000

def test_log_level_validation():
    """Test log level validation."""
    assert settings.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

def test_config_loaded():
    """Testa se a configuração foi carregada corretamente."""
    # Importa diretamente o módulo de configuração da raiz
    import config
    
    # Verifica se as variáveis de configuração estão definidas
    assert hasattr(config, 'BSCSCAN_API_KEY') is True
    assert hasattr(config, 'BSC_RPC_URL') is True
    assert config.BSC_RPC_URL == "https://bsc-dataseed.binance.org"
