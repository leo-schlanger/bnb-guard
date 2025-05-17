from web3 import Web3

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

def get_pancake_router():
    provider = Web3.HTTPProvider("https://bsc-dataseed.binance.org/")
    web3 = Web3(provider)
    router = web3.eth.contract(
        address=Web3.to_checksum_address(PANCAKE_ROUTER_ADDRESS),
        abi=PANCAKE_ROUTER_ABI
    )
    return router
