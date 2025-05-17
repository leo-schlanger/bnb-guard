import requests
from config import BSCSCAN_API_KEY

def fetch_token_metadata(token_address):
    url = (
        f"https://api.bscscan.com/api"
        f"?module=contract"
        f"&action=getsourcecode"
        f"&address={token_address}"
        f"&apikey={BSCSCAN_API_KEY}"
    )
    response = requests.get(url)

    if not response.ok:
        raise Exception("❌ Erro na chamada BscScan")

    result = response.json().get("result", [])
    if not result or not isinstance(result[0], dict):
        raise Exception("❌ Nenhum dado retornado")

    return result[0]
