import pytest
from app.utils.analyze_dynamic import analyze_dynamic

# ✅ Compra e venda com sucesso, taxas e slippage calculadas
def test_analyze_dynamic_full_success():
    data = {
        "buy": {
            "success": True,
            "expected_amount_out": 100,
            "amount_out": 95
        },
        "sell": {
            "success": True,
            "expected_amount_out": 100,
            "amount_out": 90
        }
    }
    result = analyze_dynamic(data)
    assert result["buy_success"] is True
    assert result["sell_success"] is True
    assert result["honeypot_detected"] is False
    assert result["buy_tax"] == 5.0
    assert result["sell_tax"] == 10.0
    assert result["buy_slippage"] == 5.0
    assert result["sell_slippage"] == 10.0
    assert result["error"] is None

# ⚠️ Compra ok, venda falha (honeypot)
def test_analyze_dynamic_buy_only():
    data = {
        "buy": {
            "success": True,
            "expected_amount_out": 200,
            "amount_out": 180
        },
        "sell": {
            "success": False
        }
    }
    result = analyze_dynamic(data)
    assert result["buy_success"] is True
    assert result["sell_success"] is False
    assert result["honeypot_detected"] is True
    assert result["buy_tax"] == 10.0
    assert result["sell_tax"] is None

# ⚠️ Venda ok, compra falha (situação atípica)
def test_analyze_dynamic_sell_only():
    data = {
        "buy": {
            "success": False
        },
        "sell": {
            "success": True,
            "expected_amount_out": 1000,
            "amount_out": 950
        }
    }
    result = analyze_dynamic(data)
    assert result["buy_success"] is False
    assert result["sell_success"] is True
    assert result["honeypot_detected"] is False
    assert result["sell_tax"] == 5.0
    assert result["buy_tax"] is None

# ⚠️ Nenhuma transação funcionou
def test_analyze_dynamic_both_fail():
    result = analyze_dynamic({
        "buy": {"success": False},
        "sell": {"success": False}
    })
    assert result["buy_success"] is False
    assert result["sell_success"] is False
    assert result["honeypot_detected"] is False
    assert result["buy_tax"] is None
    assert result["sell_tax"] is None

# ⚠️ Valores ausentes (esperado ou recebido)
def test_analyze_dynamic_missing_values():
    data = {
        "buy": {"success": True, "expected_amount_out": None, "amount_out": 90},
        "sell": {"success": True, "expected_amount_out": 100, "amount_out": None}
    }
    result = analyze_dynamic(data)
    assert result["buy_tax"] is None
    assert result["sell_tax"] is None

# ❌ Erro inesperado (simula KeyError interno)
def test_analyze_dynamic_with_exception():
    result = analyze_dynamic("string que quebra")  # deveria ser dict
    assert result["error"] is not None
    assert isinstance(result["error"], str)
