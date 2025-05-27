"""Audit Routes - Comprehensive Analysis for Developers

This module contains API routes for comprehensive audit functionality,
designed for developers, security researchers, and advanced users.
"""

from fastapi import APIRouter, HTTPException, Path, Query
from typing import Optional
import time

from app.core.utils.logger import get_logger
from app.services.token_audit_service import token_audit_service
from app.services.pool_audit_service import pool_audit_service

logger = get_logger(__name__)

router = APIRouter(tags=["audits"])

# ============================================================================
# TOKEN AUDIT ROUTES
# ============================================================================

@router.get("/tokens/{token_address}")
async def audit_token_comprehensive(
    token_address: str = Path(..., description="Token address to audit")
):
    """
    Comprehensive token audit for developers and security researchers.
    
    Returns detailed technical analysis including:
    - Complete contract analysis
    - Security vulnerabilities
    - Code quality assessment
    - Detailed recommendations
    - Improvement suggestions
    
    Perfect for:
    - Security audits
    - Due diligence
    - Development teams
    - Investment research
    
    Args:
        token_address: The token address to audit
        
    Returns:
        Comprehensive audit results with technical details and recommendations
    """
    logger.info("Comprehensive token audit request", {
        "token_address": token_address,
        "endpoint": "/audits/tokens"
    })
    
    try:
        start_time = time.time()
        result = await token_audit_service.audit_token(token_address)
        duration = time.time() - start_time
        
        if result.get("status") == "error":
            error_msg = result.get("error", "Audit failed")
            logger.warning("Token audit returned error", {
                "token_address": token_address,
                "error": error_msg
            })
            raise HTTPException(
                status_code=400,
                detail=f"Token audit failed: {error_msg}"
            )
        
        logger.success("Comprehensive token audit completed", {
            "token_address": token_address,
            "security_score": result.get("security_assessment", {}).get("overall_score"),
            "vulnerabilities_found": len(result.get("vulnerabilities", [])),
            "duration_ms": round(duration * 1000, 2)
        })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token audit endpoint failed", {
            "token_address": token_address,
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during token audit: {str(e)}"
        )

@router.get("/tokens/{token_address}/security")
async def audit_token_security(
    token_address: str = Path(..., description="Token address for security audit")
):
    """
    Security-focused token audit.
    
    Returns detailed security analysis including:
    - Vulnerability assessment
    - Risk classification
    - Security score
    - Critical issues
    - Security recommendations
    
    Optimized for:
    - Security teams
    - Penetration testing
    - Risk assessment
    - Compliance checks
    
    Args:
        token_address: The token address to audit for security
        
    Returns:
        Security-focused audit results
    """
    logger.info("Security token audit request", {
        "token_address": token_address,
        "endpoint": "/audits/tokens/security"
    })
    
    try:
        result = await token_audit_service.audit_token(token_address)
        
        if result.get("status") == "error":
            error_msg = result.get("error", "Security audit failed")
            raise HTTPException(
                status_code=400,
                detail=f"Security audit failed: {error_msg}"
            )
        
        # Extract security-focused information
        security_assessment = result.get("security_assessment", {})
        vulnerabilities = result.get("vulnerabilities", [])
        static_analysis = result.get("static_analysis", {})
        
        security_result = {
            "status": "success",
            "timestamp": result.get("timestamp"),
            "analysis_type": "security_audit",
            "token_address": token_address,
            
            # Security assessment
            "security_score": security_assessment.get("overall_score", 0),
            "security_grade": security_assessment.get("security_grade", "F"),
            
            # Vulnerabilities by severity
            "critical_vulnerabilities": security_assessment.get("critical_issues", []),
            "high_vulnerabilities": security_assessment.get("high_issues", []),
            "medium_vulnerabilities": security_assessment.get("medium_issues", []),
            "low_vulnerabilities": security_assessment.get("low_issues", []),
            
            # Security metrics
            "total_vulnerabilities": len(vulnerabilities),
            "code_quality": static_analysis.get("code_quality", {}),
            
            # Security recommendations
            "security_recommendations": [
                rec for rec in result.get("recommendations", [])
                if rec.get("category") in ["security", "ownership"]
            ],
            
            # Audit metadata
            "audit_info": result.get("audit_info", {})
        }
        
        logger.success("Security token audit completed", {
            "token_address": token_address,
            "security_score": security_result["security_score"],
            "vulnerabilities": security_result["total_vulnerabilities"]
        })
        
        return security_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Security audit endpoint failed", {
            "token_address": token_address,
            "error": str(e)
        }, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during security audit: {str(e)}"
        )

