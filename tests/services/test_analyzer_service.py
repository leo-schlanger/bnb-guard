import sys, os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.services.analyzer import analyze_token

def test_analyze_token_minimal(monkeypatch):
    monkeypatch.setattr("app.services.analyzer.fetch_token_metadata", lambda address: {
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
    })

    monkeypatch.setattr("app.services.analyzer.analyze_static", lambda src: {
        "owner": {"renounced": True, "functions": []},
        "functions": []
    })

    monkeypatch.setattr("app.services.analyzer.analyze_dynamic", lambda addr: {
        "honeypot": {"sell_success": True},
        "fees": {"buy": 1.0, "sell": 1.0}
    })

    monkeypatch.setattr("app.services.analyzer.analyze_onchain", lambda metadata: {
        "top_holders": {"holders": []}
    })

    monkeypatch.setattr("app.services.analyzer.calculate_risk_score", lambda *_: {
        "risk_score": 85,
        "grade": "A",
        "alerts": [],
        "risks": []
    })

    result = analyze_token("0x123")
    assert result["name"] == "MockToken"

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
