import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from utils.fetch_metadata import fetch_token_metadata
from utils.analyze_static import analyze_static
from utils.analyze_dynamic import analyze_dynamic
from utils.analyze_onchain import analyze_onchain
from utils.risk_score import calculate_risk_score

def analyze_token(token_address, lp_token_address=None):
    try:
        # 📦 Coleta metadados
        metadata = fetch_token_metadata(token_address)
        source = metadata.get("SourceCode", "")

        # 🧠 Análise Estática
        static_alerts = analyze_static(source)

        # 🔁 Análise Dinâmica (simulação de compra/venda)
        dynamic_alerts = analyze_dynamic(token_address)

        # 🔗 Análise On-chain
        metadata["lp_info"] = {
            "locked": False,
            "percent_locked": None
        }

        if lp_token_address:
            # Se houver endereço de LP, marcar como travado (ajuste se tiver lógica real)
            metadata["lp_info"]["locked"] = True
            metadata["lp_info"]["percent_locked"] = 100

        onchain_alerts = analyze_onchain(metadata)

        # 🧮 Cálculo final
        final = calculate_risk_score(static_alerts, dynamic_alerts, onchain_alerts)

        return {
            "address": token_address,
            "score": final["risk_score"],
            "status": final["grade"],
            "alerts": final["alerts"]
        }

    except Exception as e:
        return {
            "address": token_address,
            "score": 0,
            "status": "Erro",
            "alerts": [f"❌ Erro ao processar token: {str(e)}"]
        }
