from utils.analyze_token import analyze_token

def test_analyze_token_all_mocks(monkeypatch):
    monkeypatch.setattr("utils.analyze_token.fetch_token_metadata", lambda addr: {"SourceCode": "mint setFee"})
    monkeypatch.setattr("utils.analyze_token.simulate_buy_sell", lambda addr: ["❌ honeypot"])
    monkeypatch.setattr("utils.analyze_token.get_deployer_address", lambda addr: "0xDEAD...BEEF")
    monkeypatch.setattr("utils.analyze_token.get_holder_distribution", lambda addr: {"top5_percentage": 90, "holders": []})
    monkeypatch.setattr("utils.analyze_token.is_lp_locked", lambda addr: False)


    result = analyze_token("0x000000000000000000000000000000000000dEaD", lp_token_address="0x000000000000000000000000000000000000LPLP")

    assert result["score"] < 50
    assert "honeypot" in "".join(result["alerts"]).lower()
    assert result["status"] in ["🔶 Arriscado", "🔴 Perigoso"]

def test_analyze_token_with_all_failures(monkeypatch):
    # forçar erro no fetch_metadata
    monkeypatch.setattr("utils.analyze_token.fetch_token_metadata", lambda addr: (_ for _ in ()).throw(Exception("fail static")))
    monkeypatch.setattr("utils.analyze_token.simulate_buy_sell", lambda addr: (_ for _ in ()).throw(Exception("fail dynamic")))
    monkeypatch.setattr("utils.analyze_token.get_deployer_address", lambda addr: (_ for _ in ()).throw(Exception("fail deployer")))
    monkeypatch.setattr("utils.analyze_token.get_holder_distribution", lambda addr: (_ for _ in ()).throw(Exception("fail holders")))
    monkeypatch.setattr("utils.analyze_token.is_lp_locked", lambda addr: (_ for _ in ()).throw(Exception("fail lp")))

    result = analyze_token("0x000000000000000000000000000000000000fail", lp_token_address="0xlp")

    assert any("falha" in alert.lower() for alert in result["alerts"])
    assert result["score"] < 100
