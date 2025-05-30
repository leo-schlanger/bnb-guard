import re
from typing import Dict, Any
from app.core.utils.logger import get_logger

logger = get_logger(__name__)

DANGEROUS_FUNCTIONS = [
    "mint", "setFee", "setFees", "excludeFromReward", "includeInReward",
    "setTaxFeePercent", "setBuyFee", "setSellFee", "setSellTax",
    "blacklist", "pause", "unpause", "transferOwnership", "renounceOwnership"
]

DANGEROUS_MODIFIERS = [
    "onlyOwner", "admin", "isOwner", "hasRole"
]

def create_alert(title: str, description: str, severity: str) -> Dict[str, Any]:
    """Create an alert dictionary."""
    return {
        "title": title,
        "description": description,
        "severity": severity,
        "type": "security_alert"
    }

def analyze_static(source_code: str) -> Dict[str, Any]:
    logger.info("Starting static analysis of contract")
    logger.debug(f"Source code length: {len(source_code)} characters")

    if not source_code:
        logger.error("No source code provided for static analysis")
        return {
            "static": [{
                "type": "source_code",
                "message": "Source code not verified",
                "severity": "high"
            }]
        }

    result = {
        "has_mint": False,
        "has_blacklist": False,
        "has_set_fee": False,
        "has_only_owner": False,
        "has_pause": False,
        "dangerous_functions_found": [],
        "dangerous_modifiers_found": [],
        "total_dangerous_matches": 0,
        "functions": [],
        "owner": {
            "renounced": False
        }
    }

    # Ownership Renouncement
    try:
        logger.debug("Checking for ownership renouncement...")
        if re.search(r'function\s+renounceOwnership\s*\(', source_code):
            result["owner"]["renounced"] = True
            logger.info("Ownership renouncement function found")
    except Exception as e:
        logger.error("Error during renounceOwnership check", exc_info=True)

    # Dangerous Functions
    try:
        logger.debug("Checking for dangerous functions...")
        for func in DANGEROUS_FUNCTIONS:
            if re.search(fr'function\s+{func}\s*\(', source_code, re.IGNORECASE):
                # Classify severity based on function
                if func == "mint":
                    severity = "high"
                    result["has_mint"] = True
                elif func in ["blacklist", "pause", "unpause"]:
                    severity = "high" if func == "blacklist" else "medium"
                    if func == "blacklist":
                        result["has_blacklist"] = True
                    elif "pause" in func.lower():
                        result["has_pause"] = True
                elif "fee" in func.lower() or "tax" in func.lower():
                    severity = "medium"
                    result["has_set_fee"] = True
                elif func in ["transferOwnership", "renounceOwnership"]:
                    severity = "medium"
                else:
                    severity = "medium"
                
                # Adicionar como objeto com severidade
                result["dangerous_functions_found"].append({
                    "name": func,
                    "type": "dangerous_function",
                    "severity": severity,
                    "message": f"Dangerous function '{func}' found in contract"
                })
                result["total_dangerous_matches"] += 1
                logger.debug(f"Found dangerous function: {func} (severity: {severity})")
                
    except Exception as e:
        logger.error("Error during dangerous function check", exc_info=True)

    # Dangerous Modifiers
    try:
        logger.debug("Checking for dangerous modifiers...")
        for modifier in DANGEROUS_MODIFIERS:
            if re.search(fr'modifier\s+{modifier}', source_code, re.IGNORECASE) or \
               re.search(fr'\b{modifier}\s*\(', source_code, re.IGNORECASE):
                result["dangerous_modifiers_found"].append(modifier)
                result["total_dangerous_matches"] += 1
                logger.debug(f"Found dangerous modifier: {modifier}")

                if "owner" in modifier.lower():
                    result["has_only_owner"] = True
    except Exception as e:
        logger.error("Error during dangerous modifier check", exc_info=True)

    # Alert Generation
    try:
        logger.debug("Generating alerts...")
        for func in result["dangerous_functions_found"]:
            result["functions"].append(create_alert(
                title=f"Dangerous Function: {func['name']}",
                description=f"The contract contains a potentially dangerous function: {func['name']}",
                severity=func['severity']
            ))

        for mod in result["dangerous_modifiers_found"]:
            result["functions"].append(create_alert(
                title=f"Dangerous Modifier: {mod}",
                description=f"The contract uses a potentially dangerous modifier: {mod}",
                severity="medium"
            ))
    except Exception as e:
        logger.error("Error during alert generation", exc_info=True)

    # Final logging
    try:
        logger.info(
            "Static analysis completed",
            context={
                "dangerous_functions": len(result["dangerous_functions_found"]),
                "dangerous_modifiers": len(result["dangerous_modifiers_found"]),
                "owner_renounced": result["owner"]["renounced"]
            }
        )

        if result["total_dangerous_matches"] > 0:
            logger.warning(
                f"Found {result['total_dangerous_matches']} potential issues",
                context={"total_issues": result["total_dangerous_matches"]}
            )
    except Exception as e:
        logger.warning("Error during final logging", exc_info=True)

    return result
