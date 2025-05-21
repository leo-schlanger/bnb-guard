import os
import sys
import pytest
from unittest.mock import patch, MagicMock, call
from fastapi import HTTPException

# Adiciona o diretório raiz ao path para garantir que os imports funcionem
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
print(f"\n=== DEBUG: Diretório raiz: {root_dir}")
print(f"=== DEBUG: sys.path antes: {sys.path}")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

print(f"=== DEBUG: sys.path depois: {sys.path}")

# Tenta importar o módulo auditor
try:
    from app.services.auditor import audit_token
    print("=== DEBUG: Módulo auditor importado com sucesso")
except ImportError as e:
    print(f"=== ERRO ao importar auditor: {e}")
    print(f"=== sys.path: {sys.path}")
    print(f"=== Conteúdo do diretório: {os.listdir(root_dir)}")
    print(f"=== Conteúdo do diretório app: {os.listdir(os.path.join(root_dir, 'app'))}")
    print(f"=== Conteúdo do diretório services: {os.listdir(os.path.join(root_dir, 'app', 'services'))}")
    raise

from app.core.interfaces.analyzer import AnalysisResult

@pytest.fixture
def mock_metadata():
    return {
        "name": "ScamToken",
        "symbol": "SCAM",
        "decimals": 18,
        "totalSupply": 1000000.0,  # Note que é totalSupply, não total_supply
        "owner": "0x0000000000000000000000000000000000000000",
        "status": "1",
        "message": "OK",
        "SourceCode": "pragma solidity ^0.8.0;\n\ncontract ScamToken {\n    string public name = \"ScamToken\";\n    string public symbol = \"SCAM\";\n    uint8 public decimals = 18;\n    uint256 public totalSupply = 1000000 * 10**18;\n    \n    function mint(address to, uint256 amount) public {\n        // Implementação fictícia\n    }\n}",
        "ABI": "[{\"constant\":true,\"inputs\":[],\"name\":\"name\",\"outputs\":[{\"name\":\"\",\"type\":\"string\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"symbol\",\"outputs\":[{\"name\":\"\",\"type\":\"string\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"}]",
        "functions": ["mint"],
        "buy_tax": 25.0,
        "sell_tax": 25.0,
        "buy_mutable": True,
        "sell_mutable": True,
        "has_blacklist": True,
        "has_mint": True,
        "lp_info": {"locked": False},
        "deployer_address": "0xBAD",
        "deployer_token_count": 6,
        "holders": [{"address": "0x1", "percent": 30.0}]
    }

@pytest.fixture
def mock_static_analysis():
    return {
        "static": [{
            "type": "dangerous_functions",
            "message": "Found 1 dangerous functions/modifiers",
            "severity": "high"
        }],
        "functions": [{
            "name": "mint",
            "type": "dangerous_function",
            "severity": "high"
        }],
        "owner": {
            "renounced": False,
            "functions": ["mint"]
        },
        "alerts": [
            "🚨 Critical functions detected",
            "⚠️ High buy tax (25.0%)",
            "⚠️ High sell tax (25.0%)",
            "⚠️ LP is not properly locked (>70%)",
            "⚠️ High holder concentration (30.0%)"
        ]
    }

@pytest.fixture
def mock_dynamic_analysis():
    return {
        "honeypot": {
            "is_honeypot": True,
            "buy_success": False,
            "sell_success": False,
            "slippage": 90.0,
            "error_message": "Venda bloqueada",
            "high_tax": True,
            "tax_discrepancy": False
        },
        "fees": {
            "buy": 25.0,
            "sell": 25.0,
            "buy_mutable": True,
            "sell_mutable": True,
            "buy_slippage": 25.0,
            "sell_slippage": 25.0
        }
    }

@pytest.fixture
def mock_onchain_analysis():
    return {
        "deployer": {"address": "0xBAD", "token_history": []},
        "top_holders": {
            "top_1_percent": 30.0,
            "top_10_percent": 50.0,
            "top_50_percent": 80.0,
            "holders": [{"address": "0x1", "percentage": "30.00%"}]
        },
        "lp_info": {"locked": False},
        "lp_locked": False,
        "lp_percent_locked": 20.0,
        "deployer_flagged": True,
        "deployer_token_count": 6,
        "warnings": ["🚨 Deployer created many tokens"]
    }

