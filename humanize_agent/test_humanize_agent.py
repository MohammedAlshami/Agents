#!/usr/bin/env python3
"""
Test script for Humanize Agent API
Tests the text humanization functionality
"""

import requests
import json
import time
from datetime import datetime

# Base URL for the humanize agent
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/humanize/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🔍 Testing Root Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_api_info():
    """Test the API info endpoint"""
    print("\n🔍 Testing API Info Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API info failed: {e}")
        return False

def test_text_humanization():
    """Test the text humanization endpoint"""
    print("\n🔍 Testing Text Humanization...")
    
    test_texts = [
        {
            "text": "Furthermore, the results indicate that the hypothesis was supported by the data analysis.",
            "description": "Academic writing with 'Furthermore'"
        },
        {
            "text": "Moreover, it is important to note that the findings demonstrate significant correlation.",
            "description": "Academic writing with 'Moreover'"
        },
        {
            "text": "In conclusion, the research provides evidence for the proposed theoretical framework.",
            "description": "Academic writing with 'In conclusion'"
        },
        {
            "text": "The system processes the data through multiple algorithms to generate accurate results.",
            "description": "Technical writing"
        },
        {
            "text": "The implementation utilizes advanced machine learning techniques for optimization.",
            "description": "Technical implementation description"
        }
    ]
    
    passed = 0
    total = len(test_texts)
    
    for i, test_case in enumerate(test_texts, 1):
        print(f"\n--- Test {i}: {test_case['description']} ---")
        print(f"Original: '{test_case['text']}'")
        
        try:
            payload = {
                "text": test_case['text'],
                "session_id": f"test_session_{i}",
                "api_key": None
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/humanize/",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                humanized_text = response_data.get('humanized_text', '')
                execution_time = response_data.get('execution_time', 0)
                success = response_data.get('success', False)
                
                print(f"Humanized: '{humanized_text}'")
                print(f"Execution time: {execution_time:.2f}s")
                print(f"Success: {success}")
                
                if success and humanized_text and humanized_text != test_case['text']:
                    print("✅ PASSED - Text was humanized")
                    passed += 1
                else:
                    print("❌ FAILED - Text was not properly humanized")
            else:
                print(f"❌ FAILED - HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ FAILED - Exception: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    print(f"\n📊 Text Humanization Results: {passed}/{total} tests passed")
    return passed == total

def test_error_handling():
    """Test error handling"""
    print("\n🔍 Testing Error Handling...")
    
    # Test with missing text
    print("\n--- Test: Missing text ---")
    try:
        payload = {"session_id": "test_error"}
        response = requests.post(
            f"{BASE_URL}/api/v1/humanize/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("✅ PASSED - Returns 400 for missing text")
            return True
        else:
            print(f"❌ FAILED - Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAILED - Exception: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Humanize Agent Tests")
    print(f"Testing against: {BASE_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("API Info", test_api_info),
        ("Text Humanization", test_text_humanization),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 HUMANIZE AGENT TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Humanize agent is working correctly.")
        print("\n✨ Features tested:")
        print("  • Health check endpoint")
        print("  • Root endpoint")
        print("  • API info endpoint")
        print("  • Text humanization functionality")
        print("  • Error handling")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
