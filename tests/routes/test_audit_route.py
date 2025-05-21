from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import pytest
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_audit_result():
    return {
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
            "buy_slippage": 0.0,
            "sell_slippage": 0.0,
            "buy_mutable": False,
            "sell_mutable": False
        },
        "honeypot": {
            "is_honeypot": False,
            "buy_success": True,
            "sell_success": True,
            "high_tax": False,
            "tax_discrepancy": False,
            "error": None
        },
        "top_holders": {
            "holders": [],
            "top_1_percent": 0.0,
            "top_10_percent": 0.0,
            "top_50_percent": 0.0
        }
    }

def test_audit_route_success(mock_audit_result):
    with patch("app.routes.audit.audit_token", return_value=mock_audit_result) as mock_audit:
        # Testa sucesso
        response = client.get("/audit/0x123")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "MockToken"
        assert data["score"]["value"] == 90
        assert data["lp_locked"] is True
        
        # Verifica se o token de auditoria foi chamado com o endereço correto
        mock_audit.assert_called_once_with("0x123")
        
        # Testa com parâmetro lp_token
        response = client.get("/audit/0x123?lp_token=0x456")
        assert response.status_code == 200
        mock_audit.assert_called_with("0x123", "0x456")

def test_audit_route_invalid_token():
    # Testa com endereço de token inválido
    response = client.get("/audit/invalid_token")
    assert response.status_code == 422  # Erro de validação
    assert "detail" in response.json()

def test_audit_route_error_handling():
    # Testa tratamento de erro na função audit_token
    with patch("app.routes.audit.audit_token", side_effect=Exception("Erro de teste")):
        response = client.get("/audit/0x123")
        assert response.status_code == 500
        assert "detail" in response.json()
        assert "Erro ao processar o token" in response.json()["detail"]

def test_audit_route_http_exception():
    # Testa tratamento de HTTPException
    with patch("app.routes.audit.audit_token", side_effect=HTTPException(status_code=400, detail="Bad Request")):
        response = client.get("/audit/0x123")
        assert response.status_code == 400
        assert response.json()["detail"] == "Bad Request"

def test_audit_route_without_lp_token():
    # Testa sem parâmetro lp_token
    with patch("app.routes.audit.audit_token") as mock_audit:
        mock_audit.return_value = {"name": "TokenSemLP", "symbol": "TSL", "score": {"value": 80}}
        response = client.get("/audit/0x789")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TokenSemLP"
        mock_audit.assert_called_once_with("0x789")
