from app.core.utils.metadata import fetch_token_metadata
from app.core.analyzers.static_analyzer import analyze_static
from app.core.analyzers.dynamic_analyzer import analyze_dynamic
from app.core.analyzers.onchain_analyzer import analyze_onchain
from app.core.utils.scoring import calculate_risk_score
from app.core.interfaces.analyzer import AnalysisResult

def analyze_token(token_address, lp_token_address=None):
    try:
        # 📦 Fetch metadata
        metadata = fetch_token_metadata(token_address)
        source = metadata.get("SourceCode", "")

        # 🧠 Static Analysis
        static_alerts = analyze_static(source)

        # 🔁 Dynamic Analysis
        dynamic_alerts = analyze_dynamic(source)

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
                "is_honeypot": dynamic_alerts.get("honeypot", {}).get("is_honeypot", False),
                "buy_success": dynamic_alerts.get("honeypot", {}).get("buy_success", False),
                "sell_success": dynamic_alerts.get("honeypot", {}).get("sell_success", False),
                "high_tax": dynamic_alerts.get("honeypot", {}).get("high_tax", False),
                "tax_discrepancy": dynamic_alerts.get("honeypot", {}).get("tax_discrepancy", False),
                "error": dynamic_alerts.get("honeypot", {}).get("error", "")
            },
            "fees": {
                "buy": dynamic_alerts.get("fees", {}).get("buy", 0.0),
                "sell": dynamic_alerts.get("fees", {}).get("sell", 0.0),
                "buy_slippage": dynamic_alerts.get("fees", {}).get("buy_slippage", 0.0),
                "sell_slippage": dynamic_alerts.get("fees", {}).get("sell_slippage", 0.0),
                "buy_mutable": dynamic_alerts.get("fees", {}).get("buy_mutable", False),
                "sell_mutable": dynamic_alerts.get("fees", {}).get("sell_mutable", False)
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