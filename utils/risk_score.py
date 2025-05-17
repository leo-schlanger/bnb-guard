def calculate_risk(static_risks, dynamic_risks, onchain_risks):
    score = 100
    reasons = []

    # Riscos estáticos
    for alert in static_risks:
        if "mint" in alert or "setFee" in alert:
            score -= 15
            reasons.append(f"🔧 {alert}")
        elif "blacklist" in alert or "pause" in alert:
            score -= 10
            reasons.append(f"⚠️ {alert}")
        else:
            score -= 5
            reasons.append(f"🔍 {alert}")

    # Riscos dinâmicos
    for alert in dynamic_risks:
        if "honeypot" in alert.lower():
            score -= 30
            reasons.append(f"💣 {alert}")
        else:
            score -= 10
            reasons.append(f"📉 {alert}")

    # Riscos on-chain
    for alert in onchain_risks:
        if "concentração" in alert.lower():
            score -= 15
            reasons.append(f"🐳 {alert}")
        elif "lp desbloqueada" in alert.lower():
            score -= 20
            reasons.append(f"🧯 {alert}")
        else:
            score -= 5
            reasons.append(f"🔗 {alert}")

    # Limite inferior
    score = max(score, 0)

    return {
        "score": score,
        "alerts": reasons,
        "status": get_status(score)
    }


def get_status(score):
    if score >= 85:
        return "✅ Seguro"
    elif score >= 65:
        return "🟡 Moderado"
    elif score >= 40:
        return "🔶 Arriscado"
    else:
        return "🔴 Perigoso"
