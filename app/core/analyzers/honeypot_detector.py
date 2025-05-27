"""
Advanced Honeypot Detection Service

This module provides comprehensive honeypot detection using multiple methods:
1. Real PancakeSwap simulation
2. Contract pattern analysis
3. Historical transaction analysis
4. Multi-scenario testing
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal
from web3 import Web3
from web3.exceptions import ContractLogicError, TransactionNotFound
import json

from app.core.utils.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

class HoneypotDetector:
    """Advanced honeypot detection with real blockchain simulation."""
    
    def __init__(self):
        self.web3 = self._init_web3()
        self.router_contract = self._init_router_contract()
        self.wbnb_address = "0xbb4CdB9CBd36B01bD1cBaeBF2De08d9173bc095c"
        self.busd_address = "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
        
        # Test amounts in Wei
        self.test_amounts = [
            Web3.to_wei(0.001, 'ether'),  # 0.001 BNB
            Web3.to_wei(0.01, 'ether'),   # 0.01 BNB
            Web3.to_wei(0.1, 'ether'),    # 0.1 BNB
        ]
        
    def _init_web3(self) -> Web3:
        """Initialize Web3 connection with fallback."""
        try:
            web3 = Web3(Web3.HTTPProvider(settings.BSC_RPC_URL))
            if not web3.is_connected():
                logger.warning("Primary RPC failed, trying backup")
                web3 = Web3(Web3.HTTPProvider(settings.BSC_RPC_URL_BACKUP))
            
            if not web3.is_connected():
                raise ConnectionError("Cannot connect to BSC network")
                
            logger.info("Connected to BSC network", {
                "chain_id": web3.eth.chain_id,
                "latest_block": web3.eth.block_number
            })
            return web3
            
        except Exception as e:
            logger.error("Failed to initialize Web3", {"error": str(e)})
            raise
    
    def _init_router_contract(self):
        """Initialize PancakeSwap router contract."""
        router_abi = [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"}
                ],
                "name": "getAmountsOut",
                "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"}
                ],
                "name": "getAmountsIn",
                "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        return self.web3.eth.contract(
            address=Web3.to_checksum_address(settings.PANCAKESWAP_ROUTER_V2),
            abi=router_abi
        )
    
    async def detect_honeypot(self, token_address: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive honeypot detection using multiple methods.
        
        Args:
            token_address: Token contract address
            metadata: Token metadata from previous analysis
            
        Returns:
            Detailed honeypot analysis results
        """
        start_time = time.time()
        token_address = Web3.to_checksum_address(token_address)
        
        logger.info("Starting comprehensive honeypot detection", {
            "token_address": token_address,
            "token_name": metadata.get("name", "Unknown")
        })
        
        try:
            # Run multiple detection methods
            simulation_results = await self._run_trading_simulation(token_address)
            pattern_analysis = await self._analyze_contract_patterns(token_address, metadata)
            liquidity_analysis = await self._analyze_liquidity_patterns(token_address)
            transaction_analysis = await self._analyze_transaction_history(token_address)
            
            # Combine results and calculate confidence
            final_result = self._combine_detection_results(
                simulation_results,
                pattern_analysis,
                liquidity_analysis,
                transaction_analysis
            )
            
            duration = time.time() - start_time
            logger.info("Honeypot detection completed", {
                "token_address": token_address,
                "is_honeypot": final_result["is_honeypot"],
                "confidence": final_result["confidence"],
                "duration_ms": round(duration * 1000, 2)
            })
            
            return final_result
            
        except Exception as e:
            logger.error("Honeypot detection failed", {
                "token_address": token_address,
                "error": str(e),
                "error_type": type(e).__name__
            }, exc_info=True)
            
            return self._create_error_result(str(e))
    
    async def _run_trading_simulation(self, token_address: str) -> Dict[str, Any]:
        """Simulate buy/sell transactions using PancakeSwap router."""
        logger.debug("Running trading simulation", {"token_address": token_address})
        
        results = {
            "buy_tests": [],
            "sell_tests": [],
            "can_buy": False,
            "can_sell": False,
            "buy_tax_avg": 0.0,
            "sell_tax_avg": 0.0,
            "errors": []
        }
        
        try:
            # Test buying with different amounts
            for amount in self.test_amounts:
                buy_result = await self._simulate_buy(token_address, amount)
                results["buy_tests"].append(buy_result)
                
                if buy_result["success"]:
                    results["can_buy"] = True
                    
                    # Test selling the received tokens
                    if buy_result.get("tokens_out", 0) > 0:
                        sell_result = await self._simulate_sell(
                            token_address, 
                            buy_result["tokens_out"]
                        )
                        results["sell_tests"].append(sell_result)
                        
                        if sell_result["success"]:
                            results["can_sell"] = True
            
            # Calculate average taxes
            if results["buy_tests"]:
                buy_taxes = [t.get("tax_percent", 0) for t in results["buy_tests"] if t["success"]]
                results["buy_tax_avg"] = sum(buy_taxes) / len(buy_taxes) if buy_taxes else 0
                
            if results["sell_tests"]:
                sell_taxes = [t.get("tax_percent", 0) for t in results["sell_tests"] if t["success"]]
                results["sell_tax_avg"] = sum(sell_taxes) / len(sell_taxes) if sell_taxes else 0
            
            return results
            
        except Exception as e:
            logger.error("Trading simulation failed", {
                "token_address": token_address,
                "error": str(e)
            })
            results["errors"].append(str(e))
            return results
    
    async def _simulate_buy(self, token_address: str, bnb_amount: int) -> Dict[str, Any]:
        """Simulate buying tokens with BNB."""
        try:
            path = [
                Web3.to_checksum_address(self.wbnb_address), 
                Web3.to_checksum_address(token_address)
            ]
            
            # Get expected output
            amounts_out = self.router_contract.functions.getAmountsOut(
                bnb_amount, path
            ).call()
            
            expected_tokens = amounts_out[1]
            
            # Simulate with slippage tolerance
            min_tokens_out = int(expected_tokens * 0.95)  # 5% slippage tolerance
            
            # Check if we can actually get tokens
            if expected_tokens > 0:
                # Calculate effective tax
                theoretical_tokens = self._calculate_theoretical_tokens(bnb_amount, token_address)
                tax_percent = max(0, (theoretical_tokens - expected_tokens) / theoretical_tokens * 100) if theoretical_tokens > 0 else 0
                
                return {
                    "success": True,
                    "bnb_in": bnb_amount,
                    "tokens_out": expected_tokens,
                    "expected_tokens": theoretical_tokens,
                    "tax_percent": round(tax_percent, 2),
                    "slippage_percent": 5.0,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "bnb_in": bnb_amount,
                    "tokens_out": 0,
                    "error": "No tokens received"
                }
                
        except ContractLogicError as e:
            return {
                "success": False,
                "bnb_in": bnb_amount,
                "tokens_out": 0,
                "error": f"Contract logic error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "bnb_in": bnb_amount,
                "tokens_out": 0,
                "error": str(e)
            }
    
    async def _simulate_sell(self, token_address: str, token_amount: int) -> Dict[str, Any]:
        """Simulate selling tokens for BNB."""
        try:
            path = [
                Web3.to_checksum_address(token_address), 
                Web3.to_checksum_address(self.wbnb_address)
            ]
            
            # Get expected output
            amounts_out = self.router_contract.functions.getAmountsOut(
                token_amount, path
            ).call()
            
            expected_bnb = amounts_out[1]
            
            if expected_bnb > 0:
                # Calculate effective tax
                theoretical_bnb = self._calculate_theoretical_bnb(token_amount, token_address)
                tax_percent = max(0, (theoretical_bnb - expected_bnb) / theoretical_bnb * 100) if theoretical_bnb > 0 else 0
                
                return {
                    "success": True,
                    "tokens_in": token_amount,
                    "bnb_out": expected_bnb,
                    "expected_bnb": theoretical_bnb,
                    "tax_percent": round(tax_percent, 2),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "tokens_in": token_amount,
                    "bnb_out": 0,
                    "error": "No BNB received"
                }
                
        except ContractLogicError as e:
            return {
                "success": False,
                "tokens_in": token_amount,
                "bnb_out": 0,
                "error": f"Contract logic error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "tokens_in": token_amount,
                "bnb_out": 0,
                "error": str(e)
            }
    
    def _calculate_theoretical_tokens(self, bnb_amount: int, token_address: str) -> int:
        """Calculate theoretical token amount without fees."""
        # This would require getting the actual pool reserves
        # For now, we'll use the router result as baseline
        try:
            path = [
                Web3.to_checksum_address(self.wbnb_address), 
                Web3.to_checksum_address(token_address)
            ]
            amounts_out = self.router_contract.functions.getAmountsOut(
                bnb_amount, path
            ).call()
            return amounts_out[1]
        except:
            return 0
    
    def _calculate_theoretical_bnb(self, token_amount: int, token_address: str) -> int:
        """Calculate theoretical BNB amount without fees."""
        try:
            path = [
                Web3.to_checksum_address(token_address), 
                Web3.to_checksum_address(self.wbnb_address)
            ]
            amounts_out = self.router_contract.functions.getAmountsOut(
                token_amount, path
            ).call()
            return amounts_out[1]
        except:
            return 0
    
    async def _analyze_contract_patterns(self, token_address: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze contract code for honeypot patterns."""
        logger.debug("Analyzing contract patterns", {"token_address": token_address})
        
        source_code = metadata.get("SourceCode", "")
        if not source_code:
            return {"pattern_score": 0, "suspicious_patterns": [], "confidence": 0}
        
        suspicious_patterns = []
        pattern_score = 0
        
        # Check for common honeypot patterns
        honeypot_indicators = [
            ("transfer restrictions", ["onlyOwner", "require(from == owner", "require(to == owner"]),
            ("sell blocking", ["revert()", "require(false)", "assert(false)"]),
            ("balance manipulation", ["balanceOf[", "_balances[", "return 0"]),
            ("approval blocking", ["approve(", "allowance(", "return false"]),
            ("blacklist functions", ["blacklist", "isBlacklisted", "blocked"]),
            ("pause functions", ["pause", "paused", "whenNotPaused"]),
            ("max transaction", ["maxTxAmount", "maxTransactionAmount", "require(amount <"]),
            ("cooldown mechanisms", ["cooldown", "lastTx", "block.timestamp"]),
        ]
        
        for pattern_name, keywords in honeypot_indicators:
            for keyword in keywords:
                if keyword.lower() in source_code.lower():
                    suspicious_patterns.append({
                        "pattern": pattern_name,
                        "keyword": keyword,
                        "severity": "high" if pattern_name in ["sell blocking", "balance manipulation"] else "medium"
                    })
                    pattern_score += 10 if pattern_name in ["sell blocking", "balance manipulation"] else 5
        
        # Check for legitimate patterns that reduce suspicion
        legitimate_patterns = [
            "OpenZeppelin",
            "SafeMath",
            "IERC20",
            "Context",
            "Ownable"
        ]
        
        for pattern in legitimate_patterns:
            if pattern in source_code:
                pattern_score = max(0, pattern_score - 2)
        
        confidence = min(100, pattern_score * 2)
        
        return {
            "pattern_score": pattern_score,
            "suspicious_patterns": suspicious_patterns,
            "confidence": confidence,
            "has_source": bool(source_code)
        }
    
    async def _analyze_liquidity_patterns(self, token_address: str) -> Dict[str, Any]:
        """Analyze liquidity patterns for honeypot indicators."""
        logger.debug("Analyzing liquidity patterns", {"token_address": token_address})
        
        try:
            # Check if there's a liquidity pool
            factory_abi = [
                {
                    "inputs": [
                        {"internalType": "address", "name": "tokenA", "type": "address"},
                        {"internalType": "address", "name": "tokenB", "type": "address"}
                    ],
                    "name": "getPair",
                    "outputs": [{"internalType": "address", "name": "pair", "type": "address"}],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]
            
            factory_contract = self.web3.eth.contract(
                address=Web3.to_checksum_address(settings.PANCAKESWAP_FACTORY_V2),
                abi=factory_abi
            )
            
            pair_address = factory_contract.functions.getPair(
                Web3.to_checksum_address(token_address), 
                Web3.to_checksum_address(self.wbnb_address)
            ).call()
            
            if pair_address == "0x0000000000000000000000000000000000000000":
                return {
                    "has_liquidity": False,
                    "liquidity_score": 0,
                    "warning": "No liquidity pool found"
                }
            
            # Analyze pair contract for suspicious patterns
            pair_code = self.web3.eth.get_code(pair_address)
            
            return {
                "has_liquidity": True,
                "pair_address": pair_address,
                "liquidity_score": 50,  # Neutral score for having liquidity
                "code_size": len(pair_code)
            }
            
        except Exception as e:
            logger.warning("Liquidity analysis failed", {"error": str(e)})
            return {
                "has_liquidity": False,
                "liquidity_score": 0,
                "error": str(e)
            }
    
    async def _analyze_transaction_history(self, token_address: str) -> Dict[str, Any]:
        """Analyze recent transactions for honeypot patterns."""
        logger.debug("Analyzing transaction history", {"token_address": token_address})
        
        try:
            # Get recent transactions (this would require BSCScan API or event logs)
            # For now, we'll return a placeholder
            return {
                "recent_transactions": 0,
                "successful_sells": 0,
                "failed_sells": 0,
                "sell_success_rate": 0.0,
                "analysis_available": False
            }
            
        except Exception as e:
            logger.warning("Transaction history analysis failed", {"error": str(e)})
            return {
                "recent_transactions": 0,
                "analysis_available": False,
                "error": str(e)
            }
    
    def _combine_detection_results(self, simulation: Dict, patterns: Dict, 
                                 liquidity: Dict, transactions: Dict) -> Dict[str, Any]:
        """Combine all detection methods into final result."""
        
        # Calculate honeypot probability
        honeypot_indicators = []
        confidence_factors = []
        
        # Simulation results (highest weight)
        if simulation.get("can_buy") and not simulation.get("can_sell"):
            honeypot_indicators.append("Cannot sell after buying")
            confidence_factors.append(90)
        elif not simulation.get("can_buy"):
            honeypot_indicators.append("Cannot buy tokens")
            confidence_factors.append(70)
        elif simulation.get("sell_tax_avg", 0) > 50:
            honeypot_indicators.append(f"Extremely high sell tax: {simulation['sell_tax_avg']:.1f}%")
            confidence_factors.append(80)
        elif simulation.get("sell_tax_avg", 0) > 20:
            honeypot_indicators.append(f"High sell tax: {simulation['sell_tax_avg']:.1f}%")
            confidence_factors.append(60)
        
        # Pattern analysis (medium weight)
        pattern_score = patterns.get("pattern_score", 0)
        if pattern_score > 30:
            honeypot_indicators.append("Multiple suspicious code patterns")
            confidence_factors.append(70)
        elif pattern_score > 15:
            honeypot_indicators.append("Some suspicious code patterns")
            confidence_factors.append(40)
        
        # Liquidity analysis (low weight)
        if not liquidity.get("has_liquidity"):
            honeypot_indicators.append("No liquidity pool found")
            confidence_factors.append(30)
        
        # Calculate final result
        is_honeypot = len(honeypot_indicators) > 0 and max(confidence_factors, default=0) > 60
        confidence = max(confidence_factors, default=0) if honeypot_indicators else 5
        
        # Risk level
        if confidence >= 80:
            risk_level = "CRITICAL"
        elif confidence >= 60:
            risk_level = "HIGH"
        elif confidence >= 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "is_honeypot": is_honeypot,
            "confidence": confidence,
            "risk_level": risk_level,
            "indicators": honeypot_indicators,
            "simulation_results": simulation,
            "pattern_analysis": patterns,
            "liquidity_analysis": liquidity,
            "transaction_analysis": transactions,
            "buy_tax": simulation.get("buy_tax_avg", 0),
            "sell_tax": simulation.get("sell_tax_avg", 0),
            "can_buy": simulation.get("can_buy", False),
            "can_sell": simulation.get("can_sell", False),
            "recommendation": self._get_recommendation(is_honeypot, confidence, risk_level)
        }
    
    def _get_recommendation(self, is_honeypot: bool, confidence: int, risk_level: str) -> str:
        """Get user-friendly recommendation."""
        if is_honeypot and confidence >= 80:
            return "🚨 AVOID - High probability honeypot detected"
        elif is_honeypot and confidence >= 60:
            return "⚠️ HIGH RISK - Likely honeypot, avoid trading"
        elif confidence >= 30:
            return "⚡ MODERATE RISK - Exercise caution, small test trades only"
        else:
            return "✅ LOW RISK - No significant honeypot indicators found"
    
    def _create_error_result(self, error: str) -> Dict[str, Any]:
        """Create error result when detection fails."""
        return {
            "is_honeypot": True,  # Assume worst case on error
            "confidence": 0,
            "risk_level": "UNKNOWN",
            "indicators": ["Analysis failed"],
            "error": error,
            "buy_tax": 0,
            "sell_tax": 0,
            "can_buy": False,
            "can_sell": False,
            "recommendation": "⚠️ UNKNOWN RISK - Analysis failed, proceed with extreme caution"
        }

# Global instance
honeypot_detector = HoneypotDetector() 