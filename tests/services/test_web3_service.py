import pytest
from unittest.mock import patch, MagicMock
from app.services.web3 import get_pancake_router

def test_get_pancake_router():
    router = get_pancake_router()
    assert hasattr(router, "functions")
