import pytest
from utils.analyze_onchain import get_deployer_address, get_holder_distribution, is_lp_locked

# --- TESTE REAL ---
def test_get_deployer_address_real():
    token = "0xe9e7cea3dedca5984780bafc599bd69add087d56"  # BUSD antigo
    result = get_deployer_address(token)
    assert result.startswith("0x") and len(result) == 42

# --- MOCK: deployer encontrado ---
def test_get_deployer_address_mock_success(monkeypatch):
    class FakeResponse:
        ok = True
        def json(self):
            return {
                "result": [{
                    "contractCreator": "0xDEADBEEF00000000000000000000000000000000"
                }]
            }

    monkeypatch.setattr("requests.get", lambda url: FakeResponse())
    result = get_deployer_address("0x123")
    assert result == "0xDEADBEEF00000000000000000000000000000000"

# --- MOCK: deployer ausente ---
def test_get_deployer_address_mock_not_found(monkeypatch):
    class FakeResponse:
        ok = True
        def json(self):
            return {"result": [{}]}  # sem contractCreator

    monkeypatch.setattr("requests.get", lambda url: FakeResponse())

    with pytest.raises(Exception, match="Deployer não encontrado"):
        get_deployer_address("0x123")

# --- MOCK: erro HTTP ---
def test_get_deployer_address_http_error(monkeypatch):
    class FakeResponse:
        ok = False
        status_code = 500
        def json(self): return {}

    monkeypatch.setattr("requests.get", lambda url: FakeResponse())

    with pytest.raises(Exception, match="Erro ao buscar criador"):
        get_deployer_address("0x123")

def test_get_holder_distribution_mock(monkeypatch):
    class FakeResponse:
        ok = True
        def json(self):
            return {
                "result": [
                    {"address": "0x1", "percentage": "40.00%"},
                    {"address": "0x2", "percentage": "30.00%"},
                    {"address": "0x3", "percentage": "10.00%"},
                    {"address": "0x4", "percentage": "5.00%"},
                    {"address": "0x5", "percentage": "2.50%"}
                ]
            }

    monkeypatch.setattr("requests.get", lambda url: FakeResponse())
    result = get_holder_distribution("0x123")
    assert result["top5_percentage"] == 87.5
    assert len(result["holders"]) == 5

def test_get_holder_distribution_http_error(monkeypatch):
    class FakeResponse:
        ok = False
        status_code = 500
        def json(self): return {}

    monkeypatch.setattr("requests.get", lambda url: FakeResponse())

    with pytest.raises(Exception, match="Erro ao buscar distribuição"):
        get_holder_distribution("0x123")

def test_get_holder_distribution_result_none(monkeypatch):
    class FakeResponse:
        ok = True
        def json(self): return {"result": None}

    monkeypatch.setattr("requests.get", lambda url: FakeResponse())

    with pytest.raises(Exception, match="Não foi possível obter os holders"):
        get_holder_distribution("0x123")

def test_lp_locked_true(monkeypatch):
    class FakeResponse:
        ok = True
        def json(self):
            return {
                "result": [
                    {"address": "0x1fE80fC86816B778B529D3C2a3830e44A6519A25"}  # PinkLock
                ]
            }

    monkeypatch.setattr("requests.get", lambda url: FakeResponse())
    result = is_lp_locked("0x000000000000000000000000000000000000LP")
    assert result is True


def test_lp_locked_false(monkeypatch):
    class FakeResponse:
        ok = True
        def json(self):
            return {
                "result": [
                    {"address": "0xBADDEADBEEF0000000000000000000000000000"}
                ]
            }

    monkeypatch.setattr("requests.get", lambda url: FakeResponse())
    result = is_lp_locked("0x000000000000000000000000000000000000LP")
    assert result is False


def test_lp_locked_http_error(monkeypatch):
    class FakeResponse:
        ok = False
        status_code = 500
        def json(self): return {}

    monkeypatch.setattr("requests.get", lambda url: FakeResponse())

    with pytest.raises(Exception, match="Erro ao buscar holders da LP"):
        is_lp_locked("0x000000000000000000000000000000000000LP")

def test_lp_locked_invalid_result(monkeypatch):
    class FakeResponse:
        ok = True
        def json(self):
            return {"result": "erro inesperado"}  # Não é lista!

    monkeypatch.setattr("requests.get", lambda url: FakeResponse())

    with pytest.raises(Exception, match="Resultado inválido ao buscar LP"):
        is_lp_locked("0x000000000000000000000000000000000000LP")

