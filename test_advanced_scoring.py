#!/usr/bin/env python3
"""
Test script for the new advanced scoring system.

This script tests the enhanced multi-dimensional risk scoring
with detailed category analysis and confidence levels.
"""

import asyncio
import time
from typing import Dict, Any

async def test_advanced_scoring():
    """Test the new advanced scoring system."""
    print("🎯 TESTING ADVANCED SCORING SYSTEM")
    print("=" * 60)
    
    try:
        from app.core.utils.advanced_scoring import advanced_scorer
        
        print("✅ Successfully imported advanced scorer")
        print()
        
        # Test scenarios with different risk profiles
        test_scenarios = [
            {
                "name": "Safe Token (CAKE-like)",
                "static_analysis": {
                    "is_verified": True,
                    "dangerous_functions_found": [],
                    "owner": {"renounced": True, "address": "0x000...000"},
                    "has_mint": False,
                    "has_pause": False,
                    "has_blacklist": False
                },
                "dynamic_analysis": {
                    "honeypot_analysis": {
                        "is_honeypot": False,
                        "confidence": 5,
                        "can_buy": True,
                        "can_sell": True,
                        "indicators": [],
                        "recommendation": "✅ LOW RISK - No significant honeypot indicators found"
                    },
                    "fee_analysis": {
                        "buy_tax": 0.0,
                        "sell_tax": 0.0
                    },
                    "analysis_method": "advanced_honeypot_detection"
                },
                "onchain_analysis": {
                    "lp_info": {"locked": True, "percent_locked": 100},
                    "holders": {"top_holder_percent": 15}
                },
                "expected_grade": "A"
            },
            {
                "name": "Risky Token (High Fees)",
                "static_analysis": {
                    "is_verified": True,
                    "dangerous_functions_found": [],
                    "owner": {"renounced": False, "address": "0x123...456"},
                    "has_mint": True,
                    "has_pause": False,
                    "has_blacklist": False
                },
                "dynamic_analysis": {
                    "honeypot_analysis": {
                        "is_honeypot": False,
                        "confidence": 10,
                        "can_buy": True,
                        "can_sell": True,
                        "indicators": [],
                        "recommendation": "✅ LOW RISK"
                    },
                    "fee_analysis": {
                        "buy_tax": 15.0,
                        "sell_tax": 18.0
                    },
                    "analysis_method": "advanced_honeypot_detection"
                },
                "onchain_analysis": {
                    "lp_info": {"locked": False, "percent_locked": 0},
                    "holders": {"top_holder_percent": 25}
                },
                "expected_grade": "C"
            },
            {
                "name": "Honeypot Token",
                "static_analysis": {
                    "is_verified": False,
                    "dangerous_functions_found": [
                        {"name": "transfer", "severity": "high", "message": "Suspicious transfer function"}
                    ],
                    "owner": {"renounced": False, "address": "0x999...999"},
                    "has_mint": True,
                    "has_pause": True,
                    "has_blacklist": True
                },
                "dynamic_analysis": {
                    "honeypot_analysis": {
                        "is_honeypot": True,
                        "confidence": 85,
                        "can_buy": True,
                        "can_sell": False,
                        "indicators": ["Cannot sell after buying", "Suspicious code patterns"],
                        "recommendation": "🚨 AVOID - High probability honeypot detected"
                    },
                    "fee_analysis": {
                        "buy_tax": 5.0,
                        "sell_tax": 99.0
                    },
                    "analysis_method": "advanced_honeypot_detection"
                },
                "onchain_analysis": {
                    "lp_info": {"locked": False, "percent_locked": 0},
                    "holders": {"top_holder_percent": 80}
                },
                "expected_grade": "F"
            },
            {
                "name": "Moderate Risk Token",
                "static_analysis": {
                    "is_verified": True,
                    "dangerous_functions_found": [],
                    "owner": {"renounced": False, "address": "0x456...789"},
                    "has_mint": False,
                    "has_pause": False,
                    "has_blacklist": True
                },
                "dynamic_analysis": {
                    "honeypot_analysis": {
                        "is_honeypot": False,
                        "confidence": 20,
                        "can_buy": True,
                        "can_sell": True,
                        "indicators": ["Some suspicious patterns"],
                        "recommendation": "⚡ MODERATE RISK"
                    },
                    "fee_analysis": {
                        "buy_tax": 8.0,
                        "sell_tax": 12.0
                    },
                    "analysis_method": "advanced_honeypot_detection"
                },
                "onchain_analysis": {
                    "lp_info": {"locked": True, "percent_locked": 70},
                    "holders": {"top_holder_percent": 30}
                },
                "expected_grade": "B"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"🧪 Test {i}: {scenario['name']}")
            print("-" * 40)
            
            start_time = time.time()
            
            try:
                # Run advanced scoring
                breakdown = advanced_scorer.calculate_comprehensive_score(
                    scenario["static_analysis"],
                    scenario["dynamic_analysis"], 
                    scenario["onchain_analysis"]
                )
                
                duration = time.time() - start_time
                
                # Display results
                print(f"📊 Final Score: {breakdown.final_score:.1f}/100")
                print(f"🎓 Grade: {breakdown.grade}")
                print(f"⚠️ Risk Level: {breakdown.risk_level}")
                print(f"🔒 Confidence: {breakdown.confidence_level*100:.1f}%")
                print(f"⏱️ Duration: {duration*1000:.1f}ms")
                
                # Category breakdown
                print(f"\n📈 Category Scores:")
                for category, score in breakdown.category_scores.items():
                    print(f"   {category.title()}: {score:.1f}/100")
                
                # Risk factors
                if breakdown.risk_factors:
                    print(f"\n🚨 Risk Factors ({len(breakdown.risk_factors)}):")
                    for factor in breakdown.risk_factors[:5]:  # Show top 5
                        severity_emoji = {
                            "CRITICAL": "🔴",
                            "HIGH": "🟠", 
                            "MEDIUM": "🟡",
                            "LOW": "🟢",
                            "INFO": "🔵"
                        }.get(factor.severity.name, "⚪")
                        
                        print(f"   {severity_emoji} {factor.title} ({factor.category.value})")
                        print(f"      Impact: -{factor.score_impact:.1f} | Confidence: {factor.confidence*100:.0f}%")
                
                # Validation
                expected = scenario.get("expected_grade", "")
                if expected:
                    status = "✅" if breakdown.grade.startswith(expected[0]) else "⚠️"
                    print(f"\n{status} Expected: {expected} | Got: {breakdown.grade}")
                
                print()
                
            except Exception as e:
                print(f"❌ Error in scenario: {str(e)}")
                print(f"🔧 Error type: {type(e).__name__}")
                print()
        
        print("🎉 Advanced scoring testing completed!")
        
    except ImportError as e:
        print(f"❌ Failed to import advanced scorer: {str(e)}")
        print("🔧 Make sure the advanced_scoring.py file exists and is properly configured")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")

async def test_category_weights():
    """Test category weight distribution."""
    print("\n🏗️ TESTING CATEGORY WEIGHTS")
    print("=" * 60)
    
    try:
        from app.core.utils.advanced_scoring import advanced_scorer
        
        weights = advanced_scorer.category_weights
        total_weight = sum(weight for weight in weights.values())
        
        print("📊 Category Weight Distribution:")
        for category, weight in weights.items():
            percentage = weight * 100
            bar = "█" * int(percentage / 2)
            print(f"   {category.value.title():12} {weight:.2f} ({percentage:4.1f}%) {bar}")
        
        print(f"\n✅ Total Weight: {total_weight:.3f} {'✅' if abs(total_weight - 1.0) < 0.001 else '❌'}")
        
        if abs(total_weight - 1.0) >= 0.001:
            print("⚠️ Warning: Category weights should sum to 1.0")
        
    except Exception as e:
        print(f"❌ Error testing weights: {str(e)}")

async def test_scoring_consistency():
    """Test scoring consistency and edge cases."""
    print("\n🔄 TESTING SCORING CONSISTENCY")
    print("=" * 60)
    
    try:
        from app.core.utils.advanced_scoring import advanced_scorer
        
        # Test empty data
        print("🧪 Testing with empty data...")
        empty_breakdown = advanced_scorer.calculate_comprehensive_score({}, {}, {})
        print(f"   Empty data score: {empty_breakdown.final_score:.1f} (Grade: {empty_breakdown.grade})")
        
        # Test perfect token
        print("\n🧪 Testing perfect token...")
        perfect_static = {
            "is_verified": True,
            "dangerous_functions_found": [],
            "owner": {"renounced": True, "address": "0x000...000"},
            "has_mint": False,
            "has_pause": False,
            "has_blacklist": False
        }
        perfect_dynamic = {
            "honeypot_analysis": {
                "is_honeypot": False,
                "confidence": 0,
                "can_buy": True,
                "can_sell": True,
                "indicators": [],
                "recommendation": "✅ SAFE"
            },
            "fee_analysis": {"buy_tax": 0.0, "sell_tax": 0.0},
            "analysis_method": "advanced_honeypot_detection"
        }
        perfect_onchain = {
            "lp_info": {"locked": True, "percent_locked": 100},
            "holders": {"top_holder_percent": 5}
        }
        
        perfect_breakdown = advanced_scorer.calculate_comprehensive_score(
            perfect_static, perfect_dynamic, perfect_onchain
        )
        print(f"   Perfect token score: {perfect_breakdown.final_score:.1f} (Grade: {perfect_breakdown.grade})")
        
        # Test worst token
        print("\n🧪 Testing worst token...")
        worst_static = {
            "is_verified": False,
            "dangerous_functions_found": [
                {"name": "malicious", "severity": "critical", "message": "Malicious function"}
            ],
            "owner": {"renounced": False, "address": "0x999...999"},
            "has_mint": True,
            "has_pause": True,
            "has_blacklist": True
        }
        worst_dynamic = {
            "honeypot_analysis": {
                "is_honeypot": True,
                "confidence": 95,
                "can_buy": False,
                "can_sell": False,
                "indicators": ["Cannot buy", "Cannot sell", "Malicious code"],
                "recommendation": "🚨 AVOID"
            },
            "fee_analysis": {"buy_tax": 50.0, "sell_tax": 99.0},
            "analysis_method": "advanced_honeypot_detection"
        }
        worst_onchain = {
            "lp_info": {"locked": False, "percent_locked": 0},
            "holders": {"top_holder_percent": 95}
        }
        
        worst_breakdown = advanced_scorer.calculate_comprehensive_score(
            worst_static, worst_dynamic, worst_onchain
        )
        print(f"   Worst token score: {worst_breakdown.final_score:.1f} (Grade: {worst_breakdown.grade})")
        
        print(f"\n📊 Score Range: {worst_breakdown.final_score:.1f} - {perfect_breakdown.final_score:.1f}")
        
    except Exception as e:
        print(f"❌ Error testing consistency: {str(e)}")

async def main():
    """Main test function."""
    print("🚀 STARTING ADVANCED SCORING TESTS")
    print("=" * 60)
    print("🎯 Testing new multi-dimensional risk scoring system")
    print("📊 This will test category weights, risk factors, and scoring accuracy")
    print()
    
    # Test individual components
    await test_advanced_scoring()
    await test_category_weights()
    await test_scoring_consistency()
    
    print("🎉 ALL ADVANCED SCORING TESTS COMPLETED!")
    print("💡 The new scoring system provides more accurate and detailed risk assessment")

if __name__ == "__main__":
    asyncio.run(main()) 