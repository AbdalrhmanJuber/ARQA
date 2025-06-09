#!/usr/bin/env python3
"""
Test Script for ARQA API
Tests all endpoints and validates Phase 4 completion
"""

import requests
import json
import time
import os
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_endpoint(name: str, method: str, url: str, **kwargs) -> Dict[str, Any]:
    """Test an API endpoint and return results"""
    print(f"\n🧪 Testing {name}:")
    print(f"   {method} {url}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, **kwargs)
        elif method.upper() == "POST":
            response = requests.post(url, **kwargs)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Success!")
            try:
                json_data = response.json()
                return {"success": True, "status": response.status_code, "data": json_data}
            except:
                return {"success": True, "status": response.status_code, "data": response.text}
        else:
            print(f"   ❌ Failed: {response.text}")
            return {"success": False, "status": response.status_code, "error": response.text}
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection Error - Server not running?")
        return {"success": False, "error": "Connection failed"}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e)}

def main():
    print("🚀 ARQA API Testing Suite")
    print("=" * 50)
    
    # Test 1: Root endpoint (HTML welcome page)
    result1 = test_endpoint("Welcome Page", "GET", f"{BASE_URL}/")
    
    # Test 2: Status endpoint
    result2 = test_endpoint("System Status", "GET", f"{BASE_URL}/status")
    
    # Test 3: Health check
    result3 = test_endpoint("Health Check", "GET", f"{BASE_URL}/health")
    
    # Test 4: Documents list
    result4 = test_endpoint("Documents List", "GET", f"{BASE_URL}/documents")
    
    # Test 5: Upload document (if we have a test file)
    test_html_file = "test_html_articles/arabic_science.html"
    if os.path.exists(test_html_file):
        print(f"\n🧪 Testing Document Upload with {test_html_file}:")
        try:
            with open(test_html_file, 'rb') as f:
                files = {'file': ('arabic_science.html', f, 'text/html')}
                result5 = test_endpoint("Document Upload", "POST", f"{BASE_URL}/upload", files=files)
        except Exception as e:
            print(f"   ❌ Upload failed: {e}")
            result5 = {"success": False, "error": str(e)}
    else:
        print(f"\n⚠️  Skipping upload test - {test_html_file} not found")
        result5 = {"success": False, "error": "Test file not found"}
    
    # Test 6: Ask question (if upload succeeded or we have existing documents)
    if result5.get("success") or result4.get("data", {}).get("document_count", 0) > 0:
        test_question = {
            "question": "ما هو الذكاء الاصطناعي؟",  # "What is artificial intelligence?"
            "top_k": 3,
            "min_confidence": 0.01
        }
        
        result6 = test_endpoint(
            "Question Answering", 
            "POST", 
            f"{BASE_URL}/ask",
            json=test_question,
            headers={"Content-Type": "application/json"}
        )
    else:
        print(f"\n⚠️  Skipping question test - no documents available")
        result6 = {"success": False, "error": "No documents to query"}
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY:")
    print("=" * 50)
    
    tests = [
        ("Welcome Page", result1),
        ("System Status", result2), 
        ("Health Check", result3),
        ("Documents List", result4),
        ("Document Upload", result5),
        ("Question Answering", result6)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, result in tests:
        status = "✅ PASS" if result.get("success") else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result.get("success"):
            passed += 1
        else:
            failed += 1
            if "error" in result:
                print(f"                     Error: {result['error']}")
    
    print(f"\nTotal: {passed + failed} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Phase 4 API is working correctly!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the issues above.")
    
    return passed, failed

if __name__ == "__main__":
    main()
