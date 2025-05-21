import json
import pytest
from unittest.mock import MagicMock, patch
from app.core.utils.metadata import fetch_token_metadata

def fake_response(json_data, ok=True):
    class Fake:
        def __init__(self):
            self._json = json_data
            self.ok = ok
        def json(self):
            return self._json
    return Fake()

def test_fetch_metadata_success(monkeypatch, mocker):
    abi = [{"name": "name", "type": "function"},
           {"name": "symbol", "type": "function"},
           {"name": "totalSupply", "type": "function"},
           {"name": "decimals", "type": "function"}]

    # Mock da resposta da API
    monkeypatch.setattr("app.core.utils.metadata.requests.get", lambda url: fake_response({
        "result": [{
            "ABI": json.dumps(abi),
            "ContractName": "Token",
            "TokenName": "TestToken",
            "Symbol": "TT",
            "Owner": "0x123"
        }]
    }))
    
    # Cria um mock para o contrato
    mock_contract = mocker.MagicMock()
    mock_contract.functions = mocker.MagicMock()
    
    # Configura os retornos das funções do contrato
    mock_contract.functions.name.return_value.call.return_value = "TestToken"
    mock_contract.functions.symbol.return_value.call.return_value = "TT"
    mock_contract.functions.totalSupply.return_value.call.return_value = 1000000 * 10**18  # 1M tokens com 18 decimais
    mock_contract.functions.decimals.return_value.call.return_value = 18
    
    # Cria um mock para o Web3
    mock_web3 = mocker.MagicMock()
    mock_web3.eth.contract.return_value = mock_contract
    
    # Aplica o mock ao Web3
    mocker.patch('app.core.utils.metadata.Web3', return_value=mock_web3)
    
    # Executa a função de teste
    result = fetch_token_metadata("0x123")
    
    # Verifica os resultados
    assert result["name"] == "TestToken"
    assert result["symbol"] == "TT"
    assert result["totalSupply"] == 1000000.0  # Deve ser 1M após a divisão por 10^18

def test_fetch_metadata_http_error(monkeypatch):
    monkeypatch.setattr("app.core.utils.metadata.requests.get", lambda url: fake_response({}, ok=False))
    with pytest.raises(Exception, match="BscScan call"):
        fetch_token_metadata("0x123")

def test_fetch_metadata_result_none(monkeypatch):
    monkeypatch.setattr("app.core.utils.metadata.requests.get", lambda url: fake_response({"result": None}))
    with pytest.raises(Exception, match="No data returned"):
        fetch_token_metadata("0x123")

def test_fetch_metadata_result_empty(monkeypatch):
    monkeypatch.setattr("app.core.utils.metadata.requests.get", lambda url: fake_response({"result": []}))
    with pytest.raises(Exception, match="No data returned"):
        fetch_token_metadata("0x123")

def test_fetch_metadata_unverified_contract(monkeypatch):
    monkeypatch.setattr("app.core.utils.metadata.requests.get", lambda url: fake_response({
        "result": [{
            "ABI": "Contract source code not verified"
        }]
    }))
    result = fetch_token_metadata("0x123")
    assert result["name"] == "N/A"
    assert result["symbol"] == "N/A"
    assert result["totalSupply"] == 0

def test_fetch_metadata_web3_error(monkeypatch, mocker):
    # Mock da resposta da API
    monkeypatch.setattr("app.core.utils.metadata.requests.get", lambda url: fake_response({
        "result": [{
            "ABI": "[{}]"
        }]
    }))
    
    # Cria um mock para a função contract que lança uma exceção
    mock_contract = mocker.MagicMock()
    mock_contract.functions = mocker.MagicMock()
    
    # Configura o mock para lançar uma exceção quando chamado
    mock_contract.functions.name.side_effect = Exception("web3 fail")
    
    # Cria um mock para o Web3
    mock_web3 = mocker.MagicMock()
    mock_web3.eth.contract.return_value = mock_contract
    
    # Aplica o mock ao Web3
    mocker.patch('app.core.utils.metadata.Web3', return_value=mock_web3)
    
    # Executa a função de teste
    result = fetch_token_metadata("0x123")
    
    # Verifica os resultados
    assert result["name"] == "N/A"
    assert result["symbol"] == "N/A"
    assert result["totalSupply"] == 0

