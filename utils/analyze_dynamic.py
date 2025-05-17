def analyze_dynamic(simulation_result: dict) -> dict:
    result = {
        "buy_success": False,
        "sell_success": False,
        "buy_tax": None,
        "sell_tax": None,
        "buy_slippage": None,
        "sell_slippage": None,
        "honeypot_detected": False,
        "error": None
    }

    try:
        # Verifica se a simulação de compra foi bem-sucedida
        result["buy_success"] = simulation_result.get("buy", {}).get("success", False)
        result["sell_success"] = simulation_result.get("sell", {}).get("success", False)

        # Honeypot = compra funciona, venda falha
        result["honeypot_detected"] = result["buy_success"] and not result["sell_success"]

        # Taxas e slippage reais
        if result["buy_success"]:
            expected_in = simulation_result["buy"].get("expected_amount_out")
            received_in = simulation_result["buy"].get("amount_out")
            if expected_in and received_in:
                result["buy_tax"] = round(100 * (1 - (received_in / expected_in)), 2)
                result["buy_slippage"] = round(100 * abs(received_in - expected_in) / expected_in, 2)

        if result["sell_success"]:
            expected_out = simulation_result["sell"].get("expected_amount_out")
            received_out = simulation_result["sell"].get("amount_out")
            if expected_out and received_out:
                result["sell_tax"] = round(100 * (1 - (received_out / expected_out)), 2)
                result["sell_slippage"] = round(100 * abs(received_out - expected_out) / expected_out, 2)

    except Exception as e:
        result["error"] = str(e)

    return result