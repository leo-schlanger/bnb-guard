import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

import pytest
from app.utils.fetch_metadata import fetch_token_metadata

# Token real e conhecido da BNB (ou substitua por outro verificado no BscScan)
VALID_TOKEN = "0xB8c77482e45F1F44de1745F52C74426C631bdd52"

# Token inválido (não existe)
INVALID_TOKEN = "0x1"


def test_fetch_metadata_success():
    result = fetch_token_metadata(VALID_TOKEN)

    assert isinstance(result, dict)
    assert "ContractName" in result
    assert isinstance(result["ContractName"], str)
    assert "SourceCode" in result


def test_fetch_metadata_source_code_field():
    result = fetch_token_metadata(VALID_TOKEN)

    # SourceCode pode ser string vazia, mas a chave deve existir
    assert "SourceCode" in result
    assert isinstance(result["SourceCode"], str)


def test_fetch_metadata_invalid_token_raises():
    with pytest.raises(Exception, match="Nenhum dado retornado"):
        fetch_token_metadata(INVALID_TOKEN)

def test_fetch_metadata_http_error(monkeypatch):
    def fake_get(*args, **kwargs):
        class FakeResponse:
            ok = False
            def json(self):
                return {}
        return FakeResponse()

    monkeypatch.setattr("requests.get", fake_get)

    with pytest.raises(Exception, match="Erro na chamada BscScan"):
        fetch_token_metadata("0xwhatever")