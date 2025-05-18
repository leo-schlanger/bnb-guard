import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.utils.analyze_static import analyze_static

def test_detect_single_dangerous_function():
    source = "function mint(address to, uint256 amount) public onlyOwner {}"
    result = analyze_static(source)
    functions = result.get("dangerous_functions_found", [])
    assert any("mint" in f.lower() for f in functions)

def test_detect_multiple_functions():
    source = "function setFee(uint value) public onlyOwner {} function blacklist(address user) public {}"
    result = analyze_static(source)
    functions = result.get("dangerous_functions_found", [])
    assert any("setfee" in f.lower() for f in functions)
    assert any("blacklist" in f.lower() for f in functions)
    assert len(functions) >= 2

def test_safe_code_returns_empty():
    source = "function transfer(address to, uint amount) public returns (bool) {}"
    result = analyze_static(source)
    assert isinstance(result, dict)
    assert result.get("dangerous_functions_found") == []
    assert result.get("has_mint") is False
    assert result.get("has_blacklist") is False
