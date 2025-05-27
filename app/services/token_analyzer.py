"""Token Analysis Service

This module provides comprehensive token analysis functionality,
including static, dynamic, and on-chain analysis specifically for tokens.
"""

from typing import Dict, Optional, Any
from datetime import datetime, timezone

from app.core.utils.logger import get_logger
from app.core.utils.metadata import fetch_token_metadata
from app.core.analyzers.static_analyzer import analyze_static
from app.core.analyzers.dynamic_analyzer import analyze_dynamic
from app.core.analyzers.onchain_analyzer import analyze_onchain
from app.core.utils.scoring import calculate_risk_score
from app.schemas.analyze_response import AnalyzeResponse

logger = get_logger(__name__)

class TokenAnalyzer:
    """Service for analyzing individual tokens on BSC."""
    
    def __init__(self):
        self.analysis_timeout = 30  # seconds
        
    async def analyze_token(self, token_address: str) -> Dict[str, Any]:
        """
        Analyzes a BSC token and returns a security report.
        
        Args:
            token_address: BSC token address to analyze
            
        Returns:
            Dictionary with comprehensive token analysis results
        """
        start_time = datetime.now(timezone.utc)
        
        logger.info("Starting token analysis", {
            "token_address": token_address,
            "timestamp": start_time.isoformat()
        })
        
        try:
            # Validate and normalize token address
            normalized_address = self._validate_and_normalize_address(token_address)
            
            # Fetch token metadata
            metadata = await self._fetch_token_metadata(normalized_address)
            if self._is_metadata_error(metadata):
                return self._create_error_response(normalized_address, metadata)
            
            # Perform analysis layers
            static_results = await self._perform_static_analysis(metadata)
            dynamic_results = await self._perform_dynamic_analysis(metadata)
            onchain_results = await self._perform_onchain_analysis(metadata)
            
            # Calculate final risk score
            risk_score = self._calculate_risk_score(static_results, dynamic_results, onchain_results)
            
            # Build response
            response = self._build_analysis_response(
                normalized_address, metadata, static_results, 
                dynamic_results, onchain_results, risk_score, start_time
            )
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.success("Token analysis completed", {
                "token_address": normalized_address,
                "score": risk_score["score"],
                "grade": risk_score["grade"],
                "duration_ms": round(duration * 1000, 2)
            })
            
            return response
            
        except Exception as e:
            logger.failure("Token analysis failed", {
                "token_address": token_address,
                "error": str(e),
                "error_type": type(e).__name__
            }, exc_info=True)
            return AnalyzeResponse.create_error_response(
                token_address=token_address,
                error=str(e)
            )
    
    def _validate_and_normalize_address(self, token_address: str) -> str:
        """Validate and normalize token address format."""
        if not token_address or not isinstance(token_address, str):
            raise ValueError(f"Invalid token address: {token_address}")
            
        # Clean and format token address
        normalized = token_address.strip().lower()
        if not normalized.startswith('0x'):
            normalized = f'0x{normalized}'
            
        # Validate address length
        if len(normalized) != 42:
            raise ValueError(f"Invalid token address length: {normalized}")
            
        return normalized
    
    async def _fetch_token_metadata(self, token_address: str) -> Dict[str, Any]:
        """Fetch token metadata from BSCScan."""
        logger.debug("Fetching token metadata", context={"token_address": token_address})
        
        try:
            metadata = fetch_token_metadata(token_address)
            if not metadata or not isinstance(metadata, dict):
                raise ValueError("Invalid metadata format returned")
            return metadata
        except Exception as e:
            logger.error(
                "Failed to fetch token metadata",
                context={"token_address": token_address, "error": str(e)},
                exc_info=True
            )
            raise
    
    def _is_metadata_error(self, metadata: Dict[str, Any]) -> bool:
        """Check if metadata contains error information."""
        return (
            metadata.get("name") == "Error" or 
            "error" in metadata or
            not metadata.get("name")
        )
    
    def _create_error_response(self, token_address: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create error response for failed metadata fetch."""
        error_msg = metadata.get("error", "Failed to fetch token metadata")
        logger.error(
            f"Metadata fetch failed: {error_msg}",
            context={
                "token_address": token_address,
                "error": error_msg,
                "error_type": metadata.get("error_type", "Unknown")
            }
        )
        return AnalyzeResponse.create_error_response(
            token_address=token_address,
            error=error_msg
        )
    
    async def _perform_static_analysis(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Perform static code analysis on the token contract."""
        logger.debug("Performing static analysis")
        
        try:
            source_code = metadata.get("SourceCode", "")
            return analyze_static(source_code)
        except Exception as e:
            logger.warning(
                "Static analysis failed, using fallback",
                context={"error": str(e)}
            )
            return self._get_static_analysis_fallback(str(e))
    
    async def _perform_dynamic_analysis(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Perform dynamic analysis (honeypot detection, fee analysis)."""
        logger.debug("Performing dynamic analysis")
        
        try:
            # For now, we'll use a mock simulation result
            # In a real implementation, this would call PancakeSwap simulation
            mock_simulation = {
                "buy": {
                    "success": True,
                    "expected_amount_out": 1000,
                    "amount_out": 950,
                    "error": None
                },
                "sell": {
                    "success": True,
                    "expected_amount_out": 950,
                    "amount_out": 900,
                    "error": None
                }
            }
            return analyze_dynamic(mock_simulation)
        except Exception as e:
            logger.warning(
                "Dynamic analysis failed, using fallback",
                context={"error": str(e)}
            )
            return self._get_dynamic_analysis_fallback(str(e))
    
    async def _perform_onchain_analysis(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Perform on-chain analysis (holder distribution, liquidity, etc)."""
        logger.debug("Performing on-chain analysis")
        
        try:
            # Add liquidity info placeholder
            metadata["lp_info"] = {
                "locked": False,
                "percent_locked": None
            }
            return analyze_onchain(metadata)
        except Exception as e:
            logger.warning(
                "On-chain analysis failed, using fallback",
                context={"error": str(e)}
            )
            return {"holders": {"distribution": "unknown"}, "liquidity": {"locked": False}}
    
    def _calculate_risk_score(self, static_results: Dict, dynamic_results: Dict, onchain_results: Dict) -> Dict[str, Any]:
        """Calculate final risk score based on all analysis results."""
        logger.debug("Calculating risk score")
        return calculate_risk_score(static_results, dynamic_results, onchain_results)
    
    def _build_analysis_response(self, token_address: str, metadata: Dict, static_results: Dict,
                               dynamic_results: Dict, onchain_results: Dict, risk_score: Dict,
                               start_time: datetime) -> Dict[str, Any]:
        """Build the final analysis response."""
        return {
            "status": "completed",
            "timestamp": start_time.isoformat(),
            "token_address": token_address,
            "token_info": {
                "name": metadata.get("TokenName", "Unknown"),
                "symbol": metadata.get("TokenSymbol", "Unknown"),
                "decimals": int(metadata.get("Decimals", 18)),
                "total_supply": metadata.get("TotalSupply", "0"),
                "contract_creator": metadata.get("ContractCreator", "Unknown")
            },
            "score": {
                "value": risk_score["score"],
                "label": risk_score["grade"],
                "risk_meter": risk_score["risk_meter"]
            },
            "honeypot": {
                "is_honeypot": dynamic_results.get("honeypot", {}).get("is_honeypot", False),
                "buy_success": dynamic_results.get("honeypot", {}).get("buy_success", None),
                "sell_success": dynamic_results.get("honeypot", {}).get("sell_success", None),
                "high_tax": dynamic_results.get("honeypot", {}).get("high_tax", None),
                "tax_discrepancy": dynamic_results.get("honeypot", {}).get("tax_discrepancy", None)
            },
            "fees": {
                "buy": dynamic_results.get("fees", {}).get("buy", 0.0),
                "sell": dynamic_results.get("fees", {}).get("sell", 0.0),
                "buy_slippage": dynamic_results.get("fees", {}).get("buy_slippage", 0.0),
                "sell_slippage": dynamic_results.get("fees", {}).get("sell_slippage", 0.0),
                "buy_mutable": dynamic_results.get("fees", {}).get("buy_mutable", False),
                "sell_mutable": dynamic_results.get("fees", {}).get("sell_mutable", False)
            },
            "contract_security": {
                "owner_renounced": static_results.get("owner", {}).get("renounced", False),
                "has_mint": static_results.get("has_mint", False),
                "has_blacklist": static_results.get("has_blacklist", False),
                "has_set_fee": static_results.get("has_set_fee", False),
                "has_pause": static_results.get("has_pause", False),
                "dangerous_functions": static_results.get("dangerous_functions_found", []),
                "dangerous_modifiers": static_results.get("dangerous_modifiers_found", [])
            },
            "alerts": risk_score.get("alerts", []),
            "risks": risk_score.get("risks", [])
        }
    
    def _get_static_analysis_fallback(self, error: str) -> Dict[str, Any]:
        """Fallback response for failed static analysis."""
        return {
            "functions": [{
                "type": "analysis_error",
                "message": f"Error during static analysis: {error}",
                "severity": "critical"
            }],
            "owner": {"renounced": False},
            "dangerous_functions_found": [],
            "dangerous_modifiers_found": [],
            "total_dangerous_matches": 0,
            "has_mint": False,
            "has_blacklist": False,
            "has_set_fee": False,
            "has_only_owner": False,
            "has_pause": False
        }
    
    def _get_dynamic_analysis_fallback(self, error: str) -> Dict[str, Any]:
        """Fallback response for failed dynamic analysis."""
        return {
            "honeypot": {
                "is_honeypot": False,
                "buy_success": None,
                "sell_success": None,
                "high_tax": None,
                "tax_discrepancy": None,
                "error": error
            },
            "fees": {
                "buy": 0.0,
                "sell": 0.0,
                "buy_slippage": 0.0,
                "sell_slippage": 0.0,
                "buy_mutable": False,
                "sell_mutable": False
            }
        }

# Global instance
token_analyzer = TokenAnalyzer() 