# from utils.analyze_token import analyze_token

# if __name__ == "__main__":
#     token = input("🔍 Digite o endereço do contrato: ").strip()
#     lp = input("💧 Endereço do token LP (opcional): ").strip() or None

#     result = analyze_token(token, lp_token_address=lp)

#     print("\n✅ Resultado da análise:")
#     print(f"🔎 Endereço: {result['address']}")
#     print(f"🎯 Score: {result['score']} — {result['status']}")
#     print("\n📋 Alertas:")
#     for alert in result["alerts"]:
#         print(f" - {alert}")


import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
