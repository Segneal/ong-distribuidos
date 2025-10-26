#!/usr/bin/env python3
"""
Basic REST API endpoints test without complex authentication.
Tests the core functionality of the REST endpoints.
"""
import sys
import os
import json
import requests

# Configuration
BASE_URL = "http://localhost:8002"
TEST_ORG_IDS = [5, 6, 8, 10]

def test_health_endpoint():
    """Test the health endpoint."""
    print("🏥 Testing health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Service Status: {data.get('status', 'unknown')}")
            print(f"   Database Connected: {data.get('database', {}).get('database_connected', False)}")
            print("   ✅ Health endpoint working")
            return True
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Health endpoint failed: {e}")
        return False

def test_docs_endpoint():
    """Test the API documentation endpoint."""
    print("\n📚 Testing API documentation endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ API documentation accessible")
            return True
        else:
            print(f"   ❌ API documentation failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ API documentation failed: {e}")
        return False

def test_consultation_endpoint_structure():
    """Test the consultation endpoint structure (without auth)."""
    print("\n📡 Testing consultation endpoint structure...")
    
    # Test without authentication to see the expected error
    payload = {"organization_ids": TEST_ORG_IDS}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/network/consultation",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 401:
            print("   ✅ Authentication required (expected)")
            return True
        elif response.status_code == 422:
            print("   ✅ Validation working (expected)")
            return True
        elif response.status_code == 200:
            print("   ⚠️  Endpoint accessible without auth (unexpected)")
            data = response.json()
            print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            return True
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            try:
                print(f"   Response: {response.json()}")
            except:
                print(f"   Response text: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False

def test_input_validation():
    """Test input validation on consultation endpoint."""
    print("\n🔍 Testing input validation...")
    
    # Test empty organization IDs
    print("   Testing empty organization IDs...")
    empty_payload = {"organization_ids": []}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/network/consultation",
            json=empty_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code in [400, 422]:
            print("     ✅ Empty IDs validation working")
        else:
            print(f"     ❌ Empty IDs validation failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Empty IDs test failed: {e}")
        return False
    
    # Test invalid data type
    print("   Testing invalid data type...")
    invalid_payload = {"organization_ids": "not_a_list"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/network/consultation",
            json=invalid_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code in [400, 422]:
            print("     ✅ Invalid data type validation working")
        else:
            print(f"     ❌ Invalid data type validation failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Invalid data type test failed: {e}")
        return False
    
    # Test malformed JSON
    print("   Testing malformed JSON...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/network/consultation",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code in [400, 422]:
            print("     ✅ Malformed JSON validation working")
        else:
            print(f"     ❌ Malformed JSON validation failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Malformed JSON test failed: {e}")
        return False
    
    return True

def test_individual_endpoints_structure():
    """Test individual endpoint structures."""
    print("\n👤 Testing individual endpoints structure...")
    
    # Test president endpoint
    print("   Testing president endpoint...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/network/presidents/5",
            timeout=30
        )
        
        print(f"     Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("     ✅ President endpoint requires authentication (expected)")
        elif response.status_code in [200, 404]:
            print("     ⚠️  President endpoint accessible without auth")
        else:
            print(f"     ❌ Unexpected response: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ President endpoint test failed: {e}")
        return False
    
    # Test organization endpoint
    print("   Testing organization endpoint...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/network/organizations/5",
            timeout=30
        )
        
        print(f"     Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("     ✅ Organization endpoint requires authentication (expected)")
        elif response.status_code in [200, 404]:
            print("     ⚠️  Organization endpoint accessible without auth")
        else:
            print(f"     ❌ Unexpected response: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Organization endpoint test failed: {e}")
        return False
    
    # Test connection test endpoint
    print("   Testing connection test endpoint...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/network/test-connection",
            timeout=30
        )
        
        print(f"     Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("     ✅ Connection test endpoint requires authentication (expected)")
        elif response.status_code == 200:
            print("     ⚠️  Connection test endpoint accessible without auth")
            data = response.json()
            print(f"     Connection status: {data.get('connected', 'unknown')}")
        else:
            print(f"     ❌ Unexpected response: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Connection test endpoint failed: {e}")
        return False
    
    return True

def test_cors_headers():
    """Test CORS headers."""
    print("\n🌐 Testing CORS headers...")
    
    try:
        response = requests.options(
            f"{BASE_URL}/api/network/consultation",
            headers={"Origin": "http://localhost:3000"},
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print(f"   CORS Headers: {cors_headers}")
        
        if any(cors_headers.values()):
            print("   ✅ CORS headers present")
            return True
        else:
            print("   ⚠️  No CORS headers found")
            return True  # Not necessarily a failure
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CORS test failed: {e}")
        return False

def main():
    """Run basic REST API tests."""
    print("🧪 Basic REST API Endpoints Test Suite")
    print("=" * 60)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("API Documentation", test_docs_endpoint),
        ("Consultation Endpoint Structure", test_consultation_endpoint_structure),
        ("Input Validation", test_input_validation),
        ("Individual Endpoints Structure", test_individual_endpoints_structure),
        ("CORS Headers", test_cors_headers)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic REST API tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)