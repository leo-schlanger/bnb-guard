import pytest
from unittest.mock import patch, MagicMock

from app.core.analyzers.onchain_analyzer import (
    get_deployer_address,
    get_holder_distribution,
    is_lp_locked,
    analyze_onchain
)

# 🔧 Fixed generic mock utility
def fake_response(json_data, ok=True, status_code=200):
    class _Fake:
        def __init__(self):
            self._json = json_data
            self.ok = ok
            self.status_code = status_code

        def json(self):
            return self._json

    return _Fake()


# --- REAL TEST (optional) ---
@pytest.mark.skip(reason="Teste real pode falhar por instabilidade externa")
def test_get_deployer_address_real():
    token = "0xe9e7cea3dedca5984780bafc599bd69add087d56"
    result = get_deployer_address(token)
    assert result.startswith("0x") and len(result) == 42


# --- get_deployer_address MOCKS ---
def test_get_deployer_address_mock_success(monkeypatch):
    monkeypatch.setattr(
        "app.core.analyzers.onchain_analyzer.requests.get",
        lambda url: fake_response({
            "status": "1",
            "message": "OK",
            "result": [{"contractCreator": "0xDEADBEEF"}]
        })
    )
    result = get_deployer_address("0x123")
    assert result == "0xDEADBEEF"

def test_get_deployer_address_mock_not_found(monkeypatch):
    monkeypatch.setattr(
        "app.core.analyzers.onchain_analyzer.requests.get",
        lambda url: fake_response({"result": [{}]})
    )
    with pytest.raises(Exception, match=".*"):
        get_deployer_address("0x123")

def test_get_deployer_address_http_error(monkeypatch):
    monkeypatch.setattr(
        "app.core.analyzers.onchain_analyzer.requests.get",
        lambda url: fake_response({}, ok=False, status_code=500)
    )
    with pytest.raises(Exception, match=".*"):
        get_deployer_address("0x123")


# --- get_holder_distribution MOCKS ---
def test_get_holder_distribution_success(monkeypatch):
    monkeypatch.setattr(
        "app.core.analyzers.onchain_analyzer.requests.get",
        lambda url: fake_response({
            "status": "1",
            "message": "OK",
            "result": [
                {"TokenHolderAddress": "0x1", "TokenHolderQuantity": "40000000000000000000"},
                {"TokenHolderAddress": "0x2", "TokenHolderQuantity": "30000000000000000000"},
                {"TokenHolderAddress": "0x3", "TokenHolderQuantity": "10000000000000000000"},
                {"TokenHolderAddress": "0x4", "TokenHolderQuantity": "5000000000000000000"},
                {"TokenHolderAddress": "0x5", "TokenHolderQuantity": "2500000000000000000"}
            ]
        })
    )
    result = get_holder_distribution("0x123")
    assert len(result) == 5
    assert result[0]["address"] == "0x1"
    assert result[0]["percent"] > 0

def test_get_holder_distribution_http_error(monkeypatch):
    monkeypatch.setattr(
        "app.core.analyzers.onchain_analyzer.requests.get",
        lambda url: fake_response({}, ok=False)
    )
    result = get_holder_distribution("0x123")
    assert result == []

def test_get_holder_distribution_result_none(monkeypatch):
    monkeypatch.setattr(
        "app.core.analyzers.onchain_analyzer.requests.get",
        lambda url: fake_response({"result": None})
    )
    result = get_holder_distribution("0x123")
    assert result == []


# --- is_lp_locked MOCKS ---
def test_lp_locked_true(monkeypatch):
    monkeypatch.setattr(
        "app.core.analyzers.onchain_analyzer.requests.get",
        lambda url: fake_response({
            "status": "1",
            "message": "OK",
            "result": [
                {"TokenHolderAddress": "0x1fE80fC86816B778B529D3C2a3830e44A6519A25", "TokenHolderQuantity": "80000000000000000000"},
                {"TokenHolderAddress": "0x2", "TokenHolderQuantity": "20000000000000000000"}
            ]
        })
    )
    assert is_lp_locked("0xLP") is True

