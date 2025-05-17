def calculate_risk_score(static_alerts, dynamic_alerts, onchain_alerts):
    score = 100
    alerts = []
    risks = []

    # 🎯 Funções críticas
    dangerous_functions = static_alerts.get("functions", [])
    if dangerous_functions:
        score -= 20
        alerts.append("🚨 Funções críticas detectadas")
        risks.append({
            "type": "owner",
            "description": f"Funções críticas encontradas: {', '.join(f['name'] for f in dangerous_functions)}",
            "severity": "alta"
        })

    # 👑 Owner
    owner_info = static_alerts.get("owner", {})
    if not owner_info.get("renounced", False):
        score -= 10
        alerts.append("⚠️ Propriedade não renunciada")
        risks.append({
            "type": "owner",
            "description": "Contrato ainda sob controle de um owner",
            "severity": "alta"
        })

    # 💸 Taxas
    fees = dynamic_alerts.get("fees", {})
    if fees.get("buy_mutable") or fees.get("sell_mutable"):
        score -= 10
        alerts.append("⚠️ Taxas mutáveis")
        risks.append({
            "type": "fees",
            "description": "Taxas podem ser alteradas via funções setFee",
            "severity": "média"
        })

    if fees.get("buy", 0) > 10 or fees.get("sell", 0) > 10:
        score -= 5
        alerts.append("⚠️ Taxas acima de 10%")
        risks.append({
            "type": "fees",
            "description": f"Taxa de compra/venda acima de 10%: buy={fees.get('buy')}%, sell={fees.get('sell')}%",
            "severity": "média"
        })

    # 🪙 Honeypot
    honeypot = dynamic_alerts.get("honeypot", {})
    if honeypot.get("buy_success") and not honeypot.get("sell_success"):
        score -= 40
        alerts.append("🧸 Possível honeypot (venda falha)")
        risks.append({
            "type": "honeypot",
            "description": f"Venda falhou: {honeypot.get('error_message', 'erro desconhecido')}",
            "severity": "alta"
        })

    # 🔒 LP
    lp = onchain_alerts.get("lp_info", {})
    if not lp.get("locked", False):
        score -= 10
        alerts.append("🔓 LP não está travada")
        risks.append({
            "type": "lp",
            "description": "Contrato de liquidez não possui travamento",
            "severity": "média"
        })

    # 🧠 Deploy histórico
    deployer = onchain_alerts.get("deployer", {})
    tokens = deployer.get("token_history", [])
    if len(tokens) >= 3:
        score -= 10
        alerts.append("❗ Criador já lançou múltiplos tokens")
        risks.append({
            "type": "deployer",
            "description": f"O deployer criou {len(tokens)} tokens anteriores",
            "severity": "média"
        })

    # 🧮 Ajuste final
    score = max(0, min(score, 100))
    grade = (
            "🟥 Altíssimo Risco" if score <= 30 else
            "🟧 Risco Alto" if score <= 60 else
            "🟨 Risco Moderado" if score <= 80 else
            "🟩 Baixo Risco"
        )

    return {
        "risk_score": score,
        "grade": grade,
        "alerts": alerts,
        "risks": risks
    }
