import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from app.utils.analyze_onchain import (
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
        "app.utils.analyze_onchain.requests.get",
        lambda url: fake_response({"result": [{"contractCreator": "0xDEADBEEF"}]})
    )
    result = get_deployer_address("0x123")
    assert result == "0xDEADBEEF"

def test_get_deployer_address_mock_not_found(monkeypatch):
    monkeypatch.setattr(
        "app.utils.analyze_onchain.requests.get",
        lambda url: fake_response({"result": [{}]})
    )
    with pytest.raises(Exception, match=".*"):
        get_deployer_address("0x123")

def test_get_deployer_address_http_error(monkeypatch):
    monkeypatch.setattr(
        "app.utils.analyze_onchain.requests.get",
        lambda url: fake_response({}, ok=False, status_code=500)
    )
    with pytest.raises(Exception, match=".*"):
        get_deployer_address("0x123")


# --- get_holder_distribution MOCKS ---
def test_get_holder_distribution_success(monkeypatch):
    monkeypatch.setattr(
        "app.utils.analyze_onchain.requests.get",
        lambda url: fake_response({
            "result": [
                {"address": "0x1", "percentage": "40.00%"},
                {"address": "0x2", "percentage": "30.00%"},
                {"address": "0x3", "percentage": "10.00%"},
                {"address": "0x4", "percentage": "5.00%"},
                {"address": "0x5", "percentage": "2.50%"}
            ]
        })
    )
    result = get_holder_distribution("0x123")
    assert result["top5_percentage"] == 87.5
    assert len(result["holders"]) == 5
    assert result["holders"][0]["address"] == "0x1"

def test_get_holder_distribution_http_error(monkeypatch):
    monkeypatch.setattr(
        "app.utils.analyze_onchain.requests.get",
        lambda url: fake_response({}, ok=False)
    )
    with pytest.raises(Exception, match=".*"):
        get_holder_distribution("0x123")

def test_get_holder_distribution_result_none(monkeypatch):
    monkeypatch.setattr(
        "app.utils.analyze_onchain.requests.get",
        lambda url: fake_response({"result": None})
    )
    with pytest.raises(Exception, match=".*"):
        get_holder_distribution("0x123")


# --- is_lp_locked MOCKS ---
def test_lp_locked_true(monkeypatch):
    monkeypatch.setattr(
        "app.utils.analyze_onchain.requests.get",
        lambda url: fake_response({
            "result": [{"address": "0x1fE80fC86816B778B529D3C2a3830e44A6519A25"}]
        })
    )
    assert is_lp_locked("0xLP") is True

def test_lp_locked_false(monkeypatch):
    monkeypatch.setattr(
        "app.utils.analyze_onchain.requests.get",
        lambda url: fake_response({
            "result": [{"address": "0xBADDEADBEEF"}]
        })
    )
    assert is_lp_locked("0xLP") is False

def test_lp_locked_http_error(monkeypatch):
    monkeypatch.setattr(
        "app.utils.analyze_onchain.requests.get",
        lambda url: fake_response({}, ok=False)
    )
    with pytest.raises(Exception, match=".*"):
        is_lp_locked("0xLP")

def test_lp_locked_invalid_result(monkeypatch):
    monkeypatch.setattr(
        "app.utils.analyze_onchain.requests.get",
        lambda url: fake_response({"result": "erro inesperado"})
    )
    with pytest.raises(Exception, match=".*"):
        is_lp_locked("0xLP")


# --- Test analyze_onchain function ---
def test_analyze_onchain_success(monkeypatch):
    monkeypatch.setattr("app.utils.analyze_onchain.get_deployer_address", lambda token: "0xDEADBEEF")
    monkeypatch.setattr("app.utils.analyze_onchain.is_lp_locked", lambda address: True)

    metadata = {
        "deployer_address": "0xDEADBEEF",
        "deployer_token_count": 1,
        "lp_info": {
            "address": "0x1fE80fC86816B778B529D3C2a3830e44A6519A25"
        },
        "holders": [
            {"address": "0x1", "percent": 90.0}
        ]
    }

    result = analyze_onchain(metadata)

    assert result["deployer_address"] == "0xDEADBEEF"
    assert result["deployer_token_count"] == 1
    assert result["lp_locked"] is True
    assert result["top_holder_concentration"] == 90.0
    assert isinstance(result["lp_info"], dict)
    assert result["lp_info"]["address"] == "0x1fE80fC86816B778B529D3C2a3830e44A6519A25"
    assert result["alerts"] == ["⚠️ Top 5 holders hold more than 50% of supply"]

