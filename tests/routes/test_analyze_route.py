from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import pytest
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_analyze_result():
    return {
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

def test_analyze_route_success(mock_analyze_result):
    with patch("app.routes.analyze.analyze_token", return_value=mock_analyze_result) as mock_analyze:
        # Testa requisição bem-sucedida
        response = client.get("/analyze/0x123")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "MockToken"
        assert data["symbol"] == "MTK"
        assert data["score"]["value"] == 90
        assert data["honeypot"]["is_honeypot"] is False
        
        # Verifica se a função foi chamada com os parâmetros corretos
        mock_analyze.assert_called_once_with("0x123", None)
        
        # Testa com parâmetro lp_token
        response = client.get("/analyze/0x123?lp_token=0x456")
        assert response.status_code == 200
        mock_analyze.assert_called_with("0x123", "0x456")

def test_analyze_route_invalid_token():
    # Testa com endereço de token inválido
    response = client.get("/analyze/invalid_token")
    assert response.status_code == 422  # Erro de validação
    assert "detail" in response.json()

def test_analyze_route_error_handling():
    # Testa tratamento de erro na função analyze_token
    with patch("app.routes.analyze.analyze_token", side_effect=Exception("Erro de teste")):
        response = client.get("/analyze/0x123")
        assert response.status_code == 500
        assert "detail" in response.json()
        assert "Erro ao analisar o token" in response.json()["detail"]

def test_analyze_route_http_exception():
    # Testa tratamento de HTTPException
    with patch("app.routes.analyze.analyze_token", side_effect=HTTPException(status_code=400, detail="Bad Request")):
        response = client.get("/analyze/0x123")
        assert response.status_code == 400
        assert response.json()["detail"] == "Bad Request"

def test_analyze_route_without_lp_token():
    # Testa sem parâmetro lp_token
    with patch("app.routes.analyze.analyze_token") as mock_analyze:
        mock_analyze.return_value = {"name": "TokenSemLP", "symbol": "TSL", "score": {"value": 80}}
        response = client.get("/analyze/0x789")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TokenSemLP"
        mock_analyze.assert_called_once_with("0x789", None)
