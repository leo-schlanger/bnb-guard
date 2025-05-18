import pytest
from app.utils.fetch_metadata import fetch_token_metadata
from unittest.mock import MagicMock
import json

import pytest
import json
from app.utils.fetch_metadata import fetch_token_metadata

def fake_response(json_data, ok=True):
    class Fake:
        def __init__(self):
            self._json = json_data
            self.ok = ok
        def json(self):
            return self._json
    return Fake()

def test_fetch_metadata_success(monkeypatch):
    abi = [{"name": "name", "type": "function"},
           {"name": "symbol", "type": "function"},
           {"name": "totalSupply", "type": "function"}]

    monkeypatch.setattr("app.utils.fetch_metadata.requests.get", lambda url: fake_response({
        "result": [{
            "ABI": json.dumps(abi),
            "ContractName": "Token",
            "TokenName": "TestToken",
            "Symbol": "TT",
            "Owner": "0x123"
        }]
    }))

    class MockFunctionCall:
        def __init__(self, value):
            self.value = value
        def call(self):
            return self.value

    class MockFunctions:
        def name(self): return MockFunctionCall("TestToken")
        def symbol(self): return MockFunctionCall("TT")
        def totalSupply(self): return MockFunctionCall(1000000000000000000000000)

    class MockContract:
        functions = MockFunctions()

    class MockEth:
        def contract(self, address, abi):
            if isinstance(abi, str):
                json.loads(abi)  # força parse para simular erro se inválido
            return MockContract()

    class MockWeb3:
        @staticmethod
        def HTTPProvider(url): return url
        def __init__(self, provider): self.eth = MockEth()
        def to_checksum_address(self, addr): return addr

    monkeypatch.setattr("app.utils.fetch_metadata.Web3", MockWeb3)

    result = fetch_token_metadata("0x123")
    assert result["name"] == "TestToken"
    assert result["symbol"] == "TT"
    assert result["totalSupply"] == "1000000000000000000000000"


def test_fetch_metadata_http_error(monkeypatch):
    monkeypatch.setattr("app.utils.fetch_metadata.requests.get", lambda url: fake_response({}, ok=False))
    with pytest.raises(Exception, match="BscScan call"):
        fetch_token_metadata("0x123")

def test_fetch_metadata_result_none(monkeypatch):
    monkeypatch.setattr("app.utils.fetch_metadata.requests.get", lambda url: fake_response({"result": None}))
    with pytest.raises(Exception, match="No data returned"):
        fetch_token_metadata("0x123")

def test_fetch_metadata_result_empty(monkeypatch):
    monkeypatch.setattr("app.utils.fetch_metadata.requests.get", lambda url: fake_response({"result": []}))
    with pytest.raises(Exception, match="No data returned"):
        fetch_token_metadata("0x123")

def test_fetch_metadata_unverified_contract(monkeypatch):
    monkeypatch.setattr("app.utils.fetch_metadata.requests.get", lambda url: fake_response({
        "result": [{
            "ABI": "Contract source code not verified"
        }]
    }))
    result = fetch_token_metadata("0x123")
    assert result["name"] == "N/A"
    assert result["symbol"] == "N/A"
    assert result["totalSupply"] == 0

def test_fetch_metadata_web3_error(monkeypatch):
    monkeypatch.setattr("app.utils.fetch_metadata.requests.get", lambda url: fake_response({
        "result": [{
            "ABI": "[{}]"
        }]
    }))

    # Mock que lança exceção na chamada ao contrato
    class MockEth:
        def contract(self, address, abi): raise Exception("web3 fail")

    class MockWeb3:
        HTTPProvider = lambda *args, **kwargs: "http://mock"
        def __init__(self, provider): self.eth = MockEth()
        def to_checksum_address(self, addr): return addr

    monkeypatch.setattr("app.utils.fetch_metadata.Web3", MockWeb3)

    result = fetch_token_metadata("0x123")
    assert result["name"] == "N/A"
    assert result["symbol"] == "N/A"
    assert result["totalSupply"] == 0