@router.get("/tokens/{token_address}/recommendations")
async def get_token_recommendations(
    token_address: str = Path(..., description="Token address for recommendations")
):
    """
    Get improvement recommendations for a token.
    
    Returns actionable recommendations including:
    - Security improvements
    - Code quality enhancements
    - Best practice suggestions
    - Implementation guidance
    
    Perfect for:
    - Development teams
    - Code reviews
    - Security improvements
    - Best practices
    
    Args:
        token_address: The token address to get recommendations for
        
    Returns:
        Detailed improvement recommendations
    """
    logger.info("Token recommendations request", {
        "token_address": token_address,
        "endpoint": "/audits/tokens/recommendations"
    })
    
    try:
        result = await token_audit_service.audit_token(token_address)
        
        if result.get("status") == "error":
            error_msg = result.get("error", "Recommendations failed")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to generate recommendations: {error_msg}"
            )
        
        recommendations = result.get("recommendations", [])
        
        # Categorize recommendations
        categorized_recommendations = {
            "critical": [r for r in recommendations if r.get("priority") == "critical"],
            "high": [r for r in recommendations if r.get("priority") == "high"],
            "medium": [r for r in recommendations if r.get("priority") == "medium"],
            "low": [r for r in recommendations if r.get("priority") == "low"]
        }
        
        recommendations_result = {
            "status": "success",
            "timestamp": result.get("timestamp"),
            "token_address": token_address,
            "total_recommendations": len(recommendations),
            "recommendations_by_priority": categorized_recommendations,
            "recommendations_by_category": {
                "security": [r for r in recommendations if r.get("category") == "security"],
                "ownership": [r for r in recommendations if r.get("category") == "ownership"],
                "tokenomics": [r for r in recommendations if r.get("category") == "tokenomics"],
                "functionality": [r for r in recommendations if r.get("category") == "functionality"],
                "fees": [r for r in recommendations if r.get("category") == "fees"]
            },
            "implementation_summary": {
                "immediate_actions": len(categorized_recommendations["critical"]),
                "short_term_actions": len(categorized_recommendations["high"]),
                "long_term_actions": len(categorized_recommendations["medium"] + categorized_recommendations["low"])
            }
        }
        
        logger.success("Token recommendations generated", {
            "token_address": token_address,
            "total_recommendations": recommendations_result["total_recommendations"]
        })
        
        return recommendations_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Recommendations endpoint failed", {
            "token_address": token_address,
            "error": str(e)
        }, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error generating recommendations: {str(e)}"
        )

# ============================================================================
# POOL AUDIT ROUTES
# ============================================================================

