import pytest
from unittest.mock import patch, MagicMock, call
from fastapi import HTTPException
from app.services.analyzer import analyze_token
from typing import Dict, Any

@pytest.fixture
def mock_metadata():
    return {
        "name": "MockToken",
        "symbol": "MTK",
        "totalSupply": 1000000,
        "owner": "0xABC",
        "functions": ["transfer"],
        "buy_tax": 1.0,
        "sell_tax": 1.0,
        "buy_mutable": False,
        "sell_mutable": False,
        "has_blacklist": False,
        "has_mint": False,
        "lp_info": {"locked": True},
        "deployer_address": "0xABC",
        "deployer_token_count": 1,
        "holders": [{"address": "0x1", "percent": 40.0}]
    }

@pytest.fixture
def mock_static_analysis():
    return {
        "owner": {"renounced": True, "functions": []},
        "functions": []
    }

@pytest.fixture
def mock_dynamic_analysis():
    return {
        "honeypot": {
            "is_honeypot": False,
            "buy_success": True,
            "sell_success": True,
            "high_tax": False,
            "tax_discrepancy": False,
            "error": None
        },
        "fees": {
            "buy": 1.0,
            "sell": 1.0,
            "buy_slippage": 0.5,
            "sell_slippage": 0.5,
            "buy_mutable": False,
            "sell_mutable": False
        }
    }

@pytest.fixture
def mock_onchain_analysis():
    return {
        "deployer": {
            "address": "0xABC",
            "token_history": []
        },
        "top_holders": {
            "holders": [{"address": "0x1", "percentage": "40.00%"}],
            "top_1_percent": 40.0,
            "top_10_percent": 40.0,
            "top_50_percent": 40.0
        },
        "lp_info": {
            "locked": True,
            "percent_locked": 100.0,
            "unlock_date": "2025-12-31"
        },
        "warnings": []
    }

@pytest.fixture
def mock_risk_score():
    return {
        "risk_score": 85,
        "grade": "A",
        "alerts": [],
        "risks": []
    }

@pytest.fixture
def mock_analyzer_dependencies(monkeypatch, mock_metadata, mock_static_analysis, 
                          mock_dynamic_analysis, mock_onchain_analysis, mock_risk_score):
    # Mock das funções de análise
    monkeypatch.setattr("app.services.analyzer.fetch_token_metadata", lambda addr: mock_metadata)
    monkeypatch.setattr("app.services.analyzer.analyze_static", lambda src: mock_static_analysis)
    monkeypatch.setattr("app.services.analyzer.analyze_dynamic", lambda addr: mock_dynamic_analysis)
    monkeypatch.setattr("app.services.analyzer.analyze_onchain", lambda metadata: mock_onchain_analysis)
    monkeypatch.setattr("app.services.analyzer.calculate_risk_score", lambda *_: mock_risk_score)

def test_analyze_token_success(mock_analyzer_dependencies, mock_metadata, mock_onchain_analysis):
    # Testa uma análise bem-sucedida
    result = analyze_token("0x123")
    print("\nResultado da análise:", result)  # Adicionado para depuração
    
    # Verifica as chaves básicas
    assert "name" in result
    assert "symbol" in result
    assert "supply" in result
    assert "score" in result
    assert "honeypot" in result
    assert "fees" in result
    assert "lp_lock" in result
    
    # Verifica os valores básicos
    assert result["name"] == "MockToken"
    assert result["symbol"] == "MTK"
    
    # Verifica a estrutura do score
    assert isinstance(result["score"], dict)
    assert "value" in result["score"]
    assert "label" in result["score"]
    
    # Verifica a estrutura de honeypot
    assert isinstance(result["honeypot"], dict)
    assert "is_honeypot" in result["honeypot"]
    
    # Verifica a estrutura de fees
    assert isinstance(result["fees"], dict)
    assert "buy" in result["fees"]
    assert "sell" in result["fees"]
    
    # Verifica a estrutura de lp_lock
    assert isinstance(result["lp_lock"], dict)
    assert "locked" in result["lp_lock"]
    
    # Verifica se existem top_holders (pode ser None)
    if "top_holders" in result and result["top_holders"] is not None:
        assert isinstance(result["top_holders"], list)
        if len(result["top_holders"]) > 0:
            assert "percentage" in result["top_holders"][0]
    
    # Verifica se existe deployer (pode ser None)
    if "deployer" in result and result["deployer"] is not None:
        assert isinstance(result["deployer"], dict)
        if "address" in result["deployer"]:
            assert isinstance(result["deployer"]["address"], str)

def test_analyze_token_with_lp(mock_analyzer_dependencies, mock_metadata):
    # Testa análise com token de LP
    result = analyze_token("0x123", lp_token_address="0xLP")
    assert result["name"] == "MockToken"
    assert result["lp_lock"]["locked"] is True  # A chave correta é 'lp_lock.locked', não 'lp_locked'

