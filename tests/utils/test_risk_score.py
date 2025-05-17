import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.utils.risk_score import calculate_risk_score


def test_high_risk_token():
    static = {
        "functions": [{"name": "mint"}, {"name": "blacklist"}],
        "owner": {"renounced": False}
    }
    dynamic = {
        "fees": {"buy": 15, "sell": 15, "buy_mutable": True, "sell_mutable": True},
        "honeypot": {"buy_success": True, "sell_success": False, "error_message": "exec reverted"}
    }
    onchain = {
        "lp_info": {"locked": False},
        "deployer": {"token_history": ["0x1", "0x2", "0x3"]}
    }

    result = calculate_risk_score(static, dynamic, onchain)
    assert result["risk_score"] <= 40
    assert result["grade"] == "🟥 Altíssimo Risco"


def test_safe_token():
    static = {"functions": [], "owner": {"renounced": True}}
    dynamic = {
        "fees": {"buy": 0, "sell": 0, "buy_mutable": False, "sell_mutable": False},
        "honeypot": {"buy_success": True, "sell_success": True}
    }
    onchain = {
        "lp_info": {"locked": True},
        "deployer": {"token_history": []}
    }

    result = calculate_risk_score(static, dynamic, onchain)
    assert result["risk_score"] == 100
    assert result["grade"] == "🟩 Baixo Risco"


def test_score_seguro():
    static = {"functions": [], "owner": {"renounced": True}}
    dynamic = {
        "fees": {"buy": 0, "sell": 0, "buy_mutable": False, "sell_mutable": False},
        "honeypot": {"buy_success": True, "sell_success": True}
    }
    onchain = {
        "lp_info": {"locked": True},
        "deployer": {"token_history": []}
    }

    result = calculate_risk_score(static, dynamic, onchain)
    assert result["risk_score"] == 100
    assert result["grade"] == "🟩 Baixo Risco"


def test_score_moderado():
    static = {
        "functions": [{"name": "setFee"}] * 7,
        "owner": {"renounced": False}
    }
    result = calculate_risk_score(
        static,
        {"fees": {}, "honeypot": {}},
        {"lp_info": {"locked": True}, "deployer": {"token_history": []}}
    )
    assert 61 <= result["risk_score"] < 81
    assert result["grade"] == "🟨 Risco Moderado"


def test_score_arriscado():
    static = {
        "functions": [{"name": "mint"}] * 4,
        "owner": {"renounced": False}
    }
    result = calculate_risk_score(
        static,
        {"fees": {}, "honeypot": {}},
        {"lp_info": {"locked": False}, "deployer": {"token_history": []}}
    )
    assert 31 <= result["risk_score"] <= 60
    assert result["grade"] == "🟧 Risco Alto"


def test_score_perigoso():
    static = {
        "functions": [{"name": "blacklist"}],
        "owner": {"renounced": False}
    }
    dynamic = {
        "fees": {"buy_mutable": True, "sell_mutable": True},
        "honeypot": {"buy_success": True, "sell_success": False, "error_message": "revertido"}
    }
    onchain = {
        "lp_info": {"locked": False},
        "deployer": {"token_history": ["0x1", "0x2", "0x3"]}
    }

    result = calculate_risk_score(static, dynamic, onchain)
    assert result["risk_score"] <= 30
    assert result["grade"] == "🟥 Altíssimo Risco"


def test_score_nunca_negativo():
    static = {
        "functions": [{"name": "mint"}] * 10,
        "owner": {"renounced": False}
    }
    result = calculate_risk_score(
        static,
        {"fees": {}, "honeypot": {}},
        {"lp_info": {}, "deployer": {}}
    )
    assert result["risk_score"] >= 0


def test_status_moderado():
    static = {
        "functions": [{"name": "anything"}] * 7,
        "owner": {"renounced": False}
    }
    result = calculate_risk_score(
        static,
        {"fees": {}, "honeypot": {}},
        {"lp_info": {"locked": True}, "deployer": {"token_history": []}}
    )
    assert result["grade"] == "🟨 Risco Moderado"


def test_status_arriscado():
    static = {
        "functions": [{"name": "setFee"}] * 8,
        "owner": {"renounced": False}
    }
    result = calculate_risk_score(
        static,
        {"fees": {}, "honeypot": {}},
        {"lp_info": {"locked": False}, "deployer": {"token_history": []}}
    )
    assert result["grade"] == "🟧 Risco Alto"


def test_alert_lp_unlock_affects_score():
    static = {"functions": [], "owner": {"renounced": True}}
    result = calculate_risk_score(
        static,
        {"fees": {}, "honeypot": {}},
        {"lp_info": {"locked": False}, "deployer": {}}
    )
    assert result["risk_score"] < 100