@router.get("/pools/{pool_address}")
async def audit_pool_comprehensive(
    pool_address: str = Path(..., description="Pool address to audit"),
    token_address: Optional[str] = Query(None, description="Optional token address for context")
):
    """
    Comprehensive pool audit for developers and DeFi researchers.
    
    Returns detailed technical analysis including:
    - Complete liquidity analysis
    - Security vulnerabilities
    - Economic model assessment
    - Detailed recommendations
    - Improvement suggestions
    
    Perfect for:
    - DeFi protocols
    - Liquidity providers
    - Investment research
    - Risk assessment
    
    Args:
        pool_address: The pool address to audit
        token_address: Optional token address for additional context
        
    Returns:
        Comprehensive audit results with technical details and recommendations
    """
    logger.info("Comprehensive pool audit request", {
        "pool_address": pool_address,
        "token_address": token_address,
        "endpoint": "/audits/pools"
    })
    
    try:
        start_time = time.time()
        result = await pool_audit_service.audit_pool(pool_address, token_address)
        duration = time.time() - start_time
        
        if result.get("status") == "error":
            error_msg = result.get("error", "Audit failed")
            logger.warning("Pool audit returned error", {
                "pool_address": pool_address,
                "error": error_msg
            })
            raise HTTPException(
                status_code=400,
                detail=f"Pool audit failed: {error_msg}"
            )
        
        logger.success("Comprehensive pool audit completed", {
            "pool_address": pool_address,
            "overall_score": result.get("comprehensive_assessment", {}).get("overall_score"),
            "issues_found": len(result.get("issues", [])),
            "duration_ms": round(duration * 1000, 2)
        })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Pool audit endpoint failed", {
            "pool_address": pool_address,
            "token_address": token_address,
            "error": str(e),
            "error_type": type(e).__name__
        }, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during pool audit: {str(e)}"
        )

@router.get("/pools/{pool_address}/liquidity")
async def audit_pool_liquidity(
    pool_address: str = Path(..., description="Pool address for liquidity audit")
):
    """
    Liquidity-focused pool audit.
    
    Returns detailed liquidity analysis including:
    - Liquidity depth analysis
    - Lock status assessment
    - Utilization metrics
    - Stability analysis
    - Liquidity recommendations
    
    Optimized for:
    - Liquidity providers
    - DeFi protocols
    - Risk management
    - Investment decisions
    
    Args:
        pool_address: The pool address to audit for liquidity
        
    Returns:
        Liquidity-focused audit results
    """
    logger.info("Liquidity pool audit request", {
        "pool_address": pool_address,
        "endpoint": "/audits/pools/liquidity"
    })
    
    try:
        result = await pool_audit_service.audit_pool(pool_address)
        
        if result.get("status") == "error":
            error_msg = result.get("error", "Liquidity audit failed")
            raise HTTPException(
                status_code=400,
                detail=f"Liquidity audit failed: {error_msg}"
            )
        
        # Extract liquidity-focused information
        liquidity_analysis = result.get("liquidity_analysis", {})
        comprehensive_assessment = result.get("comprehensive_assessment", {})
        
        liquidity_result = {
            "status": "success",
            "timestamp": result.get("timestamp"),
            "analysis_type": "liquidity_audit",
            "pool_address": pool_address,
            
            # Liquidity metrics
            "liquidity_score": liquidity_analysis.get("liquidity_score", 0),
            "total_liquidity_usd": liquidity_analysis.get("total_liquidity_usd", 0),
            "utilization_rate": liquidity_analysis.get("utilization_rate", 0),
            "volume_to_liquidity_ratio": liquidity_analysis.get("volume_to_liquidity_ratio", 0),
            
            # Lock analysis
            "lock_analysis": liquidity_analysis.get("lock_analysis", {}),
            
            # Reserve analysis
            "reserve_analysis": liquidity_analysis.get("reserve_analysis", {}),
            
            # Depth and stability
            "depth_analysis": liquidity_analysis.get("depth_analysis", {}),
            "stability_metrics": liquidity_analysis.get("stability_metrics", {}),
            
            # Liquidity recommendations
            "liquidity_recommendations": [
                rec for rec in result.get("recommendations", [])
                if rec.get("category") == "liquidity"
            ],
            
            # Component scores
            "component_scores": comprehensive_assessment.get("component_scores", {}),
            
            # Audit metadata
            "audit_info": result.get("audit_info", {})
        }
        
        logger.success("Liquidity pool audit completed", {
            "pool_address": pool_address,
            "liquidity_score": liquidity_result["liquidity_score"],
            "liquidity_usd": liquidity_result["total_liquidity_usd"]
        })
        
        return liquidity_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Liquidity audit endpoint failed", {
            "pool_address": pool_address,
            "error": str(e)
        }, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during liquidity audit: {str(e)}"
        )