def test_lp_locked_false(monkeypatch):
    monkeypatch.setattr(
        "app.core.analyzers.onchain_analyzer.requests.get",
        lambda url: fake_response({
            "status": "1",
            "message": "OK",
            "result": [
                {"TokenHolderAddress": "0xBADDEADBEEF", "TokenHolderQuantity": "100000000000000000000"}
            ]
        })
    )
    assert is_lp_locked("0xLP") is False

def test_lp_locked_http_error(monkeypatch):
    monkeypatch.setattr(
        "app.core.analyzers.onchain_analyzer.requests.get",
        lambda url: fake_response({}, ok=False)
    )
    assert is_lp_locked("0xLP") is False

def test_lp_locked_invalid_result(monkeypatch):
    monkeypatch.setattr(
        "app.core.analyzers.onchain_analyzer.requests.get",
        lambda url: fake_response({"result": "erro inesperado"})
    )
    assert is_lp_locked("0xLP") is False


# --- Test analyze_onchain function ---
def test_analyze_onchain_success(monkeypatch):
    monkeypatch.setattr("app.core.analyzers.onchain_analyzer.get_deployer_address", lambda token: "0xDEADBEEF")
    monkeypatch.setattr("app.core.analyzers.onchain_analyzer.is_lp_locked", lambda address: True)

    metadata = {
        "deployer_address": "0xDEADBEEF",
        "deployer_token_count": 1,
        "lp_info": {
            "address": "0x1fE80fC86816B778B529D3C2a3830e44A6519A25",
            "percent_locked": 90.0
        },
        "holders": [
            {"address": "0x1", "percent": 90.0}
        ]
    }

    result = analyze_onchain(metadata)

    assert "onchain" in result
    assert "lp_info" in result
    assert "top_holder_concentration" in result
    
    assert result["top_holder_concentration"] == 90.0
    assert result["lp_info"]["locked"] is True
    assert result["lp_info"]["percent_locked"] == 90.0
    assert "⚠️ Top 5 holders hold more than 50% of supply" in result["onchain"]

def test_analyze_onchain_deployer_flagged(monkeypatch):
    monkeypatch.setattr("app.core.analyzers.onchain_analyzer.get_deployer_address", lambda token: "0xSPAM")
    monkeypatch.setattr("app.core.analyzers.onchain_analyzer.is_lp_locked", lambda address: False)

    metadata = {
        "deployer_address": "0xSPAM",
        "deployer_token_count": 10,
        "lp_info": {"address": "0x123", "percent_locked": 0},
        "holders": []
    }

    result = analyze_onchain(metadata)

    assert "onchain" in result
    assert "lp_info" in result
    assert "top_holder_concentration" in result
    
    assert result["top_holder_concentration"] is None
    assert result["lp_info"]["locked"] is False
    assert "🚨 Deployer created many tokens" in result["onchain"]

def test_analyze_onchain_lp_not_locked(monkeypatch):
    monkeypatch.setattr("app.core.analyzers.onchain_analyzer.get_deployer_address", lambda token: "0xDEAD")
    monkeypatch.setattr("app.core.analyzers.onchain_analyzer.is_lp_locked", lambda address: False)

    metadata = {
        "deployer_address": "0xDEAD",
        "deployer_token_count": 1,
        "lp_info": {
            "address": "0x123",
            "percent_locked": 50.0
        },
        "holders": []
    }

    result = analyze_onchain(metadata)

    assert "onchain" in result
    assert "lp_info" in result
    assert "top_holder_concentration" in result
    
    lp_info = result["lp_info"]
    assert "locked" in lp_info
    assert "percent_locked" in lp_info
    
    assert lp_info["locked"] is False
    assert lp_info["percent_locked"] == 50.0
    assert "❌ LP is not properly locked (>70%)" in result["onchain"]

