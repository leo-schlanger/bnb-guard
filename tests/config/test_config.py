import pytest
import os

# TODO: Adicionar mais testes para as variáveis de configuração

def test_config_loaded():
    """Testa se a configuração foi carregada corretamente."""
    # Importa diretamente o módulo de configuração da raiz
    import config
    
    # Verifica se as variáveis de configuração estão definidas
    assert hasattr(config, 'BSCSCAN_API_KEY') is True
    assert hasattr(config, 'BSC_RPC_URL') is True
    assert config.BSC_RPC_URL == "https://bsc-dataseed.binance.org"
