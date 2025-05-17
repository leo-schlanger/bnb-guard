import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi.testclient import TestClient
from app.routes.audit import router
from fastapi import FastAPI
import pytest
from unittest.mock import patch

app = FastAPI()
app.include_router(router)

@pytest.fixture
def client():
    return TestClient(app)

def test_audit_route_success(client):
    mock_result = {
        "functions": [],
        "is_owner": True,
        "lp_locked": True,
        "score": {
            "value": 85,
            "details": ["✅ Sem riscos críticos detectados"]
        },
        "risks": [],
        "alerts": [],
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
        "honeypot": {"is_honeypot": False},
        "lp_lock": {"locked": True}
    }

    with patch("app.services.auditor.audit_token", return_value=mock_result):
        response = client.get("/audit/0x123")
        assert response.status_code == 200
        assert response.json() == mock_result
