import pytest
from app.core.analyzers.dynamic_analyzer import analyze_dynamic, _calculate_tax_and_slippage, _check_suspicious_patterns

def test_analyze_dynamic_full_success():
    """Testa uma análise dinâmica bem-sucedida com compra e venda."""
    # Dados de simulação
    data = {
        "buy": {
            "success": True,
            "expected_amount_out": 100,
            "amount_out": 95  # 5% de taxa
        },
        "sell": {
            "success": True,
            "expected_amount_out": 100,
            "amount_out": 90  # 10% de taxa
        }
    }
    
    # Chama a função com os dados de simulação
    result = analyze_dynamic(data)
    
    # Verifica estrutura do retorno
    assert "honeypot" in result
    assert "fees" in result
    
    # Verifica honeypot
    assert result["honeypot"]["is_honeypot"] is False
    assert result["honeypot"]["buy_success"] is True
    assert result["honeypot"]["sell_success"] is True
    assert result["honeypot"]["high_tax"] is False
    assert "tax_discrepancy" in result["honeypot"]
    
    # Verifica taxas
    assert result["fees"]["buy"] == 5.0  # 5% de taxa
    assert result["fees"]["sell"] == 10.0  # 10% de taxa
    assert "buy_slippage" in result["fees"]
    assert "sell_slippage" in result["fees"]
    assert "buy_mutable" in result["fees"]
    assert "sell_mutable" in result["fees"]

def test_analyze_dynamic_honeypot():
    """Testa detecção de honeypot (compra funciona, venda falha)."""
    # Dados de simulação para um honeypot (compra funciona, venda falha)
    data = {
        "buy": {
            "success": True,
            "expected_amount_out": 200,
            "amount_out": 180  # 10% de taxa
        },
        "sell": {
            "success": False  # Venda falha - característica de honeypot
        }
    }
    
    # Chama a função com os dados de simulação
    result = analyze_dynamic(data)
    
    # Verifica se detectou corretamente o honeypot
    assert result["honeypot"]["is_honeypot"] is True
    assert result["honeypot"]["buy_success"] is True
    assert result["honeypot"]["sell_success"] is False
    
    # Verifica taxas
    assert "fees" in result
    assert "buy" in result["fees"]
    assert "sell" in result["fees"]
    assert "buy_slippage" in result["fees"]
    assert "sell_slippage" in result["fees"]
    assert "buy_mutable" in result["fees"]
    assert "sell_mutable" in result["fees"]

def test_analyze_dynamic_high_tax():
    """Testa detecção de taxas altas."""
    # Dados de simulação com taxas altas
    data = {
        "buy": {
            "success": True,
            "expected_amount_out": 100,
            "amount_out": 80  # 20% de taxa (alta)
        },
        "sell": {
            "success": True,
            "expected_amount_out": 100,
            "amount_out": 75  # 25% de taxa (alta)
        }
    }
    
    # Chama a função com os dados de simulação
    result = analyze_dynamic(data)
    
    # Verifica se detectou corretamente as taxas altas
    assert result["honeypot"]["high_tax"] is True
    assert "fees" in result
    assert "buy" in result["fees"]
    assert "sell" in result["fees"]
    assert "buy_slippage" in result["fees"]
    assert "sell_slippage" in result["fees"]
    assert "buy_mutable" in result["fees"]
    assert "sell_mutable" in result["fees"]

def test_analyze_dynamic_tax_discrepancy():
    """Testa detecção de discrepância entre taxas."""
    # Dados de simulação com discrepância entre taxas
    data = {
        "buy": {
            "success": True,
            "expected_amount_out": 100,
            "amount_out": 95  # 5% de taxa
        },
        "sell": {
            "success": True,
            "expected_amount_out": 100,
            "amount_out": 80  # 20% de taxa (discrepância > 10%)
        }
    }
    
    # Chama a função com os dados de simulação
    result = analyze_dynamic(data)
    
    # Verifica se detectou corretamente a discrepância entre taxas
    assert result["honeypot"]["tax_discrepancy"] is True
    assert "fees" in result
    assert "buy" in result["fees"]
    assert "sell" in result["fees"]
    assert "buy_slippage" in result["fees"]
    assert "sell_slippage" in result["fees"]
    assert "buy_mutable" in result["fees"]
    assert "sell_mutable" in result["fees"]

def test_analyze_dynamic_invalid_input():
    """Testa comportamento com entrada inválida."""
    # Testa com entrada inválida (não dicionário)
    invalid_input = "not a dictionary"
    
    # Chama a função com entrada inválida
    result = analyze_dynamic(invalid_input)
    
    # Verifica se retornou erro para entrada inválida
    assert "error" in result
    assert "honeypot" in result
    assert "fees" in result
    
    # Verifica a estrutura do honeypot
    assert "is_honeypot" in result["honeypot"]
    assert "buy_success" in result["honeypot"]
    assert "sell_success" in result["honeypot"]
    assert "error" in result["honeypot"]
    
    # Verifica a estrutura das taxas
    assert "buy" in result["fees"]
    assert "sell" in result["fees"]
    assert "buy_mutable" in result["fees"]
    assert "sell_mutable" in result["fees"]
    
    # Verifica a mensagem de erro
    assert "Resultado de simulação inválido" in result["error"]
    assert "Resultado de simulação inválido" in result["honeypot"]["error"]

def test_analyze_dynamic_missing_values():
    """Testa comportamento com valores ausentes."""
    # Dados de simulação com valores ausentes/None
    data = {
        "buy": {
            "success": True, 
            "expected_amount_out": None,  # Valor ausente
            "amount_out": 90
        },
        "sell": {
            "success": True, 
            "expected_amount_out": 100, 
            "amount_out": None  # Valor ausente
        }
    }
    
    # Chama a função com os dados de simulação
    result = analyze_dynamic(data)
    
    # Verifica se as taxas foram calculadas como 0 devido aos valores ausentes
    assert "fees" in result
    assert "buy" in result["fees"]
    assert "sell" in result["fees"]
    assert "buy_slippage" in result["fees"]
    assert "sell_slippage" in result["fees"]
    assert "buy_mutable" in result["fees"]
    assert "sell_mutable" in result["fees"]
    
    # Verifica que não foi detectado como honeypot
    assert "honeypot" in result
    assert "is_honeypot" in result["honeypot"]
    assert result["honeypot"]["is_honeypot"] is False
    assert result["honeypot"]["buy_success"] is True
    assert result["honeypot"]["sell_success"] is True
    assert "high_tax" in result["honeypot"]
    assert "tax_discrepancy" in result["honeypot"]
