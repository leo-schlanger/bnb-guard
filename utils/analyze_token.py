import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from utils.fetch_metadata import fetch_token_metadata
from utils.analyze_static import analyze_static_code
from utils.analyze_dynamic import simulate_buy_sell
from utils.analyze_onchain import (
    get_deployer_address,
    get_holder_distribution,
    is_lp_locked
)
from utils.risk_score import calculate_risk

def analyze_token(token_address, lp_token_address=None):
    static_alerts = []
    dynamic_alerts = []
    onchain_alerts = []

    try:
        metadata = fetch_token_metadata(token_address)
        source = metadata.get("SourceCode", "")
        static_alerts = analyze_static_code(source)
    except Exception as e:
        static_alerts.append(f"❌ Falha na análise estática: {str(e)}")

    try:
        dynamic_alerts = simulate_buy_sell(token_address)
    except Exception as e:
        dynamic_alerts.append(f"❌ Falha na simulação: {str(e)}")

    try:
        deployer = get_deployer_address(token_address)
        onchain_alerts.append(f"🔍 Deploy feito por {deployer}")
    except Exception as e:
        onchain_alerts.append(f"❌ Falha ao buscar deployer: {str(e)}")

    try:
        holders = get_holder_distribution(token_address)
        if holders["top5_percentage"] > 80:
            onchain_alerts.append(f"🐳 Concentração de {holders['top5_percentage']}% nos top 5 holders")
    except Exception as e:
        onchain_alerts.append(f"❌ Falha na distribuição de holders: {str(e)}")

    if lp_token_address:
        try:
            locked = is_lp_locked(lp_token_address)
            if not locked:
                onchain_alerts.append("🧯 LP desbloqueada")
        except Exception as e:
            onchain_alerts.append(f"❌ Falha ao verificar LP: {str(e)}")

    final = calculate_risk(static_alerts, dynamic_alerts, onchain_alerts)

    return {
        "address": token_address,
        "score": final["score"],
        "status": final["status"],
        "alerts": final["alerts"]
    }
