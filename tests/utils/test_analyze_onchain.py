import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from app.utils.analyze_onchain import (
    get_deployer_address,
    get_holder_distribution,
    is_lp_locked,
    analyze_onchain
)

# 🔧 Utilitário de mock genérico corrigido
def fake_response(json_data, ok=True, status_code=200):
    class _Fake:
        def __init__(self):
            self._json = json_data
            self.ok = ok
            self.status_code = status_code

        def json(self):
            return self._json

    return _Fake()


# --- TESTE REAL (opcional) ---
@pytest.mark.skip(reason="Teste real pode falhar por instabilidade externa")
def test_get_deployer_address_real():
    token = "0xe9e7cea3dedca5984780bafc599bd69add087d56"
    result = get_deployer_address(token)
    assert result.startswith("0x") and len(result) == 42


# --- MOCKS DE get_deployer_address ---
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


# --- MOCKS DE get_holder_distribution ---
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


# --- MOCKS DE is_lp_locked ---
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


# --- NOVO: Teste da função analyze_onchain ---
def test_analyze_onchain_success(monkeypatch):
    monkeypatch.setattr("app.utils.analyze_onchain.get_deployer_address", lambda token: "0xDEADBEEF")
    monkeypatch.setattr("app.utils.analyze_onchain.get_holder_distribution", lambda token: {
        "top5_percentage": 90.0,
        "holders": [{"address": "0x1", "percentage": "90.00%"}]
    })
    monkeypatch.setattr("app.utils.analyze_onchain.is_lp_locked", lambda lp: True)

    result = analyze_onchain("0xTOKEN")

    assert result["deployer"]["address"] == "0xDEADBEEF"
    assert isinstance(result["deployer"]["token_history"], list)
    assert result["lp_info"]["locked"] is True
    assert result["holders"][0]["address"] == "0x1"
