import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from utils.analyze_static import analyze_static_code

def test_detect_single_dangerous_function():
    source = "function mint(address to, uint256 amount) public onlyOwner {}"
    result = analyze_static_code(source)
    assert any("mint" in r for r in result)

def test_detect_multiple_functions():
    source = "function setFee(uint value) public onlyOwner {} function blacklist(address user) public {}"
    result = analyze_static_code(source)
    assert len(result) >= 2
    assert any("setFee" in r for r in result)
    assert any("blacklist" in r for r in result)

def test_safe_code_returns_empty():
    source = "function transfer(address to, uint amount) public returns (bool) {}"
    result = analyze_static_code(source)
    assert result == []