@router.get("/pools/{pool_address}/economics")
async def audit_pool_economics(
    pool_address: str = Path(..., description="Pool address for economic audit")
):
    """
    Economic-focused pool audit.
    
    Returns detailed economic analysis including:
    - Fee structure analysis
    - Profitability assessment
    - Impermanent loss analysis
    - APR/APY calculations
    - Economic recommendations
    
    Optimized for:
    - Yield farmers
    - Investment analysis
    - Economic research
    - Strategy development
    
    Args:
        pool_address: The pool address to audit for economics
        
    Returns:
        Economic-focused audit results
    """
    logger.info("Economic pool audit request", {
        "pool_address": pool_address,
        "endpoint": "/audits/pools/economics"
    })
    
    try:
        result = await pool_audit_service.audit_pool(pool_address)
        
        if result.get("status") == "error":
            error_msg = result.get("error", "Economic audit failed")
            raise HTTPException(
                status_code=400,
                detail=f"Economic audit failed: {error_msg}"
            )
        
        # Extract economic-focused information
        economic_analysis = result.get("economic_analysis", {})
        comprehensive_assessment = result.get("comprehensive_assessment", {})
        
        economic_result = {
            "status": "success",
            "timestamp": result.get("timestamp"),
            "analysis_type": "economic_audit",
            "pool_address": pool_address,
            
            # Profitability metrics
            "profitability_score": economic_analysis.get("profitability_score", 0),
            "fee_metrics": economic_analysis.get("fee_metrics", {}),
            
            # Impermanent loss analysis
            "impermanent_loss_analysis": economic_analysis.get("impermanent_loss_analysis", {}),
            
            # Efficiency metrics
            "efficiency_metrics": economic_analysis.get("efficiency_metrics", {}),
            
            # Fee analysis
            "fee_analysis": economic_analysis.get("fee_analysis", {}),
            
            # Economic recommendations
            "economic_recommendations": [
                rec for rec in result.get("recommendations", [])
                if rec.get("category") in ["economics", "fees"]
            ],
            
            # Component scores
            "component_scores": comprehensive_assessment.get("component_scores", {}),
            
            # Audit metadata
            "audit_info": result.get("audit_info", {})
        }
        
        logger.success("Economic pool audit completed", {
            "pool_address": pool_address,
            "profitability_score": economic_result["profitability_score"],
            "estimated_apr": economic_result["fee_metrics"].get("estimated_apr", 0)
        })
        
        return economic_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Economic audit endpoint failed", {
            "pool_address": pool_address,
            "error": str(e)
        }, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during economic audit: {str(e)}"
        )

# ============================================================================
# COMPARATIVE ANALYSIS ROUTES
# ============================================================================

