import sys, os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.services.auditor import audit_token

def test_audit_token_full(monkeypatch):
    monkeypatch.setattr("app.services.auditor.fetch_token_metadata", lambda addr: {
        "name": "ScamToken",
        "symbol": "SCM",
        "totalSupply": 1000000,
        "owner": "0xBAD",
        "functions": ["mint"],
        "buy_tax": 25.0,
        "sell_tax": 25.0,
        "buy_mutable": True,
        "sell_mutable": True,
        "has_blacklist": True,
        "has_mint": True,
        "lp_info": {"locked": False},
        "deployer_address": "0xBAD",
        "deployer_token_count": 6,
        "holders": [{"address": "0x1", "percent": 30.0}]
    })

    monkeypatch.setattr("app.services.auditor.analyze_static", lambda src: {
        "owner": {"renounced": False, "functions": ["mint"]},
        "functions": ["mint"]
    })

    monkeypatch.setattr("app.services.auditor.analyze_dynamic", lambda addr: {
        "honeypot": {
            "buy_success": False,
            "sell_success": False,
            "slippage": 90.0,
            "error_message": "Venda bloqueada"
        },
        "fees": {
            "buy": 25.0,
            "sell": 25.0,
            "buy_mutable": True,
            "sell_mutable": True
        }
    })

    monkeypatch.setattr("app.services.auditor.analyze_onchain", lambda metadata: {
        "deployer": {"address": "0xBAD", "token_history": []},
        "top_holders": {
            "top_1_percent": 30.0,
            "top_10_percent": 50.0,
            "top_50_percent": 80.0,
            "holders": [{"address": "0x1", "percentage": "30.00%"}]
        },
        "lp_info": {"locked": False},
        "lp_locked": False,
        "lp_percent_locked": 20.0,
        "deployer_flagged": True,
        "deployer_token_count": 6,
        "warnings": ["🚨 Deployer criou muitos tokens"]
    })

    monkeypatch.setattr("app.services.auditor.calculate_risk_score", lambda *_: {
        "risk_score": 20,
        "alerts": ["⚠️ LP não está travada"],
        "risks": [],
        "grade": "D"
    })

    result = audit_token("0xdead")
    assert result["name"] == "ScamToken"

def test_audit_token_with_exception(monkeypatch):
    # Força erro no fetch_token_metadata
    monkeypatch.setattr("app.services.auditor.fetch_token_metadata", lambda address: (_ for _ in ()).throw(Exception("Erro forçado")))

    result = audit_token("0xERRO")

    assert result["name"] == "Erro"
    assert result["score"]["value"] == 0
    assert result["honeypot"]["error_message"]
    assert "❌" in result["score"]["details"][0]

def test_audit_token_raises(monkeypatch):
    def fake_fetch(*args, **kwargs):
        raise Exception("Erro audit")
    
    monkeypatch.setattr("app.services.auditor.fetch_token_metadata", fake_fetch)

    result = audit_token("0x456")
    assert result["name"] == "Erro"
    assert result["score"]["value"] == 0
    assert "Erro ao processar token" in result["score"]["details"][0]


def test_audit_token_exception(monkeypatch):
    def raise_error(address):
        raise Exception("Erro forçado no fetch")

    monkeypatch.setattr("app.services.auditor.fetch_token_metadata", raise_error)

    result = audit_token("0xBEEF")
    assert result["name"] == "Erro"
    assert result["symbol"] == "ERR"
    assert result["score"]["value"] == 0
    assert "❌ Erro ao processar token" in result["score"]["details"][0]

def test_audit_token_with_lp(monkeypatch):
    monkeypatch.setattr("app.services.auditor.fetch_token_metadata", lambda address: {
        "name": "AuditLP",
        "symbol": "AUD",
        "totalSupply": 1234567,
        "SourceCode": "",
        "deployer_address": "0xDEAD",
        "deployer_token_count": 2,
        "holders": [],
        "lp_info": {}
    })

    monkeypatch.setattr("app.services.auditor.analyze_static", lambda src: {})
    monkeypatch.setattr("app.services.auditor.analyze_dynamic", lambda addr: {})
    monkeypatch.setattr("app.services.auditor.analyze_onchain", lambda metadata: {
        "top_holders": {
            "top_1_percent": 10,
            "top_10_percent": 30,
            "top_50_percent": 50,
            "holders": []
        },
        "deployer": {"address": "0xDEAD", "token_history": []}
    })
    monkeypatch.setattr("app.services.auditor.calculate_risk_score", lambda *_: {
        "risk_score": 90,
        "alerts": [],
        "risks": []
    })

    result = audit_token("0x456", lp_token_address="0xLP")
    assert result["lp_lock"]["locked_percentage"] == 100.0

