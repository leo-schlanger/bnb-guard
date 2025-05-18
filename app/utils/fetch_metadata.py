import requests
from web3 import Web3
from config import BSCSCAN_API_KEY, BSC_RPC_URL
from decimal import Decimal

def fetch_token_metadata(token_address):
    # 1. BscScan source code
    url = (
        f"https://api.bscscan.com/api"
        f"?module=contract"
        f"&action=getsourcecode"
        f"&address={token_address}"
        f"&apikey={BSCSCAN_API_KEY}"
    )
    response = requests.get(url)

    if not response.ok:
        raise Exception("❌ BscScan call failed")

    result = response.json().get("result", [])
    if not result or not isinstance(result[0], dict):
        raise Exception("❌ No data returned")

    metadata = result[0]

    # 2. Connect via Web3 to BNB Chain
    w3 = Web3(Web3.HTTPProvider(BSC_RPC_URL))
    abi = metadata.get("ABI", "[]")

    if abi == "Contract source code not verified":
        metadata["name"] = "N/A"
        metadata["symbol"] = "N/A"
        metadata["totalSupply"] = 0
        return metadata

    try:
        contract = w3.eth.contract(address=w3.to_checksum_address(token_address), abi=abi)
        metadata["name"] = contract.functions.name().call()
        metadata["symbol"] = contract.functions.symbol().call()        
        raw_supply = contract.functions.totalSupply().call()
        metadata["totalSupply"] = str(Decimal(raw_supply))
    except Exception as e:
        metadata["name"] = "N/A"
        metadata["symbol"] = "N/A"
        metadata["totalSupply"] = 0

    return metadata