@pytest.fixture
def mock_risk_score():
    return {
        "risk_score": 85.0,  # Score que deve resultar em nota A
        "alerts": ["⚠️ LP não está travada"],
        "details": ["⚠️ LP não está travada"],  # Adicionando a chave 'details' que é esperada
        "risks": [],
        "grade": "A"
    }

@pytest.fixture
def mock_auditor_dependencies(monkeypatch, mock_metadata, mock_static_analysis, 
                          mock_dynamic_analysis, mock_onchain_analysis, mock_risk_score):
    # Mock das funções de análise
    def mock_fetch_token_metadata(addr):
        print(f"\n=== MOCK fetch_token_metadata called with {addr} ===")
        print(f"mock_metadata: {mock_metadata}")
        print(f"mock_metadata type: {type(mock_metadata)}")
        print(f"mock_metadata['name']: {mock_metadata['name']}" if 'name' in mock_metadata else "'name' not in mock_metadata")
        print(f"mock_metadata keys: {mock_metadata.keys()}")
        print(f"mock_metadata['name'] type: {type(mock_metadata['name'])}")
        print(f"mock_metadata['name'] value: {mock_metadata['name']}")
        
        # Força o retorno dos valores esperados
        result = {
            'name': 'ScamToken',
            'symbol': 'SCAM',
            'totalSupply': '1000000.0',  # Garantindo que é uma string para simular a resposta da API
            'SourceCode': mock_metadata.get('SourceCode', ''),
            'ABI': mock_metadata.get('ABI', ''),
            'decimals': 18,
            'owner': mock_metadata.get('owner', ''),
            'status': '1',
            'message': 'OK',
            'buy_tax': 25.0,
            'sell_tax': 25.0,
            'buy_mutable': True,
            'sell_mutable': True,
            'has_blacklist': True,
            'has_mint': True,
            'lp_info': {'locked': False},
            'deployer_address': '0xBAD',
            'deployer_token_count': 6,
            'holders': [{'address': '0x1', 'percent': 30.0}]
        }
        
        print(f"\n=== MOCK fetch_token_metadata retornando: {result}")
        print(f"Tipo do nome retornado: {type(result['name'])}")
        print(f"Valor do nome retornado: {result['name']}")
        print(f"Tipo do totalSupply retornado: {type(result['totalSupply'])}")
        print(f"Valor do totalSupply retornado: {result['totalSupply']}")
        
        # Adiciona logs de depuração
        print(f"\n=== MOCK fetch_token_metadata retornando: {result}")
        print(f"Tipo do nome retornado: {type(result['name'])}")
        print(f"Valor do nome retornado: {result['name']}")
        print(f"Tipo do totalSupply retornado: {type(result['totalSupply'])}")
        print(f"Valor do totalSupply retornado: {result['totalSupply']}")
        
        # Retorna o resultado mesmo que o endereço não seja o esperado
        return result
    
    # Verifica se o módulo está sendo importado corretamente
    import sys
    if 'app.services.auditor' in sys.modules:
        print("\n=== DEBUG: app.services.auditor já está importado ===")
        # Se o módulo já estiver importado, precisamos garantir que o mock seja aplicado corretamente
        import importlib
        import app.services.auditor
        importlib.reload(app.services.auditor)
    else:
        print("\n=== DEBUG: app.services.auditor NÃO está importado ===")
    
    # Aplica os mocks
    monkeypatch.setattr("app.services.auditor.fetch_token_metadata", mock_fetch_token_metadata)
    monkeypatch.setattr("app.services.auditor.analyze_static", lambda src: mock_static_analysis)
    monkeypatch.setattr("app.services.auditor.analyze_dynamic", lambda addr: mock_dynamic_analysis)
    monkeypatch.setattr("app.services.auditor.analyze_onchain", lambda metadata: mock_onchain_analysis)
    
    # Verifica se o mock foi aplicado corretamente
    from app.services.auditor import fetch_token_metadata, analyze_static, analyze_dynamic, analyze_onchain
    print(f"\n=== DEBUG: Verificando mocks ===")
    print(f"fetch_token_metadata é mock: {fetch_token_metadata.__code__ == mock_fetch_token_metadata.__code__}")
    print(f"analyze_static é mock: {analyze_static.__code__ == (lambda src: mock_static_analysis).__code__}")
    print(f"analyze_dynamic é mock: {analyze_dynamic.__code__ == (lambda addr: mock_dynamic_analysis).__code__}")
    print(f"analyze_onchain é mock: {analyze_onchain.__code__ == (lambda metadata: mock_onchain_analysis).__code__}")
    
    # Força a recarga do módulo para garantir que o mock seja aplicado
    import importlib
    import app.services.auditor
    importlib.reload(app.services.auditor)
    
    # Mock da função calculate_risk_score para retornar o risk_score como um valor numérico
    def mock_calculate_risk_score(static_alerts, dynamic_alerts, onchain_alerts):
        print(f"\n=== MOCK calculate_risk_score chamado ===")
        print(f"static_alerts: {static_alerts}")
        print(f"dynamic_alerts: {dynamic_alerts}")
        print(f"onchain_alerts: {onchain_alerts}")
        
        # Garante que o mock_risk_score tem a estrutura correta
        # Retorna um dicionário com a estrutura esperada pela função audit_token
        result = {
            'risk_score': 20.0,  # A chave principal deve ser 'risk_score'
            'alerts': mock_risk_score.get('alerts', []),  # Mantém 'alerts' para compatibilidade
            'details': mock_risk_score.get('details', mock_risk_score.get('alerts', [])),  # Usa 'details' se existir, senão usa 'alerts'
            'risks': mock_risk_score.get('risks', []),
            'grade': mock_risk_score.get('grade', 'D')
        }
        print(f"Resultado do mock_calculate_risk_score: {result}")
        return result
        
    monkeypatch.setattr("app.services.auditor.calculate_risk_score", mock_calculate_risk_score)

