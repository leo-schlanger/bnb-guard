from utils.fetch_metadata import fetch_token_metadata
from utils.analyze_static import analyze_static
from utils.analyze_dynamic import analyze_dynamic
from utils.analyze_onchain import analyze_onchain
from utils.risk_score import calculate_risk_score

def audit_token(token_address, lp_token_address=None):
    try:
        # 📦 Coleta metadados
        metadata = fetch_token_metadata(token_address)
        source = metadata.get("SourceCode", "")

        # 🧠 Análise Estática
        static_alerts = analyze_static(source)

        # 🔁 Análise Dinâmica
        dynamic_alerts = analyze_dynamic(token_address)

        # 🔗 Análise On-chain
        metadata["lp_info"] = {
            "locked": False,
            "percent_locked": 0.0,
            "unlock_date": None
        }
        if lp_token_address:
            metadata["lp_info"]["locked"] = True
            metadata["lp_info"]["percent_locked"] = 100

        onchain_alerts = analyze_onchain(metadata)

        # 🧮 Score final
        final = calculate_risk_score(static_alerts, dynamic_alerts, onchain_alerts)

        # ✅ Resposta detalhada para rota /audit
        return {
            "token_address": token_address,
            "name": metadata.get("name", "N/A"),
            "symbol": metadata.get("symbol", "N/A"),
            "supply": str(metadata.get("totalSupply", 0)),
            "score": {
                "value": final["risk_score"],
                "details": final.get("alerts", [])
            },
            "honeypot": {
                "buy_success": dynamic_alerts.get("honeypot", {}).get("buy_success", False),
                "sell_success": dynamic_alerts.get("honeypot", {}).get("sell_success", False),
                "slippage": dynamic_alerts.get("honeypot", {}).get("slippage", 0.0),
                "error_message": dynamic_alerts.get("honeypot", {}).get("error_message", "")
            },
            "fees": {
                "buy": dynamic_alerts.get("fees", {}).get("buy", 0.0),
                "sell": dynamic_alerts.get("fees", {}).get("sell", 0.0),
                "buy_mutable": dynamic_alerts.get("fees", {}).get("buy_mutable", False),
                "sell_mutable": dynamic_alerts.get("fees", {}).get("sell_mutable", False)
            },
            "lp_lock": {
                "locked": metadata.get("lp_info", {}).get("locked", False),
                "locked_percentage": metadata.get("lp_info", {}).get("percent_locked", 0.0),
                "unlock_date": metadata.get("lp_info", {}).get("unlock_date", None)
            },
            "owner": {
                "renounced": static_alerts.get("owner", {}).get("renounced", False),
                "functions": static_alerts.get("owner", {}).get("functions", [])
            },
            "critical_functions": static_alerts.get("functions", []),
            "top_holders": {
                "top_1_percent": onchain_alerts.get("top_holders", {}).get("top_1_percent", 0.0),
                "top_10_percent": onchain_alerts.get("top_holders", {}).get("top_10_percent", 0.0),
                "top_50_percent": onchain_alerts.get("top_holders", {}).get("top_50_percent", 0.0),
                "holders": onchain_alerts.get("top_holders", {}).get("holders", [])
            },
            "deployer": {
                "address": onchain_alerts.get("deployer", {}).get("address", ""),
                "token_history": onchain_alerts.get("deployer", {}).get("token_history", [])
            },
            "risks": final.get("risks", [])
        }

    except Exception as e:
        return {
            "token_address": token_address,
            "name": "Erro",
            "symbol": "ERR",
            "supply": "0",
            "score": {
                "value": 0,
                "details": [f"❌ Erro ao processar token: {str(e)}"]
            },
            "honeypot": {
                "buy_success": False,
                "sell_success": False,
                "slippage": 0.0,
                "error_message": str(e)
            },
            "fees": {
                "buy": 0.0,
                "sell": 0.0,
                "buy_mutable": False,
                "sell_mutable": False
            },
            "lp_lock": {
                "locked": False,
                "locked_percentage": 0.0,
                "unlock_date": None
            },
            "owner": {
                "renounced": False,
                "functions": []
            },
            "critical_functions": [],
            "top_holders": {
                "top_1_percent": 0.0,
                "top_10_percent": 0.0,
                "top_50_percent": 0.0,
                "holders": []
            },
            "deployer": {
                "address": "",
                "token_history": []
            },
            "risks": []
        }
