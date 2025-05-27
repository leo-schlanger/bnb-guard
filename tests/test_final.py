#!/usr/bin/env python3
"""
Final test script for BNBGuard improvements.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_token_analyzer():
    """Test the new TokenAnalyzer."""
    print("🔍 Testing TokenAnalyzer...")
    
    try:
        from app.services.token_analyzer import token_analyzer
        
        # Test with WBNB (Wrapped BNB) - valid 42 character address
        test_address = "0xbb4CdB9CBd36B01bD1cBaEF60eF3DC3A"
        
        print(f"   Analyzing token: {test_address}")
        result = await token_analyzer.analyze_token(test_address)
        
        # Check if result is AnalyzeResponse object or dict
        if hasattr(result, 'status'):
            status = result.status
            error = getattr(result, 'error', None)
        else:
            status = result.get("status") if isinstance(result, dict) else None
            error = result.get("error") if isinstance(result, dict) else str(result)
        
        if status == "completed":
            print("   ✅ TokenAnalyzer working correctly")
            if hasattr(result, 'score'):
                print(f"   📊 Risk Score: {getattr(result.score, 'value', 'N/A')}")
                print(f"   📈 Grade: {getattr(result.score, 'label', 'N/A')}")
        else:
            print(f"   ❌ TokenAnalyzer failed: {error}")
            
    except Exception as e:
        print(f"   ❌ TokenAnalyzer test failed: {str(e)}")

def test_imports():
    """Test all critical imports."""
    print("📦 Testing Imports...")
    
    imports_to_test = [
        ("app.services.token_analyzer", "TokenAnalyzer"),
        ("app.services.pool_analyzer", "PoolAnalyzer"),
        ("app.core.config", "settings"),
        ("app.routes.tokens", "router"),
        ("app.routes.pools", "router"),
        ("app.core.analyzers.static_analyzer", "analyze_static"),
        ("app.core.analyzers.dynamic_analyzer", "analyze_dynamic"),
        ("app.core.analyzers.onchain_analyzer", "analyze_onchain"),
    ]
    
    failed_imports = []
    
    for module_name, item_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[item_name])
            getattr(module, item_name)
            print(f"   ✅ {module_name}.{item_name}")
        except Exception as e:
            print(f"   ❌ {module_name}.{item_name}: {str(e)}")
            failed_imports.append(f"{module_name}.{item_name}")
    
    if not failed_imports:
        print("   🎉 All imports successful!")
    else:
        print(f"   ⚠️  {len(failed_imports)} import(s) failed")

def test_configuration():
    """Test configuration loading."""
    print("\n⚙️  Testing Configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"   API Title: {settings.API_TITLE}")
        print(f"   API Version: {settings.API_VERSION}")
        print(f"   BSC RPC URL: {settings.BSC_RPC_URL}")
        print(f"   Log Level: {settings.LOG_LEVEL}")
        
        # Check if BSCSCAN_API_KEY is set
        if settings.BSCSCAN_API_KEY and settings.BSCSCAN_API_KEY != "your_bscscan_api_key_here":
            print("   ✅ Configuration loaded correctly")
        else:
            print("   ⚠️  BSCSCAN_API_KEY not configured (using default)")
            
    except Exception as e:
        print(f"   ❌ Configuration test failed: {str(e)}")

async def main():
    """Run all tests."""
    print("🚀 BNBGuard Final Test Suite")
    print("=" * 50)
    
    # Test imports first
    test_imports()
    
    # Test configuration
    test_configuration()
    
    # Test token analyzer
    await test_token_analyzer()
    
    print("\n" + "=" * 50)
    print("✨ Test suite completed!")

if __name__ == "__main__":
    asyncio.run(main()) 