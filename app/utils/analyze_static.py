import re

DANGEROUS_FUNCTIONS = [
    "mint", "setFee", "setFees", "excludeFromReward", "includeInReward",
    "setTaxFeePercent", "setBuyFee", "setSellFee", "setSellTax",
    "blacklist", "pause", "unpause", "transferOwnership", "renounceOwnership"
]

DANGEROUS_MODIFIERS = [
    "onlyOwner", "admin", "isOwner", "hasRole"
]

def analyze_static(source_code: str) -> dict:
    result = {
        "has_mint": False,
        "has_blacklist": False,
        "has_set_fee": False,
        "has_only_owner": False,
        "has_pause": False,
        "dangerous_functions_found": [],
        "dangerous_modifiers_found": [],
        "total_dangerous_matches": 0,
    }

    found_functions = []
    for func in DANGEROUS_FUNCTIONS:
        pattern = r"function\s+" + re.escape(func) + r"\b"
        if re.search(pattern, source_code):
            found_functions.append(func)
            result[f"has_{func.lower()}"] = True

    found_modifiers = []
    for modifier in DANGEROUS_MODIFIERS:
        if modifier in source_code:
            found_modifiers.append(modifier)

    result["dangerous_functions_found"] = found_functions
    result["dangerous_modifiers_found"] = found_modifiers
    result["has_only_owner"] = any(m in ["onlyOwner", "admin", "isOwner"] for m in found_modifiers)
    result["has_set_fee"] = any(f in ["setFee", "setFees", "setBuyFee", "setSellFee", "setSellTax"] for f in found_functions)
    result["has_blacklist"] = "blacklist" in found_functions
    result["has_pause"] = "pause" in found_functions
    result["has_mint"] = "mint" in found_functions
    result["total_dangerous_matches"] = len(found_functions) + len(found_modifiers)

    return result