def test_analyze_onchain_missing_lp_info(monkeypatch):
    monkeypatch.setattr("app.core.analyzers.onchain_analyzer.get_deployer_address", lambda token: "0xDEAD")
    monkeypatch.setattr("app.core.analyzers.onchain_analyzer.is_lp_locked", lambda address: False)

    metadata = {
        "deployer_address": "0xDEAD",
        "deployer_token_count": 1,
        "holders": []
    }

    result = analyze_onchain(metadata)

    assert "onchain" in result
    assert "lp_info" in result
    assert "top_holder_concentration" in result
    
    lp_info = result["lp_info"]
    assert "locked" in lp_info
    assert "percent_locked" in lp_info
    
    assert lp_info["locked"] is False
    assert "❌ LP is not properly locked (>70%)" in result["onchain"]

def test_analyze_onchain_is_lp_locked_exception(monkeypatch):
    monkeypatch.setattr("app.core.analyzers.onchain_analyzer.get_deployer_address", lambda token: "0xDEAD")
    monkeypatch.setattr("app.core.analyzers.onchain_analyzer.is_lp_locked", lambda address: (_ for _ in ()).throw(Exception("Erro simulado")))

    metadata = {
        "deployer_address": "0xDEAD",
        "deployer_token_count": 1,
        "lp_info": {
            "address": "0x123",
            "percent_locked": 10.0
        },
        "holders": []
    }

    result = analyze_onchain(metadata)

    assert "onchain" in result
    assert "lp_info" in result
    assert "top_holder_concentration" in result
    
    lp_info = result["lp_info"]
    assert "locked" in lp_info
    assert "percent_locked" in lp_info
    
    assert lp_info["locked"] is False
    assert "❌ LP is not properly locked (>70%)" in result["onchain"]

def test_analyze_onchain_no_holders(monkeypatch):
    monkeypatch.setattr("app.core.analyzers.onchain_analyzer.get_deployer_address", lambda token: "0xNOHOLDER")
    monkeypatch.setattr("app.core.analyzers.onchain_analyzer.is_lp_locked", lambda address: True)

    metadata = {
        "deployer_address": "0xNOHOLDER",
        "deployer_token_count": 1,
        "lp_info": {
            "address": "0x1fE80fC86816B778B529D3C2a3830e44A6519A25",
            "percent_locked": 90.0
        },
        "holders": []
    }

    result = analyze_onchain(metadata)

    assert "onchain" in result
    assert "lp_info" in result
    assert "top_holder_concentration" in result
    
    lp_info = result["lp_info"]
    assert "locked" in lp_info
    assert "percent_locked" in lp_info
    
    assert result["top_holder_concentration"] is None
    assert lp_info["locked"] is True
    assert "⚠️ Top 5 holders hold more than 50% of supply" not in result["onchain"]

def test_analyze_onchain_low_holder_concentration(monkeypatch):
    monkeypatch.setattr("app.core.analyzers.onchain_analyzer.get_deployer_address", lambda token: "0xDEADBEEF")
    monkeypatch.setattr("app.core.analyzers.onchain_analyzer.is_lp_locked", lambda address: True)

    metadata = {
        "deployer_address": "0xDEADBEEF",
        "deployer_token_count": 2,
        "lp_info": {
            "address": "0x1fE80fC86816B778B529D3C2a3830e44A6519A25",
            "percent_locked": 90.0
        },
        "holders": [
            {"address": "0x1", "percent": 20.0},
            {"address": "0x2", "percent": 10.0},
            {"address": "0x3", "percent": 10.0},
            {"address": "0x4", "percent": 5.0},
            {"address": "0x5", "percent": 4.0},
        ]
    }

    result = analyze_onchain(metadata)

    assert "onchain" in result
    assert "lp_info" in result
    assert "top_holder_concentration" in result
    
    lp_info = result["lp_info"]
    assert "locked" in lp_info
    assert "percent_locked" in lp_info
    
    assert result["top_holder_concentration"] == 49.0
    assert "⚠️ Top 5 holders hold more than 50% of supply" not in result["onchain"]
