from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_audit_route_success():
    mock_result = {
        "token_address": "0x123",
        "name": "MockToken",
        "symbol": "MTK",
        "supply": 1000000,
        "functions": [],
        "owner": {"renounced": True, "functions": []},
        "lp_locked": True,
        "lp_lock": {
            "locked": True,
            "locked_percentage": 80.0,
            "unlock_date": "2025-12-31"
        },
        "lp_info": {"locked": True},
        "score": {
            "value": 90,
            "label": "Low Risk",
            "details": ["✅ Seguro"]
        },
        "alerts": [],
        "risks": [],
        "critical_functions": [],
        "deployer": {
            "address": "0x123",
            "token_history": []
        },
        "fees": {
            "buy": 0.0,
            "sell": 0.0,
            "buy_mutable": False,
            "sell_mutable": False
        },
        "honeypot": {
            "is_honeypot": False,
            "buy_success": True,
            "sell_success": True,
            "slippage": 0.5,
            "error_message": None
        },
        "top_holders": {
            "holders": [],
            "top_1_percent": 0.0,
            "top_10_percent": 0.0,
            "top_50_percent": 0.0
        }
    }

    with patch("app.routes.audit.audit_token", return_value=mock_result):
        response = client.get("/audit/0x123")
        assert response.status_code == 200
        assert response.json()["name"] == "MockToken"
