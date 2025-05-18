import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.services.web3 import get_pancake_router

def test_get_pancake_router():
    router = get_pancake_router()
    assert hasattr(router, "functions")