@router.post("/tokens/compare")
async def compare_tokens(
    token_addresses: list[str]
):
    """
    Compare multiple tokens side by side.
    
    Performs comprehensive audits on multiple tokens and provides
    comparative analysis. Limited to 5 tokens per request.
    
    Args:
        token_addresses: List of token addresses to compare (max 5)
        
    Returns:
        Comparative analysis results
    """
    if len(token_addresses) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 tokens allowed per comparison"
        )
    
    logger.info("Token comparison request", {
        "token_count": len(token_addresses),
        "endpoint": "/audits/tokens/compare"
    })
    
    results = []
    for token_address in token_addresses:
        try:
            result = await token_audit_service.audit_token(token_address)
            results.append(result)
        except Exception as e:
            results.append({
                "status": "error",
                "token_address": token_address,
                "error": str(e)
            })
    
    # Generate comparison summary
    successful_results = [r for r in results if r.get("status") == "success"]
    
    comparison_summary = {
        "highest_security_score": max([r.get("security_assessment", {}).get("overall_score", 0) for r in successful_results], default=0),
        "lowest_security_score": min([r.get("security_assessment", {}).get("overall_score", 100) for r in successful_results], default=0),
        "average_security_score": sum([r.get("security_assessment", {}).get("overall_score", 0) for r in successful_results]) / len(successful_results) if successful_results else 0,
        "total_vulnerabilities": sum([len(r.get("vulnerabilities", [])) for r in successful_results]),
        "recommended_token": None
    }
    
    # Find recommended token (highest security score)
    if successful_results:
        best_token = max(successful_results, key=lambda x: x.get("security_assessment", {}).get("overall_score", 0))
        comparison_summary["recommended_token"] = best_token.get("token_address")
    
    logger.info("Token comparison completed", {
        "token_count": len(token_addresses),
        "successful": len(successful_results),
        "failed": len(results) - len(successful_results)
    })
    
    return {
        "status": "completed",
        "total_tokens": len(token_addresses),
        "comparison_summary": comparison_summary,
        "detailed_results": results
    }

@router.post("/pools/compare")
async def compare_pools(
    pool_addresses: list[str]
):
    """
    Compare multiple pools side by side.
    
    Performs comprehensive audits on multiple pools and provides
    comparative analysis. Limited to 3 pools per request.
    
    Args:
        pool_addresses: List of pool addresses to compare (max 3)
        
    Returns:
        Comparative analysis results
    """
    if len(pool_addresses) > 3:
        raise HTTPException(
            status_code=400,
            detail="Maximum 3 pools allowed per comparison"
        )
    
    logger.info("Pool comparison request", {
        "pool_count": len(pool_addresses),
        "endpoint": "/audits/pools/compare"
    })
    
    results = []
    for pool_address in pool_addresses:
        try:
            result = await pool_audit_service.audit_pool(pool_address)
            results.append(result)
        except Exception as e:
            results.append({
                "status": "error",
                "pool_address": pool_address,
                "error": str(e)
            })
    
    # Generate comparison summary
    successful_results = [r for r in results if r.get("status") == "success"]
    
    comparison_summary = {
        "highest_overall_score": max([r.get("comprehensive_assessment", {}).get("overall_score", 0) for r in successful_results], default=0),
        "lowest_overall_score": min([r.get("comprehensive_assessment", {}).get("overall_score", 100) for r in successful_results], default=0),
        "average_overall_score": sum([r.get("comprehensive_assessment", {}).get("overall_score", 0) for r in successful_results]) / len(successful_results) if successful_results else 0,
        "highest_liquidity": max([r.get("liquidity_analysis", {}).get("total_liquidity_usd", 0) for r in successful_results], default=0),
        "best_profitability": max([r.get("economic_analysis", {}).get("profitability_score", 0) for r in successful_results], default=0),
        "recommended_pool": None
    }
    
    # Find recommended pool (highest overall score)
    if successful_results:
        best_pool = max(successful_results, key=lambda x: x.get("comprehensive_assessment", {}).get("overall_score", 0))
        comparison_summary["recommended_pool"] = best_pool.get("pool_address")
    
    logger.info("Pool comparison completed", {
        "pool_count": len(pool_addresses),
        "successful": len(successful_results),
        "failed": len(results) - len(successful_results)
    })
    
    return {
        "status": "completed",
        "total_pools": len(pool_addresses),
        "comparison_summary": comparison_summary,
        "detailed_results": results
    }

# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def audit_health():
    """
    Health check for audit services.
    
    Returns:
        Health status of all audit services
    """
    return {
        "status": "healthy",
        "services": {
            "token_audit": "operational",
            "pool_audit": "operational"
        },
        "version": "1.0.0",
        "features": [
            "comprehensive_token_audit",
            "comprehensive_pool_audit",
            "security_analysis",
            "liquidity_analysis",
            "economic_analysis",
            "comparative_analysis",
            "detailed_recommendations"
        ]
    } 