from unittest.mock import patch, MagicMock

# Cria um mock para a função fetch_token_metadata
def mock_fetch_token_metadata(token_address):
    return {
        "name": "ScamToken",
        "symbol": "SCAM",
        "totalSupply": 1000000.0,
        "SourceCode": "pragma solidity ^0.8.0;"
    }

def test_audit_token_success(mock_metadata, mock_onchain_analysis, mock_dynamic_analysis, mock_risk_score, monkeypatch):
    """
    Testa o fluxo de sucesso da função audit_token.
    Verifica se a função retorna a estrutura esperada com os valores corretos.
    """
    # Configuração inicial
    print("\n=== DEBUG: Iniciando teste test_audit_token_success...")
    
    # Configura o mock_risk_score para retornar um score baixo que resulte em nota D
    expected_risk_score = {
        'risk_score': 85.0,  # Score que deve resultar em nota A
        'grade': 'A',
        'alerts': [
            '⚠️ Ownership not renounced',
            '⚠️ Mutable fees',
            '⚠️ Fees above 10%',
            '⚠️ LP not locked'
        ],
        'risks': [
            {'type': 'owner', 'description': 'Contract still under owner control', 'severity': 'high'},
            {'type': 'fees', 'description': 'Fees can be changed via setFee functions', 'severity': 'medium'},
            {'type': 'lp', 'description': 'Liquidity is not locked', 'severity': 'high'}
        ]
    }
    
    # Atualiza o mock_risk_score com os valores esperados
    mock_risk_score.update(expected_risk_score)
    print(f"=== DEBUG: mock_risk_score configurado: {mock_risk_score}")
    
    # Aplica os mocks usando monkeypatch
    monkeypatch.setattr('app.core.utils.metadata.fetch_token_metadata', mock_fetch_token_metadata)
    
    # Configura os mocks para as funções de análise
    with patch('app.services.auditor.analyze_static', return_value={'static': [], 'functions': [], 'owner': {'renounced': False}}) as mock_static, \
         patch('app.services.auditor.analyze_dynamic', return_value=mock_dynamic_analysis) as mock_dynamic, \
         patch('app.services.auditor.analyze_onchain', return_value=mock_onchain_analysis) as mock_onchain, \
         patch('app.services.auditor.calculate_risk_score', return_value=expected_risk_score) as mock_calc_risk:
            
        # Configura o comportamento do mock_calc_risk para retornar o expected_risk_score
        mock_calc_risk.return_value = expected_risk_score
        
        # Importa o módulo auditor após configurar os mocks
        import sys
        if 'app.services.auditor' in sys.modules:
            del sys.modules['app.services.auditor']
            
        from app.services.auditor import audit_token
        
        print("=== DEBUG: Mocks configurados com sucesso")
        
        # Chama a função audit_token
        print("\n=== DEBUG: Chamando audit_token...")
        
        # Executa o teste
        result = audit_token("0x123", "0x456")
        
        # Verificações
        print(f"\n=== DEBUG: Resultado de audit_token: {result}")
        print(f"=== DEBUG: Tipo do resultado: {type(result)}")
        
        # Verifica se o resultado é um dicionário
        assert isinstance(result, dict), f"O resultado deve ser um dicionário, mas foi {type(result)}"
        
        # Verifica as chaves principais
        expected_keys = ['name', 'symbol', 'supply', 'score', 'honeypot', 'fees', 
                      'lp_lock', 'owner', 'critical_functions', 'top_holders',
                      'deployer', 'risks']
        for key in expected_keys:
            assert key in result, f"O resultado deve conter a chave '{key}'"
        
        # Verifica o nome do token
        assert result['name'] == 'ScamToken', f"O nome do token deve ser 'ScamToken', mas foi {result.get('name')}"
        
        # Verifica a estrutura do score
        assert 'score' in result, "O resultado deve conter a chave 'score'"
        score = result['score']
        assert isinstance(score, dict), "O score deve ser um dicionário"
        
        # Verifica o risk_score
        assert 'risk_score' in score, "O score deve conter a chave 'risk_score'"
        # Verifica se o risk_score está dentro de uma faixa razoável (0-100)
        assert 0 <= score['risk_score'] <= 100, f"O risk_score deve estar entre 0 e 100, mas foi {score.get('risk_score')}"
        
        # Verifica o valor do score
        assert 'value' in score, "O score deve conter a chave 'value'"
        assert isinstance(score['value'], (int, float)), f"O valor do score deve ser um número, mas é {type(score['value'])}"
        
        # Verifica a grade
        assert 'grade' in score, "O score deve conter a chave 'grade'"
        
        # Verificações adicionais
        assert 'value' in result['score'], "result['score'] deve conter a chave 'value'"
        assert isinstance(result["score"]["value"], (int, float)), \
            f"Score deve ser um número, mas é {type(result['score']['value'])}"
        
        # Verifica se o grade está correto
        assert result["score"]["grade"] == mock_risk_score["grade"], \
            f"Expected grade {mock_risk_score['grade']}, got {result['score']['grade']}"
        
        # Verifica se os risks estão corretos
        assert "risks" in result, "O resultado deve conter a chave 'risks'"
        assert isinstance(result["risks"], list), "risks deve ser uma lista"
        
        # Verifica se o risk_score está dentro do intervalo válido (0-100)
        assert 0 <= result["score"]["value"] <= 100, \
            f"Score deve estar entre 0 e 100, mas é {result['score']['value']}"
        
        # Verifica se o supply é um número
        assert isinstance(result["supply"], (int, float)), \
            f"Supply deve ser um número, mas é {type(result['supply'])}"
        
        # Verifica o restante da estrutura
        assert result["lp_lock"]["locked"] is False
        assert result["lp_lock"]["percent_locked"] == 20.0
        assert result["top_holders"]["top_1_percent"] == 30.0
        assert len(result["top_holders"]["holders"]) == 1
        assert result["deployer"]["address"] == "0xBAD"
        assert result["honeypot"]["is_honeypot"] is True
        assert result["fees"]["buy_tax"] == 30.0
        assert result["fees"]["sell_tax"] == 30.0
        assert "⚠️ LP não está travada" in result["score"]["details"]
        # Verifica se o deployer está marcado como flagged
        assert result["deployer"]["flagged"] is True
        
        # Verificações adicionais de score
        assert 'score' in result, "O resultado deve conter a chave 'score'"
        assert isinstance(result['score'], dict), "result['score'] deve ser um dicionário"
        
        # Verifica se 'risk_score' está no dicionário de score
        assert 'risk_score' in result['score'], "result['score'] deve conter a chave 'risk_score'"
        
        # Verifica o valor de risk_score
        risk_score = result['score']['risk_score']
        print(f"=== DEBUG: risk_score no resultado: {risk_score} (tipo: {type(risk_score)})")
        
        # Garante que o risk_score seja um número
        assert isinstance(risk_score, (int, float)), "risk_score deve ser um número"
        
        # Verifica o valor de risk_score
        assert risk_score == mock_risk_score["risk_score"], f"O risk_score deve ser {mock_risk_score['risk_score']}, mas foi {risk_score}"
        
        # Verifica se o score é um número
        assert isinstance(result["score"]["value"], (int, float)), \
            f"Score deve ser um número, mas é {type(result['score']['value'])}"
        
        # Verifica se o score está dentro do intervalo válido (0-100)
        assert 0 <= result["score"]["value"] <= 100, \
            f"Score deve estar entre 0 e 100, mas é {result['score']['value']}"
        
        # Verifica se o grade está correto
        assert result["score"]["grade"] == mock_risk_score["grade"], \
            f"Expected grade {mock_risk_score['grade']}, got {result['score']['grade']}"
        
        # Verifica se o score é o esperado
        assert result["score"]["value"] == mock_risk_score["risk_score"], \
            f"Expected score {mock_risk_score['risk_score']}, got {result['score']['value']}"
        
        # Verifica se os detalhes do score estão corretos
        assert "⚠️ LP não está travada" in result["score"]["details"], \
            f"Expected '⚠️ LP não está travada' in {result['score']['details']}"
        
        # Verifica a grade final
        print(f"=== DEBUG: Nota final: {result['score']['grade']}")
        print(f"=== DEBUG: risk_score: {result['score']['risk_score']}")
        print(f"=== DEBUG: Detalhes do score: {result['score']}")
        assert result["score"]["grade"] == "A"

