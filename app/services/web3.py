from web3 import Web3
from app.core.config import settings

PANCAKE_ROUTER_ADDRESS = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
PANCAKE_ROUTER_ABI = [
    {
        "name": "getAmountsOut",
        "type": "function",
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "path", "type": "address[]"},
        ],
        "outputs": [{"name": "", "type": "uint256[]"}],
        "stateMutability": "view",
    }
]

def get_web3_instance():
    """Get a Web3 instance connected to BSC."""
    provider = Web3.HTTPProvider(settings.BSC_RPC_URL)
    web3 = Web3(provider)
    return web3

def get_pancake_router():
    """Get PancakeSwap router contract instance."""
    web3 = get_web3_instance()
    router = web3.eth.contract(
        address=Web3.to_checksum_address(PANCAKE_ROUTER_ADDRESS),
        abi=PANCAKE_ROUTER_ABI
    )
    return router
