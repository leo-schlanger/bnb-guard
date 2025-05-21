import pytest
from fastapi.testclient import TestClient
from app.main import app

# TODO: Adicionar mais testes de inicialização da aplicação

# Cria um cliente de teste para a aplicação
client = TestClient(app)

def test_app_starts():
    """Testa se a aplicação inicializa corretamente."""
    # Verifica se a instância do FastAPI foi criada
    assert app is not None
    # Verifica se o título da aplicação está definido
    assert app.title == "BNBGuard API"

def test_root_endpoint():
    """Testa o endpoint raiz da aplicação."""
    # Faz uma requisição GET para o endpoint raiz
    response = client.get("/")
    # Verifica se o status code é 200 (OK)
    assert response.status_code == 200
    # Verifica se a resposta contém uma mensagem
    response_json = response.json()
    assert "message" in response_json
    # Verifica se a mensagem contém o nome da aplicação
    assert "BNBGuard API" in response_json["message"]
