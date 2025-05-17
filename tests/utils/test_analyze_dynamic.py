import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

import pytest
from app.utils.analyze_dynamic import analyze_dynamic
from web3.exceptions import ContractLogicError

# --- Mock de sucesso ---
class FakeGetAmountsOut:
    def call(self):
        return [1, 2]

class FakeFunctions:
    def getAmountsOut(self, amount, path):
        return FakeGetAmountsOut()

class FakeRouterSuccess:
    functions = FakeFunctions()

def test_analyze_dynamic_success(monkeypatch):
    monkeypatch.setattr("app.utils.analyze_dynamic.get_pancake_router", lambda: FakeRouterSuccess())
    result = analyze_dynamic("0x000000000000000000000000000000000000dEaD")
    assert isinstance(result, list)
    assert result == []


# --- ContractLogicError ---
class FakeGetAmountsError:
    def call(self):
        raise ContractLogicError("reverted")

class FakeFunctionsError:
    def getAmountsOut(self, amount, path):
        return FakeGetAmountsError()

class FakeRouterLogicError:
    functions = FakeFunctionsError()

def test_analyze_dynamic_contract_logic_error(monkeypatch):
    monkeypatch.setattr("app.utils.analyze_dynamic.get_pancake_router", lambda: FakeRouterLogicError())
    result = analyze_dynamic("0x000000000000000000000000000000000000dEaD")
    assert any("possível honeypot" in r.lower() for r in result)


# --- Exception com “execution reverted” ---
class FakeRouterExecReverted:
    def __init__(self):
        class ExecCall:
            def call(self):
                raise Exception("execution reverted: no data")
        self.functions = type("F", (), {"getAmountsOut": lambda *args, **kwargs: ExecCall()})

def test_analyze_dynamic_exec_reverted(monkeypatch):
    monkeypatch.setattr("app.utils.analyze_dynamic.get_pancake_router", lambda: FakeRouterExecReverted())
    result = analyze_dynamic("0x000000000000000000000000000000000000dEaD")
    assert any("possível honeypot" in r.lower() for r in result)


# --- Erro genérico ---
class FailingCall:
    def call(self):
        raise RuntimeError("erro inesperado")

class FailingFunctions:
    def getAmountsOut(self, amount, path):
        return FailingCall()

class FakeRouterGenericFail:
    functions = FailingFunctions()

def test_analyze_dynamic_generic_error(monkeypatch):
    monkeypatch.setattr("app.utils.analyze_dynamic.get_pancake_router", lambda: FakeRouterGenericFail())
    result = analyze_dynamic("0x000000000000000000000000000000000000dEaD")
    assert any("erro durante simulação" in r.lower() for r in result)


# --- Retorno vazio ---
class FailingCallEmpty:
    def call(self):
        return []

class EmptyResponseRouter:
    class Functions:
        def getAmountsOut(self, amount, path):
            return FailingCallEmpty()
    functions = Functions()

def test_analyze_dynamic_returns_empty(monkeypatch):
    monkeypatch.setattr("app.utils.analyze_dynamic.get_pancake_router", lambda: EmptyResponseRouter())
    result = analyze_dynamic("0x000000000000000000000000000000000000dEaD")
    assert any("falha ao simular" in r.lower() for r in result)
