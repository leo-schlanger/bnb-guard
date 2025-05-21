import pytest
from app.core.analyzers.static_analyzer import analyze_static

def test_detect_single_dangerous_function():
    source = "function mint(address to, uint256 amount) public onlyOwner {}"
    result = analyze_static(source)
    functions = [f["name"] for f in result.get("functions", [])]
    assert "mint" in functions
    # Verifica se há um alerta de funções perigosas
    assert any(alert["type"] == "dangerous_functions" for alert in result.get("static", []))

def test_detect_multiple_functions():
    source = "function setFee(uint value) public onlyOwner {} function blacklist(address user) public {}"
    result = analyze_static(source)
    functions = [f["name"] for f in result.get("functions", [])]
    assert "setFee" in functions
    assert "blacklist" in functions
    assert len(functions) == 2
    # Verifica se há um alerta de funções perigosas
    assert any(alert["type"] == "dangerous_functions" for alert in result.get("static", []))

def test_safe_code_returns_empty():
    source = "function transfer(address to, uint amount) public returns (bool) {}"
    result = analyze_static(source)
    assert isinstance(result, dict)
    assert result.get("functions") == []
    assert result.get("static") == []
    assert result.get("owner", {}).get("renounced") is True

def test_empty_source_code():
    result = analyze_static("")
    assert isinstance(result, dict)
    assert "static" in result
    assert result["static"][0]["type"] == "source_code"
    assert result["static"][0]["severity"] == "high"

def test_dangerous_modifiers():
    source = """
    contract Test {
        address public owner;
        modifier onlyOwner() { _; }
        
        function setOwner(address _owner) public onlyOwner {
            owner = _owner;
        }
    }
    """
    result = analyze_static(source)
    # Verifica se há um alerta de funções perigosas
    assert any(alert["type"] == "dangerous_functions" for alert in result.get("static", []))
    # O owner não deve estar renunciado quando há um modificador onlyOwner
    assert result.get("owner", {}).get("renounced") is False

def test_multiple_dangerous_functions():
    source = """
    contract Test {
        function mint(address to, uint amount) public {}
        function setFee(uint fee) public {}
        function pause() public {}
    }
    """
    result = analyze_static(source)
    functions = [f["name"] for f in result.get("functions", [])]
    assert "mint" in functions
    assert "setFee" in functions
    assert "pause" in functions
    assert any(alert["type"] == "dangerous_functions" for alert in result.get("static", []))
