import re
import traceback
from typing import List, Dict, Optional, Any
from app.core.interfaces.analyzer import Alert
from app.core.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

DANGEROUS_FUNCTIONS = [
    "mint", "setFee", "setFees", "excludeFromReward", "includeInReward",
    "setTaxFeePercent", "setBuyFee", "setSellFee", "setSellTax",
    "blacklist", "pause", "unpause", "transferOwnership", "renounceOwnership"
]

DANGEROUS_MODIFIERS = [
    "onlyOwner", "admin", "isOwner", "hasRole"
]

def analyze_static(source_code: str) -> Dict[str, Any]:
    """
    Analyze Solidity source code for potential security issues and dangerous patterns.
    
    Args:
        source_code (str): Solidity source code to analyze
        
    Returns:
        Dict containing analysis results and alerts in the format:
        {
            "functions": List[Alert],
            "owner": {
                "renounced": bool
            },
            "dangerous_functions_found": List[str],
            "dangerous_modifiers_found": List[str],
            "total_dangerous_matches": int
        }
    """
    logger.info("Starting static analysis of contract")
    logger.debug(f"Source code length: {len(source_code)} characters")
    
    # Initialize result with default values
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
    
    logger.debug("Searching for dangerous patterns in contract")

    if not source_code:
        logger.error("No source code provided for static analysis")
        return {
            "static": [{
                "type": "source_code",
                "message": "Source code not verified",
                "severity": "high"
            }]
        }

    # Check for ownership renouncement
    logger.debug("Checking for ownership renouncement...")
    if re.search(r'function\s+renounceOwnership\s*\\(\s*\\)', source_code):
        result["owner"] = {"renounced": True}
        logger.info("Contract has a renounceOwnership function")
    else:
        result["owner"] = {"renounced": False}
        logger.debug("No renounceOwnership function found")

    # Check for dangerous functions
    logger.debug("Checking for dangerous functions...")
    for func in DANGEROUS_FUNCTIONS:
        if re.search(fr'function\s+{func}\s*\\(', source_code, re.IGNORECASE):
            result["dangerous_functions_found"].append(func)
            result["total_dangerous_matches"] += 1
            logger.debug(f"Found dangerous function: {func}")
            
            # Set specific flags for certain functions
            if func == "mint":
                result["has_mint"] = True
                logger.debug("Contract has mint function")
            elif func == "blacklist":
                result["has_blacklist"] = True
                logger.debug("Contract has blacklist function")
            elif "fee" in func.lower():
                result["has_set_fee"] = True
                logger.debug("Contract has fee-related function")
            elif "pause" in func.lower():
                result["has_pause"] = True
                logger.debug("Contract has pause function")

    # Check for dangerous modifiers
    logger.debug("Checking for dangerous modifiers...")
    for modifier in DANGEROUS_MODIFIERS:
        if re.search(fr'modifier\s+{modifier}', source_code, re.IGNORECASE) or \
           re.search(fr'\b{modifier}\\(', source_code, re.IGNORECASE):
            result["dangerous_modifiers_found"].append(modifier)
            result["total_dangerous_matches"] += 1
            logger.debug(f"Found dangerous modifier: {modifier}")
            
            if "owner" in modifier.lower():
                result["has_only_owner"] = True
                logger.debug("Contract has onlyOwner or similar modifier")

    # Process and log findings
    logger.info(
        "Static analysis completed",
        context={
            "dangerous_functions": len(result["dangerous_functions_found"]),
            "dangerous_modifiers": len(result["dangerous_modifiers_found"]),
            "has_owner_controls": result["has_only_owner"],
            "has_mint_function": result["has_mint"]
        }
    )
    
    if result["total_dangerous_matches"] > 0:
        logger.warning(
            f"Found {result['total_dangerous_matches']} potential issues",
            context={"total_issues": result["total_dangerous_matches"]}
        )

    # Create alerts for dangerous functions
    logger.debug("Generating alerts for dangerous functions...")
    for func in result["dangerous_functions_found"]:
        alert = Alert(
            title=f"Dangerous Function: {func}",
            description=f"The contract contains a potentially dangerous function: {func}",
            severity="high"
        )
        result["functions"].append(alert.dict())
        logger.debug(f"Generated alert for dangerous function: {func}")

    # Create alerts for dangerous modifiers
    logger.debug("Generating alerts for dangerous modifiers...")
    for modifier in result["dangerous_modifiers_found"]:
        alert = Alert(
            title=f"Dangerous Modifier: {modifier}",
            description=f"The contract uses a potentially dangerous modifier: {modifier}",
            severity="medium"
        )
        result["functions"].append(alert.dict())
        logger.debug(f"Generated alert for dangerous modifier: {modifier}")

    try:
        # Log the results
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
        
        return result
        
    except Exception as e:
        logger.critical(
            "Critical error during static analysis",
            context={
                "error": str(e), 
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        
        # Return minimal valid response with error indication
        return {
            "functions": [{
                "type": "analysis_error",
                "message": f"Error during static analysis: {str(e)}",
                "severity": "critical"
            }],
            "owner": {
                "renounced": False
            },
            "dangerous_functions_found": [],
            "dangerous_modifiers_found": [],
            "total_dangerous_matches": 0,
            "has_mint": False,
            "has_blacklist": False,
            "has_set_fee": False,
            "has_only_owner": False,
            "has_pause": False
        }
