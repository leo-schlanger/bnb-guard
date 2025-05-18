def calculate_risk_score(static_alerts, dynamic_alerts, onchain_alerts):
    score = 100
    alerts = []
    risks = []

    # 🎯 Critical Functions
    dangerous_functions = static_alerts.get("functions", [])
    if dangerous_functions:
        score -= 20
        alerts.append("🚨 Critical functions detected")
        risks.append({
            "type": "owner",
            "description": f"Critical functions found: {', '.join(f['name'] for f in dangerous_functions)}",
            "severity": "high"
        })

    # 👑 Owner
    owner_info = static_alerts.get("owner", {})
    if not owner_info.get("renounced", False):
        score -= 10
        alerts.append("⚠️ Ownership not renounced")
        risks.append({
            "type": "owner",
            "description": "Contract still under owner control",
            "severity": "high"
        })

    # 💸 Fees
    fees = dynamic_alerts.get("fees", {})
    if fees.get("buy_mutable") or fees.get("sell_mutable"):
        score -= 10
        alerts.append("⚠️ Mutable fees")
        risks.append({
            "type": "fees",
            "description": "Fees can be changed via setFee functions",
            "severity": "medium"
        })

    if fees.get("buy", 0) > 10 or fees.get("sell", 0) > 10:
        score -= 5
        alerts.append("⚠️ Fees above 10%")
        risks.append({
            "type": "fees",
            "description": f"Buy/Sell fees above 10%: buy={fees.get('buy')}%, sell={fees.get('sell')}%",
            "severity": "medium"
        })

    # 🪙 Honeypot
    honeypot = dynamic_alerts.get("honeypot", {})
    if honeypot.get("buy_success") and not honeypot.get("sell_success"):
        score -= 40
        alerts.append("🧸 Possible honeypot (sell fails)")
        risks.append({
            "type": "honeypot",
            "description": f"Sell failed: {honeypot.get('error_message', 'unknown error')}",
            "severity": "high"
        })

    # 🔒 LP
    lp = onchain_alerts.get("lp_info", {})
    if not lp.get("locked", False):
        score -= 10
        alerts.append("🔓 LP not locked")
        risks.append({
            "type": "lp",
            "description": "Liquidity contract is not locked",
            "severity": "medium"
        })

    # 🧠 Deploy History
    deployer = onchain_alerts.get("deployer", {})
    tokens = deployer.get("token_history", [])
    if len(tokens) >= 3:
        score -= 10
        alerts.append("❗ Creator has launched multiple tokens")
        risks.append({
            "type": "deployer",
            "description": f"Deployer has created {len(tokens)} previous tokens",
            "severity": "medium"
        })

    # 🧮 Final Adjustment
    score = max(0, min(score, 100))
    grade = (
            "🔴 Extreme Risk" if score <= 30 else
            "🟠 High Risk" if score <= 60 else
            "🟡 Moderate Risk" if score <= 80 else
            "🟢 Low Risk"
        )

    return {
        "risk_score": score,
        "grade": grade,
        "alerts": alerts,
        "risks": risks
    }