def test_audit_token_with_lp(mock_auditor_dependencies, mock_metadata, mock_onchain_analysis):
    # Testa auditoria com token de LP
    result = audit_token("0xdead", lp_token_address="0xLP")
    assert result["name"] == "ScamToken"
    assert result["lp_lock"]["locked"] is False  # Deve herdar do mock_onchain_analysis

    # Testa com LP travada
    mock_onchain_analysis["lp_locked"] = True
    mock_onchain_analysis["lp_percent_locked"] = 100.0
    result = audit_token("0xdead", lp_token_address="0xLP")
    assert result["lp_lock"]["locked"] is True
    assert result["lp_lock"]["locked_percentage"] == 100.0

def test_audit_token_metadata_error(monkeypatch):
    # Testa erro ao buscar metadados
    monkeypatch.setattr(
        "app.services.auditor.fetch_token_metadata", 
        lambda addr: (_ for _ in ()).throw(Exception("Erro de rede"))
    )
    
    result = audit_token("0xERROR")
    assert result["name"] == "Error"
    assert result["score"]["value"] == 0
    assert "❌ Error processing token" in result["score"]["details"][0]

def test_audit_token_static_analysis_error(monkeypatch):
    # Configura o mock para fetch_token_metadata
    def mock_fetch_metadata(address):
        return {
            "name": "Test Token",
            "symbol": "TEST",
            "totalSupply": "1000000",
            "SourceCode": ""
        }
        
    # Configura o mock para analyze_static
    def raise_error(src):
        raise Exception("Erro na análise estática")
        
    # Aplica os mocks
    monkeypatch.setattr("app.services.auditor.fetch_token_metadata", mock_fetch_metadata)
    monkeypatch.setattr("app.services.auditor.analyze_static", raise_error)
    
    # Executa o teste
    result = audit_token("0x123")
    print("\nMensagem de erro retornada:", result["score"]["details"][0])  # Para depuração
    
    # Verificações
    assert result["name"] == "Error"  # Nome padrão quando há erro
    assert "Erro na análise estática" in result["score"]["details"][0]  # Verifica apenas a mensagem de erro

