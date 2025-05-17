from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_valid_token():
    token = "0xe9e7cea3dedca5984780bafc599bd69add087d56"  # BUSD antigo
    response = client.get(f"/analyze/{token}")
    assert response.status_code == 200

    data = response.json()
    assert "address" in data
    assert "score" in data
    assert "status" in data
    assert isinstance(data["alerts"], list)

def test_analyze_invalid_token():
    token = "0x000000000000000000000000000000000000dEaD"
    response = client.get(f"/analyze/{token}")
    assert response.status_code == 200
    data = response.json()
    assert data["score"] < 100  # Deve detectar algum risco
