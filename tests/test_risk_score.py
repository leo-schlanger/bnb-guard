from utils.risk_score import calculate_risk

def test_high_risk_token():
    static = ["⚠️ Função mint() detectada", "⚠️ blacklist presente"]
    dynamic = ["❌ Erro de lógica no contrato — possível honeypot"]
    onchain = ["🐳 Alta concentração entre top holders", "🧯 LP desbloqueada"]

    result = calculate_risk(static, dynamic, onchain)
    assert result["score"] <= 40
    assert result["status"] == "🔴 Perigoso"

def test_safe_token():
    static = []
    dynamic = []
    onchain = []

    result = calculate_risk(static, dynamic, onchain)
    assert result["score"] == 100
    assert result["status"] == "✅ Seguro"

from utils.risk_score import calculate_risk

def test_score_seguro():
    result = calculate_risk([], [], [])
    assert result["score"] == 100
    assert result["status"] == "✅ Seguro"

def test_score_moderado():
    static = ["⚠️ Função qualquer"] * 7  # 7 * -5 = -35
    result = calculate_risk(static, [], [])
    assert 65 <= result["score"] < 85
    assert result["status"] == "🟡 Moderado"

def test_score_arriscado():
    static = ["⚠️ Função mint() detectada"] * 4  # 4 * -15 = -60
    result = calculate_risk(static, [], [])
    assert 40 <= result["score"] < 65
    assert result["status"] == "🔶 Arriscado"

def test_score_perigoso():
    static = ["⚠️ blacklist presente"]
    dynamic = ["❌ honeypot"]
    onchain = ["🧯 LP desbloqueada",  "🐳 Concentração em poucos holders"]
    result = calculate_risk(static, dynamic, onchain)
    assert result["score"] < 40
    assert result["status"] == "🔴 Perigoso"

def test_score_nunca_negativo():
    static = ["mint"] * 10  # 150 de desconto
    result = calculate_risk(static, [], [])
    assert result["score"] == 0

def test_status_moderado():
    result = calculate_risk(["generic"] * 7, [], [])  # -35 → score 65
    assert result["status"] == "🟡 Moderado"

def test_status_arriscado():
    # 8 * -5 = -40 ⇒ score = 60 (faixa Arriscado)
    result = calculate_risk(["generic"] * 8, [], [])
    assert result["status"] == "🔶 Arriscado"

def test_alert_lp_unlock_affects_score():
    result = calculate_risk([], [], ["🧯 LP desbloqueada"])
    assert result["score"] < 100
