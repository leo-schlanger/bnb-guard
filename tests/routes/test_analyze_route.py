from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

def test_analyze_route_success():
    mock_result = {
        "token_address": "0x123",
        "name": "MockToken",
        "symbol": "MTK",
        "supply": 1000000,
        "functions": ["transfer", "approve"],
        "owner": {"renounced": True, "functions": []},
        "score": {
            "value": 90,
            "label": "Low Risk",
            "details": ["✅ Seguro"]
        },
        "honeypot": {
            "is_honeypot": False,
            "buy_success": True,
            "sell_success": True,
            "slippage": 0.3,
            "error_message": None
        },
        "fees": {
            "buy": 1.0,
            "sell": 1.0,
            "buy_mutable": False,
            "sell_mutable": False
        },
        "lp_lock": {
            "locked": True,
            "locked_percentage": 95.0,
            "unlock_date": "2025-12-31"
        },
        "top_holders": [
            {"address": "0x1", "percent": 10.0}
        ],
        "risks": []
    }

    with patch("app.routes.analyze.analyze_token", return_value=mock_result):
        response = client.get("/analyze/0x123")
        assert response.status_code == 200
        assert response.json()["name"] == "MockToken"
