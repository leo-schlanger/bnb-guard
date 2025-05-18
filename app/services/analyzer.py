from utils.fetch_metadata import fetch_token_metadata
from utils.analyze_static import analyze_static
from utils.analyze_dynamic import analyze_dynamic
from utils.analyze_onchain import analyze_onchain
from utils.risk_score import calculate_risk_score

def analyze_token(token_address, lp_token_address=None):
    try:
        # 📦 Fetch metadata
        metadata = fetch_token_metadata(token_address)
        source = metadata.get("SourceCode", "")

        # 🧠 Static Analysis
        static_alerts = analyze_static(source)

        # 🔁 Dynamic Analysis
        dynamic_alerts = analyze_dynamic(token_address)

        # 🔗 On-chain Analysis
        metadata["lp_info"] = {
            "locked": False,
            "percent_locked": None
        }
        if lp_token_address:
            metadata["lp_info"]["locked"] = True
            metadata["lp_info"]["percent_locked"] = 100

        onchain_alerts = analyze_onchain(metadata)

        # 🧮 Final Score
        final = calculate_risk_score(static_alerts, dynamic_alerts, onchain_alerts)

        return {
            "token_address": token_address,
            "name": metadata.get("name", "N/A"),
            "symbol": metadata.get("symbol", "N/A"),
            "supply": float(metadata.get("totalSupply", 0)),
            "score": {
                "value": final["risk_score"],
                "label": final["grade"]
            },
            "honeypot": {
                "is_honeypot": not dynamic_alerts.get("honeypot", {}).get("sell_success", True)
            },
            "fees": {
                "buy": dynamic_alerts.get("fees", {}).get("buy", 0),
                "sell": dynamic_alerts.get("fees", {}).get("sell", 0)
            },
            "lp_lock": {
                "locked": metadata["lp_info"]["locked"]
            },
            "owner": {
                "renounced": static_alerts.get("owner", {}).get("renounced", False)
            },
            "top_holders": onchain_alerts.get("top_holders", {}).get("holders", []),
            "risks": final.get("alerts", [])
        }

    except Exception as e:
        return {
            "token_address": token_address,
            "name": "Error",
            "symbol": "ERR",
            "supply": 0,
            "score": {
                "value": 0,
                "label": "Error"
            },
            "honeypot": {"is_honeypot": False},
            "fees": {"buy": 0, "sell": 0},
            "lp_lock": {"locked": False},
            "owner": {"renounced": False},
            "top_holders": [],
            "risks": [f"❌ Error processing token: {str(e)}"]
        }