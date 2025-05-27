#!/usr/bin/env python3
"""
Clean API Test Script for BNBGuard v2.0.0

This script tests the new clean architecture without legacy routes.
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

class BNBGuardTester:
    """Test class for BNBGuard clean API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.test_results = []
        
        # Test data
        self.test_token = "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82"  # CAKE
        self.test_pool = "0x0ed7e52944161450477ee417de9cd3a859b14fd0"   # CAKE-WBNB
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Test a single endpoint."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    result = await response.json()
                    status_code = response.status
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    result = await response.json()
                    status_code = response.status
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            duration = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "status_code": status_code,
                "duration_ms": round(duration, 2),
                "response": result,
                "endpoint": endpoint,
                "method": method.upper()
            }
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return {
                "success": False,
                "status_code": 0,
                "duration_ms": round(duration, 2),
                "error": str(e),
                "endpoint": endpoint,
                "method": method.upper()
            }
    
    def print_test_result(self, test_name: str, result: Dict[str, Any]):
        """Print formatted test result."""
        if result["success"] and result["status_code"] == 200:
            status_icon = "✅"
            status_text = f"Status: {result['status_code']}"
        else:
            status_icon = "❌"
            status_text = f"Status: {result.get('status_code', 'ERROR')}"
        
        print(f"{status_icon} {test_name}")
        print(f"   📊 {status_text} | ⏱️  {result['duration_ms']}ms")
        
        # Print additional info for successful responses
        if result["success"] and "response" in result:
            response = result["response"]
            if "safety_score" in response:
                print(f"   🛡️  Safety Score: {response['safety_score']}")
            if "risk_level" in response:
                print(f"   ⚠️  Risk Level: {response['risk_level']}")
            if "overall_score" in response.get("comprehensive_assessment", {}):
                print(f"   📈 Overall Score: {response['comprehensive_assessment']['overall_score']}")
        
        print()
    
    async def test_analysis_routes(self):
        """Test all analysis routes."""
        print("🔍 TESTING ANALYSIS ROUTES")
        print("=" * 50)
        
        # Token analysis
        print("🪙 TOKEN ANALYSIS")
        
        # Simple token analysis
        result = await self.test_endpoint("GET", f"/api/v1/analysis/tokens/{self.test_token}")
        self.test_results.append(("Token Analysis", result))
        self.print_test_result("Simple Token Analysis", result)
        
        # Quick token check
        result = await self.test_endpoint("GET", f"/api/v1/analysis/tokens/{self.test_token}/quick")
        self.test_results.append(("Token Quick Check", result))
        self.print_test_result("Quick Token Check", result)
        
        # Batch token analysis
        batch_data = [self.test_token, "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c"]
        result = await self.test_endpoint("POST", "/api/v1/analysis/tokens/batch", batch_data)
        self.test_results.append(("Token Batch", result))
        self.print_test_result("Batch Token Analysis", result)
        
        # Pool analysis
        print("🏊 POOL ANALYSIS")
        
        # Simple pool analysis
        result = await self.test_endpoint("GET", f"/api/v1/analysis/pools/{self.test_pool}")
        self.test_results.append(("Pool Analysis", result))
        self.print_test_result("Simple Pool Analysis", result)
        
        # Quick pool check
        result = await self.test_endpoint("GET", f"/api/v1/analysis/pools/{self.test_pool}/quick")
        self.test_results.append(("Pool Quick Check", result))
        self.print_test_result("Quick Pool Check", result)
        
        # Health check
        result = await self.test_endpoint("GET", "/api/v1/analysis/health")
        self.test_results.append(("Analysis Health", result))
        self.print_test_result("Analysis Health Check", result)
    
    async def test_audit_routes(self):
        """Test all audit routes."""
        print("🔬 TESTING AUDIT ROUTES")
        print("=" * 50)
        
        # Token audits
        print("🪙 TOKEN AUDITS")
        
        # Comprehensive token audit
        result = await self.test_endpoint("GET", f"/api/v1/audits/tokens/{self.test_token}")
        self.test_results.append(("Token Audit", result))
        self.print_test_result("Comprehensive Token Audit", result)
        
        # Security audit
        result = await self.test_endpoint("GET", f"/api/v1/audits/tokens/{self.test_token}/security")
        self.test_results.append(("Token Security", result))
        self.print_test_result("Security Audit", result)
        
        # Recommendations
        result = await self.test_endpoint("GET", f"/api/v1/audits/tokens/{self.test_token}/recommendations")
        self.test_results.append(("Token Recommendations", result))
        self.print_test_result("Token Recommendations", result)
        
        # Pool audits
        print("🏊 POOL AUDITS")
        
        # Comprehensive pool audit
        result = await self.test_endpoint("GET", f"/api/v1/audits/pools/{self.test_pool}")
        self.test_results.append(("Pool Audit", result))
        self.print_test_result("Comprehensive Pool Audit", result)
        
        # Liquidity audit
        result = await self.test_endpoint("GET", f"/api/v1/audits/pools/{self.test_pool}/liquidity")
        self.test_results.append(("Pool Liquidity", result))
        self.print_test_result("Liquidity Audit", result)
        
        # Economic audit
        result = await self.test_endpoint("GET", f"/api/v1/audits/pools/{self.test_pool}/economics")
        self.test_results.append(("Pool Economics", result))
        self.print_test_result("Economic Audit", result)
        
        # Health check
        result = await self.test_endpoint("GET", "/api/v1/audits/health")
        self.test_results.append(("Audit Health", result))
        self.print_test_result("Audit Health Check", result)
    
    async def test_root_endpoint(self):
        """Test root endpoint."""
        print("🏠 TESTING ROOT ENDPOINT")
        print("=" * 50)
        
        result = await self.test_endpoint("GET", "/")
        self.test_results.append(("Root", result))
        self.print_test_result("Root Endpoint", result)
    
    def generate_summary(self):
        """Generate test summary."""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for _, result in self.test_results if result["success"] and result["status_code"] == 200)
        
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Successful tests: {successful_tests}")
        print(f"❌ Failed tests: {total_tests - successful_tests}")
        print(f"📈 Success rate: {(successful_tests / total_tests * 100):.1f}%")
        
        if successful_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Clean API is working perfectly!")
        else:
            print("⚠️ Some tests failed. Check the results above.")
        
        return successful_tests == total_tests

async def main():
    """Main test function."""
    print("🚀 STARTING CLEAN API TESTS - BNBGuard v2.0.0")
    print("=" * 60)
    print("🌐 Base URL: http://localhost:8000")
    print()
    
    async with BNBGuardTester() as tester:
        # Test root endpoint
        await tester.test_root_endpoint()
        
        # Test analysis routes
        await tester.test_analysis_routes()
        
        # Test audit routes
        await tester.test_audit_routes()
        
        # Generate summary
        all_passed = tester.generate_summary()
        
        if all_passed:
            print("\n💾 Clean API is ready for production!")
        else:
            print("\n🔧 Some issues need to be addressed.")

if __name__ == "__main__":
    asyncio.run(main()) 