def test_analyze_onchain_deployer_flagged(monkeypatch):
    monkeypatch.setattr("app.utils.analyze_onchain.get_deployer_address", lambda token: "0xSPAM")
    monkeypatch.setattr("app.utils.analyze_onchain.is_lp_locked", lambda address: False)

    metadata = {
        "deployer_address": "0xSPAM",
        "deployer_token_count": 10,
        "lp_info": {"address": "0x123"},
        "holders": []
    }

    result = analyze_onchain(metadata)

    assert result["deployer_flagged"] is True
    assert "🚨 Deployer created many tokens" in result["alerts"]

def test_analyze_onchain_lp_not_locked(monkeypatch):
    monkeypatch.setattr("app.utils.analyze_onchain.get_deployer_address", lambda token: "0xDEAD")
    monkeypatch.setattr("app.utils.analyze_onchain.is_lp_locked", lambda address: False)

    metadata = {
        "deployer_address": "0xDEAD",
        "deployer_token_count": 1,
        "lp_info": {
            "address": "0x123",
            "locked": False,
            "percent_locked": 50.0
        },
        "holders": []
    }

    result = analyze_onchain(metadata)

    assert result["lp_locked"] is False
    assert result["lp_percent_locked"] == 50.0
    assert "❌ LP is not properly locked (>70%)" in result["alerts"]

def test_analyze_onchain_missing_lp_info(monkeypatch):
    monkeypatch.setattr("app.utils.analyze_onchain.get_deployer_address", lambda token: "0xDEAD")
    monkeypatch.setattr("app.utils.analyze_onchain.is_lp_locked", lambda address: False)

    metadata = {
        "deployer_address": "0xDEAD",
        "deployer_token_count": 1,
        "holders": []
    }

    result = analyze_onchain(metadata)

    assert result["lp_locked"] is False
    assert "❌ LP is not properly locked (>70%)" in result["alerts"]

def test_analyze_onchain_lp_not_locked(monkeypatch):
    monkeypatch.setattr("app.utils.analyze_onchain.get_deployer_address", lambda token: "0xDEAD")
    monkeypatch.setattr("app.utils.analyze_onchain.is_lp_locked", lambda address: False)

    metadata = {
        "deployer_address": "0xDEAD",
        "deployer_token_count": 1,
        "lp_info": {
            "address": "0x123",
            "locked": False,
            "percent_locked": 100.0
        },
        "holders": []
    }

    result = analyze_onchain(metadata)

    assert result["lp_locked"] is False
    assert result["lp_percent_locked"] == 100.0
    assert "❌ LP is not properly locked (>70%)" in result["alerts"]

def test_analyze_onchain_is_lp_locked_exception(monkeypatch):
    monkeypatch.setattr("app.utils.analyze_onchain.get_deployer_address", lambda token: "0xDEAD")
    monkeypatch.setattr("app.utils.analyze_onchain.is_lp_locked", lambda address: (_ for _ in ()).throw(Exception("Erro simulado")))

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

    assert result["lp_locked"] is False
    assert "❌ LP is not properly locked (>70%)" in result["alerts"]

def test_analyze_onchain_no_holders(monkeypatch):
    monkeypatch.setattr("app.utils.analyze_onchain.get_deployer_address", lambda token: "0xNOHOLDER")
    monkeypatch.setattr("app.utils.analyze_onchain.is_lp_locked", lambda address: True)

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

    assert result["top_holder_concentration"] is None
    assert result["lp_locked"] is True
    assert "⚠️ Top 5 holders hold more than 50% of supply" not in result["alerts"]

def test_analyze_onchain_low_holder_concentration(monkeypatch):
    monkeypatch.setattr("app.utils.analyze_onchain.get_deployer_address", lambda token: "0xDEADBEEF")
    monkeypatch.setattr("app.utils.analyze_onchain.is_lp_locked", lambda address: True)

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

    assert result["top_holder_concentration"] == 49.0
    assert "⚠️ Top 5 holders hold more than 50% of supply" not in result["alerts"]
