def calculate_risk_score(static_risk: dict, dynamic_risk: dict, onchain_risk: dict) -> dict:
    score = 100
    alerts = []

    # ⚠️ Análise Estática
    if static_risk.get("has_mint"):
        score -= 20
        alerts.append("🚨 Função mint() detectada")
    if static_risk.get("has_set_fee"):
        score -= 15
        alerts.append("⚠️ Função para modificar taxas encontrada")
    if static_risk.get("has_blacklist"):
        score -= 15
        alerts.append("⚠️ Função de blacklist presente")
    if static_risk.get("has_only_owner"):
        score -= 10
        alerts.append("⚠️ Permissões centralizadas detectadas")
    if static_risk.get("has_pause"):
        score -= 10
        alerts.append("⚠️ Contrato pode ser pausado")

    # 📉 Análise Dinâmica
    if dynamic_risk.get("honeypot_detected"):
        score -= 30
        alerts.append("🚨 Possível honeypot: venda falha")
    if dynamic_risk.get("buy_tax") is not None and dynamic_risk["buy_tax"] > 10:
        score -= 10
        alerts.append(f"⚠️ Buy tax alta: {dynamic_risk['buy_tax']}%")

    if dynamic_risk.get("sell_tax") is not None and dynamic_risk["sell_tax"] > 10:
        score -= 10
        alerts.append(f"⚠️ Sell tax alta: {dynamic_risk['sell_tax']}%")


    # 🔗 Análise On-Chain
    if onchain_risk.get("deployer_flagged"):
        score -= 15
        alerts.append("⚠️ Deployer suspeito: criou muitos tokens")
    if onchain_risk.get("top_holder_concentration") is not None and onchain_risk["top_holder_concentration"] > 50:
        score -= 10
        alerts.append("⚠️ Concentração alta nos Top 5 holders")
    if not onchain_risk.get("lp_locked") or (onchain_risk.get("lp_percent_locked") or 0) < 70:
        score -= 20
        alerts.append("❌ LP não está devidamente travada")

    # Ajuste de limites
    score = max(score, 0)

    return {
        "risk_score": score,
        "alerts": alerts,
        "grade": (
            "🟥 Altíssimo Risco" if score <= 30 else
            "🟧 Risco Alto" if score <= 60 else
            "🟨 Risco Moderado" if score <= 80 else
            "🟩 Baixo Risco"
        )
    }