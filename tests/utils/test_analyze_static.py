import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from app.utils.analyze_static import analyze_static


def test_detect_single_dangerous_function():
    source = "function mint(address to, uint256 amount) public onlyOwner {}"
    result = analyze_static(source)
    assert any("mint" in r.get("name", "") and r.get("dangerous") for r in result)


def test_detect_multiple_functions():
    source = "function setFee(uint value) public onlyOwner {} function blacklist(address user) public {}"
    result = analyze_static(source)
    names = [r.get("name", "") for r in result if r.get("dangerous")]

    assert "setFee" in names
    assert "blacklist" in names
    assert len(names) >= 2


def test_safe_code_returns_empty():
    source = "function transfer(address to, uint amount) public returns (bool) {}"
    result = analyze_static(source)
    dangerous = [r for r in result if r.get("dangerous")]
    assert dangerous == []