def test_audit_token_dynamic_analysis_error(monkeypatch):
    # Configura o mock para fetch_token_metadata
    def mock_fetch_metadata(address):
        return {
            "name": "Test Token",
            "symbol": "TEST",
            "totalSupply": "1000000",
            "SourceCode": ""
        }
    
    # Configura o mock para analyze_static (sucesso)
    def mock_static_analysis(src):
        return {"static": [], "functions": [], "owner": {"renounced": True}}
    
    # Configura o mock para analyze_dynamic (erro)
    def mock_dynamic_analysis(addr):
        raise Exception("Erro na análise dinâmica")
    
    # Aplica os mocks
    monkeypatch.setattr("app.services.auditor.fetch_token_metadata", mock_fetch_metadata)
    monkeypatch.setattr("app.services.auditor.analyze_static", mock_static_analysis)
    monkeypatch.setattr("app.services.auditor.analyze_dynamic", mock_dynamic_analysis)
    
    # Executa o teste
    result = audit_token("0x123")
    print("\nMensagem de erro retornada:", result["score"]["details"][0])  # Para depuração
    
    # Verificações
    assert result["name"] == "Error"  # Nome padrão quando há erro
    assert "Erro na análise dinâmica" in result["score"]["details"][0]  # Verifica a mensagem de erro