def test_analyze_token_metadata_error(monkeypatch, mock_metadata):
    # Testa erro ao buscar metadados
    error_msg = "Erro de rede"
    monkeypatch.setattr(
        "app.services.analyzer.fetch_token_metadata", 
        lambda addr: (_ for _ in ()).throw(Exception("Erro de rede"))
    )
    
    result = analyze_token("0xERROR")
    print("\nMensagem de erro retornada:", result["risks"][0])  # Para depuração
    assert result["name"] == "Error"
    assert result["score"]["value"] == 0
    assert f"❌ Error processing token: {error_msg}" == result["risks"][0]

def test_analyze_token_static_analysis_error(monkeypatch, mock_metadata):
    # Testa erro na análise estática
    error_msg = "❌ No data returned"
    monkeypatch.setattr("app.services.analyzer.analyze_static", 
                      lambda src: (_ for _ in ()).throw(Exception("❌ No data returned")))
    
    result = analyze_token("0x123")
    print("\nMensagem de erro retornada (estática):", result["risks"][0])  # Para depuração
    assert result["name"] == "Error"
    assert f"❌ Error processing token: {error_msg}" == result["risks"][0]

def test_analyze_token_dynamic_analysis_error(monkeypatch, mock_metadata):
    # Testa erro na análise dinâmica
    error_msg = "❌ No data returned"
    monkeypatch.setattr("app.services.analyzer.analyze_dynamic", 
                      lambda addr: (_ for _ in ()).throw(Exception("❌ No data returned")))
    
    result = analyze_token("0x123")
    print("\nMensagem de erro retornada (dinâmica):", result["risks"][0])  # Para depuração
    assert result["name"] == "Error"
    assert f"❌ Error processing token: {error_msg}" == result["risks"][0]

def test_analyze_token_onchain_analysis_error(monkeypatch, mock_metadata):
    # Testa erro na análise on-chain
    error_msg = "❌ No data returned"
    monkeypatch.setattr("app.services.analyzer.analyze_onchain", 
                      lambda addr: (_ for _ in ()).throw(Exception("❌ No data returned")))
    
    result = analyze_token("0x123")
    print("\nMensagem de erro retornada (on-chain):", result["risks"][0])  # Para depuração
    assert result["name"] == "Error"
    assert f"❌ Error processing token: {error_msg}" == result["risks"][0]

def test_analyze_token_with_exception(monkeypatch):
    monkeypatch.setattr("app.services.analyzer.fetch_token_metadata", lambda address: (_ for _ in ()).throw(Exception("Simulated error")))

    result = analyze_token("0xERROR")

    assert result["name"] == "Error"
    assert result["score"]["value"] == 0
    assert result["risks"]
    assert result["risks"][0].startswith("❌ Error processing token")

def test_analyze_token_raises(monkeypatch):
    def fake_fetch(*args, **kwargs):
        raise Exception("Forced error")
    
    monkeypatch.setattr("app.services.analyzer.fetch_token_metadata", fake_fetch)

    result = analyze_token("0x123")
    assert result["name"] == "Error"
    assert result["score"]["value"] == 0
    assert "❌ Error processing token" in result["risks"][0]

def test_analyze_token_exception(monkeypatch):
    def raise_error(address):
        raise Exception("Forced fetch error")

    monkeypatch.setattr("app.services.analyzer.fetch_token_metadata", raise_error)

    result = analyze_token("0xFAIL")
    assert result["name"] == "Error"
    assert result["symbol"] == "ERR"
    assert result["score"]["value"] == 0
    assert "❌ Error processing token" in result["risks"][0]

def test_analyze_token_with_lp(monkeypatch):
    # 🧪 Simulate minimal metadata with LP
    monkeypatch.setattr("app.services.analyzer.fetch_token_metadata", lambda address: {
        "name": "LPLocked",
        "symbol": "LPL",
        "totalSupply": 1000000,
        "SourceCode": "",
        "deployer_address": "0xABC",
        "deployer_token_count": 1,
        "holders": [],
        "lp_info": {}
    })

    monkeypatch.setattr("app.services.analyzer.analyze_static", lambda src: {})
    monkeypatch.setattr("app.services.analyzer.analyze_dynamic", lambda addr: {})
    monkeypatch.setattr("app.services.analyzer.analyze_onchain", lambda metadata: {
        "top_holders": {"holders": []},
        "deployer": {"address": "0xABC", "token_history": []}
    })
    monkeypatch.setattr("app.services.analyzer.calculate_risk_score", lambda *_: {
        "risk_score": 75, "grade": "B", "alerts": []
    })

    result = analyze_token("0x123", lp_token_address="0xLP")
    assert result["lp_lock"]["locked"] is True
