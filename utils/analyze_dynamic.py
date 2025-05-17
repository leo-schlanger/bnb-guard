from services.web3 import get_pancake_router
from web3 import Web3
from web3.exceptions import ContractLogicError

WBNB_ADDRESS = Web3.to_checksum_address("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")

def simulate_buy_sell(token_address):
    router = get_pancake_router()
    token = Web3.to_checksum_address(token_address)

    try:
        amount_in_wei = Web3.to_wei(1, 'ether')
        buy_path = [WBNB_ADDRESS, token]
        sell_path = [token, WBNB_ADDRESS]

        buy_out = router.functions.getAmountsOut(amount_in_wei, buy_path).call()
        sell_out = router.functions.getAmountsOut(amount_in_wei, sell_path).call()

        if not buy_out or not sell_out:
            return ["⚠️ Falha ao simular compra ou venda"]

        return []
    except ContractLogicError:
        # Erro de lógica no contrato indica possível honeypot
        return ["❌ Erro de lógica no contrato — possível honeypot"]
    except Exception as e:
        msg = str(e).lower()
        # Se for “execution reverted”, também é honeypot
        if 'execution reverted' in msg:
            return ["❌ Erro de lógica no contrato — possível honeypot"]
        return [f"❌ Erro durante simulação: {e}"]