def test_audit_token_onchain_analysis_error(monkeypatch):
    # Configura o mock para fetch_token_metadata
    def mock_fetch_metadata(address):
        return {
            "name": "Test Token",
            "symbol": "TEST",
            "totalSupply": "1000000",
            "SourceCode": "",
            "holders": []
        }
    
    # Configura o mock para analyze_static (sucesso)
    def mock_static_analysis(src):
        return {"static": [], "functions": [], "owner": {"renounced": True}}
    
    # Configura o mock para analyze_dynamic (sucesso)
    def mock_dynamic_analysis(addr):
        return {"honeypot": {"is_honeypot": False}, "fees": {}}
    
    # Configura o mock para analyze_onchain (erro)
    def mock_onchain_analysis(metadata):
        raise Exception("Erro na análise on-chain")
    
    # Aplica os mocks
    monkeypatch.setattr("app.services.auditor.fetch_token_metadata", mock_fetch_metadata)
    monkeypatch.setattr("app.services.auditor.analyze_static", mock_static_analysis)
    monkeypatch.setattr("app.services.auditor.analyze_dynamic", mock_dynamic_analysis)
    monkeypatch.setattr("app.services.auditor.analyze_onchain", mock_onchain_analysis)
    
    # Executa o teste
    result = audit_token("0x123")
    print("\nMensagem de erro retornada:", result["score"]["details"][0])  # Para depuração
    
    # Verificações
    assert result["name"] == "Error"  # Nome padrão quando há erro
    assert "Erro na análise on-chain" in result["score"]["details"][0]  # Verifica a mensagem de erro

def test_audit_token_with_exception(monkeypatch):
    # Force error in fetch_token_metadata
    monkeypatch.setattr("app.services.auditor.fetch_token_metadata", lambda address: (_ for _ in ()).throw(Exception("Simulated error")))

    result = audit_token("0xERROR")

    assert result["name"] == "Error"
    assert result["score"]["value"] == 0
    assert "Simulated error" in result["honeypot"]["error"]
    assert "❌" in result["score"]["details"][0]

def test_audit_token_raises(monkeypatch):
    def fake_fetch(*args, **kwargs):
        raise Exception("Audit error")
    
    monkeypatch.setattr("app.services.auditor.fetch_token_metadata", fake_fetch)

    result = audit_token("0x456")
    assert result["name"] == "Error"
    assert result["score"]["value"] == 0
    assert "❌ Error processing token" in result["score"]["details"][0]


def test_audit_token_exception(monkeypatch):
    def raise_error(address):
        raise Exception("Forced fetch error")

    monkeypatch.setattr("app.services.auditor.fetch_token_metadata", raise_error)

    result = audit_token("0xBEEF")
    assert result["name"] == "Error"
    assert result["symbol"] == "ERR"
    assert result["score"]["value"] == 0
    assert "❌ Error processing token" in result["score"]["details"][0]

def test_audit_token_with_lp(monkeypatch):
    monkeypatch.setattr("app.services.auditor.fetch_token_metadata", lambda address: {
        "name": "AuditLP",
        "symbol": "AUD",
        "totalSupply": 1234567,
        "SourceCode": "",
        "deployer_address": "0xDEAD",
        "deployer_token_count": 2,
        "holders": [],
        "lp_info": {}
    })

    monkeypatch.setattr("app.services.auditor.analyze_static", lambda src: {})
    monkeypatch.setattr("app.services.auditor.analyze_dynamic", lambda addr: {})
    monkeypatch.setattr("app.services.auditor.analyze_onchain", lambda metadata: {
        "top_holders": {
            "top_1_percent": 10,
            "top_10_percent": 30,
            "top_50_percent": 50,
            "holders": []
        },
        "deployer": {"address": "0xDEAD", "token_history": []}
    })
    monkeypatch.setattr("app.services.auditor.calculate_risk_score", lambda *_: {
        "risk_score": 90,
        "alerts": [],
        "risks": []
    })

    result = audit_token("0x456", lp_token_address="0xLP")
    assert result["lp_lock"]["locked_percentage"] == 100.0

