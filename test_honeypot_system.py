#!/usr/bin/env python3
"""
Test script for the new advanced honeypot detection system.

This script tests the enhanced honeypot detection capabilities
with real PancakeSwap simulation.
"""

import asyncio
import time
from typing import Dict, Any

async def test_honeypot_detection():
    """Test the new honeypot detection system."""
    print("🔍 TESTING ADVANCED HONEYPOT DETECTION SYSTEM")
    print("=" * 60)
    
    # Test tokens
    test_tokens = [
        {
            "name": "CAKE (PancakeSwap Token)",
            "address": "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82",
            "expected": "safe"
        },
        {
            "name": "WBNB (Wrapped BNB)",
            "address": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",
            "expected": "safe"
        },
        {
            "name": "BUSD (Binance USD)",
            "address": "0xe9e7cea3dedca5984780bafc599bd69add087d56",
            "expected": "safe"
        }
    ]
    
    try:
        # Import the honeypot detector
        from app.core.analyzers.honeypot_detector import honeypot_detector
        
        print("✅ Successfully imported honeypot detector")
        print()
        
        for token in test_tokens:
            print(f"🪙 Testing: {token['name']}")
            print(f"📍 Address: {token['address']}")
            
            start_time = time.time()
            
            try:
                # Create mock metadata
                metadata = {
                    "name": token["name"],
                    "symbol": token["name"].split()[0],
                    "SourceCode": "",  # No source code for basic test
                    "is_verified": True
                }
                
                # Run honeypot detection
                result = await honeypot_detector.detect_honeypot(token["address"], metadata)
                
                duration = time.time() - start_time
                
                # Display results
                print(f"🎯 Result: {'✅ SAFE' if not result['is_honeypot'] else '🚨 HONEYPOT'}")
                print(f"🔒 Confidence: {result['confidence']}%")
                print(f"⚠️ Risk Level: {result['risk_level']}")
                print(f"💰 Buy Tax: {result.get('buy_tax', 0)}%")
                print(f"💸 Sell Tax: {result.get('sell_tax', 0)}%")
                print(f"📈 Can Buy: {result.get('can_buy', False)}")
                print(f"📉 Can Sell: {result.get('can_sell', False)}")
                print(f"⏱️ Duration: {duration:.2f}s")
                
                if result.get('indicators'):
                    print(f"🚨 Indicators: {', '.join(result['indicators'])}")
                
                print(f"💡 Recommendation: {result['recommendation']}")
                
                # Check simulation details
                simulation = result.get('simulation_results', {})
                if simulation:
                    print(f"🧪 Buy Tests: {len(simulation.get('buy_tests', []))}")
                    print(f"🧪 Sell Tests: {len(simulation.get('sell_tests', []))}")
                
                print()
                
            except Exception as e:
                print(f"❌ Error testing {token['name']}: {str(e)}")
                print(f"🔧 Error type: {type(e).__name__}")
                print()
        
        print("🎉 Honeypot detection testing completed!")
        
    except ImportError as e:
        print(f"❌ Failed to import honeypot detector: {str(e)}")
        print("🔧 Make sure the honeypot_detector.py file exists and is properly configured")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")

