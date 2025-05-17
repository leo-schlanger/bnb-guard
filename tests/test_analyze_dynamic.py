import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

import pytest
from utils.analyze_dynamic import simulate_buy_sell
from web3.exceptions import ContractLogicError

# --- Mock de sucesso ---
class FakeGetAmountsOut:
    def call(self):
        return [1, 2]  # simula valores válidos

class FakeFunctions:
    def getAmountsOut(self, amount, path):
        return FakeGetAmountsOut()

class FakeRouterSuccess:
    functions = FakeFunctions()

def test_simulate_buy_sell_success(monkeypatch):
    monkeypatch.setattr("utils.analyze_dynamic.get_pancake_router", lambda: FakeRouterSuccess())
    result = simulate_buy_sell("0x000000000000000000000000000000000000dEaD")
    assert result == []


# --- Mock para ContractLogicError ---
class FakeGetAmountsError:
    def call(self):
        raise ContractLogicError("reverted")

class FakeFunctionsError:
    def getAmountsOut(self, amount, path):
        return FakeGetAmountsError()

class FakeRouterLogicError:
    functions = FakeFunctionsError()

def test_simulate_buy_sell_contract_logic_error(monkeypatch):
    monkeypatch.setattr("utils.analyze_dynamic.get_pancake_router", lambda: FakeRouterLogicError())
    result = simulate_buy_sell("0x000000000000000000000000000000000000dEaD")
    assert "possível honeypot" in result[0].lower()


# --- Mock para mensagem “execution reverted” fora de ContractLogicError ---
class FakeRouterExecReverted:
    def __init__(self):
        # getAmountsOut retorna um objeto cujo .call() devolve uma tupla
        class ExecCall:
            def call(self):
                raise Exception("execution reverted: no data")
        self.functions = type("F", (), {"getAmountsOut": lambda *args, **k: ExecCall()})

def test_simulate_buy_sell_exec_reverted(monkeypatch):
    monkeypatch.setattr("utils.analyze_dynamic.get_pancake_router", lambda: FakeRouterExecReverted())
    result = simulate_buy_sell("0x000000000000000000000000000000000000dEaD")
    assert "possível honeypot" in result[0].lower()


# --- Mock para erro genérico ---
class FailingCall:
    def call(self):
        raise RuntimeError("erro inesperado")

class FailingFunctions:
    def getAmountsOut(self, amount, path):
        return FailingCall()

class FakeRouterGenericFail:
    functions = FailingFunctions()

def test_simulate_buy_sell_generic_error(monkeypatch):
    monkeypatch.setattr("utils.analyze_dynamic.get_pancake_router", lambda: FakeRouterGenericFail())
    result = simulate_buy_sell("0x000000000000000000000000000000000000dEaD")
    assert "erro durante simulação" in result[0].lower()


class FailingCallEmpty:
    def call(self):
        return []  # retorno vazio para simular falha de swap

class EmptyResponseRouter:
    class Functions:
        def getAmountsOut(self, amount, path):
            return FailingCallEmpty()
    functions = Functions()

def test_simulate_buy_sell_returns_empty(monkeypatch):
    monkeypatch.setattr("utils.analyze_dynamic.get_pancake_router", lambda: EmptyResponseRouter())
    result = simulate_buy_sell("0x000000000000000000000000000000000000dEaD")
    assert "falha ao simular" in result[0].lower()
