import pytest
from typing import Dict, Any
from app.core.utils.scoring import calculate_risk_score


def test_high_risk_token():
    static = {
        "functions": [
            {"name": "mint", "description": "Mint function", "severity": "high"},
            {"name": "blacklist", "description": "Blacklist function", "severity": "high"}
        ],
        "owner": {"renounced": False}
    }
    dynamic = {
        "fees": {"buy": 15, "sell": 15, "buy_mutable": True, "sell_mutable": True},
        "honeypot": {"buy_success": True, "sell_success": False, "error_message": "exec reverted"},
        "lp_info": {"locked": False},
        "holder_concentration": 60
    }
    onchain = {
        "deployer": {"token_history": ["0x1", "0x2", "0x3"]}
    }

    result = calculate_risk_score(static, dynamic, onchain)
    assert result["risk_score"] <= 40
    assert result["grade"] == "F"  # A implementação atual retorna letras, não emojis


def test_safe_token():
    static = {
        "functions": [], 
        "owner": {"renounced": True}
    }
    dynamic = {
        "fees": {"buy": 0, "sell": 0, "buy_mutable": False, "sell_mutable": False},
        "honeypot": {"buy_success": True, "sell_success": True},
        "lp_info": {"locked": True},
        "holder_concentration": 10
    }
    onchain = {
        "deployer": {"token_history": []}
    }

    result = calculate_risk_score(static, dynamic, onchain)
    assert result["risk_score"] == 100
    assert result["grade"] == "A+"  # A implementação atual retorna letras, não emojis


def test_safe_token_grade():
    static = {
        "functions": [], 
        "owner": {"renounced": True}
    }
    dynamic = {
        "fees": {"buy": 0, "sell": 0, "buy_mutable": False, "sell_mutable": False},
        "honeypot": {"buy_success": True, "sell_success": True},
        "lp_info": {"locked": True},
        "holder_concentration": 10
    }
    onchain = {
        "deployer": {"token_history": []}
    }

    result = calculate_risk_score(static, dynamic, onchain)
    assert result["risk_score"] == 100
    assert result["grade"] == "A+"  # A implementação atual retorna letras, não emojis


def test_moderate_risk_grade():
    static = {
        "functions": [
            {"name": "setFee", "description": "Set fee function", "severity": "medium"}
        ] * 7,
        "owner": {"renounced": False}
    }
    dynamic = {
        "fees": {"buy": 0, "sell": 0, "buy_mutable": False, "sell_mutable": False},
        "honeypot": {"buy_success": True, "sell_success": True},
        "lp_info": {"locked": True},
        "holder_concentration": 20
    }
    onchain = {
        "deployer": {"token_history": []}
    }
    
    result = calculate_risk_score(static, dynamic, onchain)
    assert 61 <= result["risk_score"] < 81
    assert result["grade"] in ["A", "B", "C"]  # A implementação atual retorna letras, não emojis


def test_high_risk_grade():
    static = {
        "functions": [
            {"name": "mint", "description": "Mint function", "severity": "high"}
        ] * 4,
        "owner": {"renounced": False}
    }
    dynamic = {
        "fees": {"buy": 0, "sell": 0, "buy_mutable": False, "sell_mutable": False},
        "honeypot": {"buy_success": True, "sell_success": True},
        "lp_info": {"locked": False},
        "holder_concentration": 30
    }
    onchain = {
        "deployer": {"token_history": []}
    }
    
    result = calculate_risk_score(static, dynamic, onchain)
    assert 31 <= result["risk_score"] <= 60
    assert result["grade"] in ["D", "F"]  # A implementação atual retorna letras, não emojis


def test_extreme_risk_grade():
    static = {
        "functions": [
            {"name": "blacklist", "description": "Blacklist function", "severity": "high"}
        ],
        "owner": {"renounced": False}
    }
    dynamic = {
        "fees": {"buy": 15, "sell": 15, "buy_mutable": True, "sell_mutable": True},
        "honeypot": {"buy_success": True, "sell_success": False, "error_message": "revertido"},
        "lp_info": {"locked": False},
        "holder_concentration": 70
    }
    onchain = {
        "deployer": {"token_history": ["0x1", "0x2", "0x3"]}
    }

    result = calculate_risk_score(static, dynamic, onchain)
    assert result["risk_score"] <= 30
    assert result["grade"] == "F"  # A implementação atual retorna letras, não emojis


def test_score_never_negative():
    static = {
        "functions": [
            {"name": "mint", "description": "Mint function", "severity": "high"}
        ] * 10,
        "owner": {"renounced": False}
    }
    dynamic = {
        "fees": {"buy": 100, "sell": 100, "buy_mutable": True, "sell_mutable": True},
        "honeypot": {"buy_success": False, "sell_success": False},
        "lp_info": {"locked": False},
        "holder_concentration": 100
    }
    onchain = {
        "deployer": {"token_history": ["0x1"] * 10}
    }
    
    result = calculate_risk_score(static, dynamic, onchain)
    assert result["risk_score"] >= 0


def test_moderate_risk_status():
    static = {
        "functions": [
            {"name": "setFee", "description": "Set fee function", "severity": "medium"}
        ] * 7,
        "owner": {"renounced": False}
    }
    dynamic = {
        "fees": {"buy": 0, "sell": 0, "buy_mutable": False, "sell_mutable": False},
        "honeypot": {"buy_success": True, "sell_success": True},
        "lp_info": {"locked": True},
        "holder_concentration": 20
    }
    onchain = {
        "deployer": {"token_history": []}
    }
    
    result = calculate_risk_score(static, dynamic, onchain)
    assert result["grade"] in ["A", "B", "C"]  # A implementação atual retorna letras, não emojis


def test_high_risk_status():
    static = {
        "functions": [
            {"name": "mint", "description": "Mint function", "severity": "high"}
        ] * 4,
        "owner": {"renounced": False}
    }
    dynamic = {
        "fees": {"buy": 0, "sell": 0, "buy_mutable": False, "sell_mutable": False},
        "honeypot": {"buy_success": True, "sell_success": True},
        "lp_info": {"locked": False},
        "holder_concentration": 30
    }
    onchain = {
        "deployer": {"token_history": []}
    }
    
    result = calculate_risk_score(static, dynamic, onchain)
    assert result["grade"] in ["D", "F"]  # A implementação atual retorna letras, não emojis


def test_lp_unlock_affects_score():
    static = {
        "functions": [], 
        "owner": {"renounced": True}
    }
    
    # Testa com LP bloqueado
    dynamic_locked = {
        "fees": {"buy": 0, "sell": 0, "buy_mutable": False, "sell_mutable": False},
        "honeypot": {"buy_success": True, "sell_success": True},
        "lp_info": {"locked": True},
        "holder_concentration": 10
    }
    
    # Testa com LP desbloqueado
    dynamic_unlocked = {
        "fees": {"buy": 0, "sell": 0, "buy_mutable": False, "sell_mutable": False},
        "honeypot": {"buy_success": True, "sell_success": True},
        "lp_info": {"locked": False},
        "holder_concentration": 10
    }
    
    onchain = {
        "deployer": {"token_history": []}
    }
    
    result_locked = calculate_risk_score(static, dynamic_locked, onchain)
    result_unlocked = calculate_risk_score(static, dynamic_unlocked, onchain)
    
    assert result_unlocked["risk_score"] < result_locked["risk_score"]