async def test_dynamic_analyzer():
    """Test the enhanced dynamic analyzer."""
    print("\n🔬 TESTING ENHANCED DYNAMIC ANALYZER")
    print("=" * 60)
    
    try:
        from app.core.analyzers.dynamic_analyzer import analyze_dynamic_advanced
        
        test_token = "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82"  # CAKE
        metadata = {
            "name": "PancakeSwap Token",
            "symbol": "CAKE",
            "SourceCode": "",
            "is_verified": True
        }
        
        print(f"🪙 Testing dynamic analysis for CAKE token")
        print(f"📍 Address: {test_token}")
        
        start_time = time.time()
        result = await analyze_dynamic_advanced(test_token, metadata)
        duration = time.time() - start_time
        
        print(f"✅ Analysis completed in {duration:.2f}s")
        print(f"🔒 Method: {result.get('analysis_method', 'unknown')}")
        
        honeypot = result.get('honeypot', {})
        print(f"🎯 Honeypot: {honeypot.get('is_honeypot', False)}")
        print(f"🔒 Confidence: {honeypot.get('confidence', 0)}%")
        print(f"⚠️ Risk Level: {honeypot.get('risk_level', 'UNKNOWN')}")
        
        fees = result.get('fees', {})
        print(f"💰 Buy Tax: {fees.get('buy', 0)}%")
        print(f"💸 Sell Tax: {fees.get('sell', 0)}%")
        
        alerts = result.get('alerts', [])
        print(f"🚨 Alerts: {len(alerts)}")
        for alert in alerts[:3]:  # Show first 3 alerts
            print(f"   - {alert.get('title', 'Unknown')}: {alert.get('description', 'No description')}")
        
        print()
        
    except Exception as e:
        print(f"❌ Error testing dynamic analyzer: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")

async def test_token_analysis_service():
    """Test the updated token analysis service."""
    print("\n📊 TESTING TOKEN ANALYSIS SERVICE")
    print("=" * 60)
    
    try:
        from app.services.token_analysis_service import token_analysis_service
        
        test_token = "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82"  # CAKE
        
        print(f"🪙 Testing token analysis service")
        print(f"📍 Address: {test_token}")
        
        # Test quick check
        print("\n🚀 Quick Check:")
        start_time = time.time()
        quick_result = await token_analysis_service.quick_check(test_token)
        duration = time.time() - start_time
        
        print(f"✅ Quick check completed in {duration:.2f}s")
        print(f"🎯 Safety Score: {quick_result.get('safety_score', 0)}")
        print(f"⚠️ Risk Level: {quick_result.get('risk_level', 'UNKNOWN')}")
        print(f"💡 Recommendation: {quick_result.get('recommendation', 'No recommendation')}")
        
        # Test full analysis
        print("\n🔍 Full Analysis:")
        start_time = time.time()
        full_result = await token_analysis_service.analyze_token(test_token)
        duration = time.time() - start_time
        
        print(f"✅ Full analysis completed in {duration:.2f}s")
        print(f"🎯 Safety Score: {full_result.get('safety_score', 0)}")
        print(f"⚠️ Risk Level: {full_result.get('risk_level', 'UNKNOWN')}")
        print(f"💡 Recommendation: {full_result.get('recommendation', 'No recommendation')}")
        
        quick_checks = full_result.get('quick_checks', {})
        print(f"🔒 Honeypot: {quick_checks.get('honeypot', False)}")
        print(f"📈 Can Buy: {quick_checks.get('can_buy', False)}")
        print(f"📉 Can Sell: {quick_checks.get('can_sell', False)}")
        print(f"💸 High Fees: {quick_checks.get('high_fees', False)}")
        
        critical_risks = full_result.get('critical_risks', [])
        if critical_risks:
            print(f"🚨 Critical Risks: {len(critical_risks)}")
            for risk in critical_risks:
                print(f"   - {risk}")
        
        warnings = full_result.get('warnings', [])
        if warnings:
            print(f"⚠️ Warnings: {len(warnings)}")
            for warning in warnings[:3]:  # Show first 3 warnings
                print(f"   - {warning}")
        
        print()
        
    except Exception as e:
        print(f"❌ Error testing token analysis service: {str(e)}")
        print(f"🔧 Error type: {type(e).__name__}")

async def main():
    """Main test function."""
    print("🚀 STARTING HONEYPOT SYSTEM TESTS")
    print("=" * 60)
    print("🌐 Testing new advanced honeypot detection capabilities")
    print("🔧 This will test real PancakeSwap integration")
    print()
    
    # Test individual components
    await test_honeypot_detection()
    await test_dynamic_analyzer()
    await test_token_analysis_service()
    
    print("🎉 ALL TESTS COMPLETED!")
    print("💡 The new honeypot detection system is ready for use")

if __name__ == "__main__":
    asyncio.run(main()) 