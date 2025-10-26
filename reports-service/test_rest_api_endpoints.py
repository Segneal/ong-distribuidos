#!/usr/bin/env python3
"""
Comprehensive test script for REST API endpoints functionality.
This script tests all aspects of the REST API as specified in task 1.2.
"""
import sys
import os
import json
import requests
from typing import Dict, Any, List

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configuration
BASE_URL = "http://localhost:8002"  # Reports service port
TEST_ORG_IDS = [5, 6, 8, 10]

def get_auth_token() -> str:
    """
    Get authentication token for testing.
    This is a placeholder - in real testing you'd get a valid JWT token.
    """
    # For testing purposes, we'll use a mock token
    # In real implementation, you'd authenticate with valid credentials
    return "mock_jwt_token_for_testing"

def test_post_consultation_endpoint():
    """Test POST /api/network/consultation endpoint."""
    print("📡 Testing POST /api/network/consultation endpoint...")
    
    # Test valid request
    print("   Testing valid request...")
    valid_payload = {
        "organization_ids": TEST_ORG_IDS
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_auth_token()}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/network/consultation",
            json=valid_payload,
            headers=headers,
            timeout=30
        )
        
        print(f"     Status Code: {response.status_code}")
        print(f"     Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"     Presidents found: {data.get('total_presidents', 0)}")
            print(f"     Organizations found: {data.get('total_organizations', 0)}")
            print(f"     Errors: {len(data.get('errors', []))}")
            print("     ✅ Valid request successful")
        else:
            print(f"     ❌ Valid request failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Request failed: {e}")
        return False
    
    # Test input validation - empty organization IDs
    print("   Testing empty organization IDs validation...")
    empty_payload = {"organization_ids": []}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/network/consultation",
            json=empty_payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 400:
            print("     ✅ Empty IDs validation working")
        else:
            print(f"     ❌ Empty IDs validation failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Empty IDs test failed: {e}")
        return False
    
    # Test input validation - too many organization IDs
    print("   Testing maximum IDs limit validation...")
    large_payload = {"organization_ids": list(range(1, 52))}  # 51 IDs
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/network/consultation",
            json=large_payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 400:
            print("     ✅ Maximum IDs limit validation working")
        else:
            print(f"     ❌ Maximum IDs limit validation failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Maximum IDs test failed: {e}")
        return False
    
    # Test input validation - invalid organization IDs
    print("   Testing invalid organization IDs validation...")
    invalid_payload = {"organization_ids": [1, -5, 0, "invalid"]}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/network/consultation",
            json=invalid_payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 400 or response.status_code == 422:
            print("     ✅ Invalid IDs validation working")
        else:
            print(f"     ❌ Invalid IDs validation failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Invalid IDs test failed: {e}")
        return False
    
    return True

def test_get_president_endpoint():
    """Test GET /api/network/presidents/{organization_id} endpoint."""
    print("\n👤 Testing GET /api/network/presidents/{organization_id} endpoint...")
    
    headers = {
        "Authorization": f"Bearer {get_auth_token()}"
    }
    
    # Test valid organization ID
    test_org_id = TEST_ORG_IDS[0]
    print(f"   Testing valid organization ID: {test_org_id}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/network/presidents/{test_org_id}",
            headers=headers,
            timeout=30
        )
        
        print(f"     Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"     President Name: {data.get('president_name', 'N/A')}")
            print(f"     Organization ID: {data.get('organization_id', 'N/A')}")
            print("     ✅ Valid president query successful")
        elif response.status_code == 404:
            print("     ⚠️  No president found (might be expected)")
        else:
            print(f"     ❌ Valid president query failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ President query failed: {e}")
        return False
    
    # Test invalid organization ID
    print("   Testing invalid organization ID...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/network/presidents/-1",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 400:
            print("     ✅ Invalid ID validation working")
        else:
            print(f"     ❌ Invalid ID validation failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Invalid ID test failed: {e}")
        return False
    
    return True

def test_get_organization_endpoint():
    """Test GET /api/network/organizations/{organization_id} endpoint."""
    print("\n🏢 Testing GET /api/network/organizations/{organization_id} endpoint...")
    
    headers = {
        "Authorization": f"Bearer {get_auth_token()}"
    }
    
    # Test valid organization ID
    test_org_id = TEST_ORG_IDS[0]
    print(f"   Testing valid organization ID: {test_org_id}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/network/organizations/{test_org_id}",
            headers=headers,
            timeout=30
        )
        
        print(f"     Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"     Organization Name: {data.get('organization_name', 'N/A')}")
            print(f"     Organization ID: {data.get('organization_id', 'N/A')}")
            print("     ✅ Valid organization query successful")
        elif response.status_code == 404:
            print("     ⚠️  No organization found (might be expected)")
        else:
            print(f"     ❌ Valid organization query failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Organization query failed: {e}")
        return False
    
    # Test invalid organization ID
    print("   Testing invalid organization ID...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/network/organizations/0",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 400:
            print("     ✅ Invalid ID validation working")
        else:
            print(f"     ❌ Invalid ID validation failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Invalid ID test failed: {e}")
        return False
    
    return True

def test_connection_test_endpoint():
    """Test GET /api/network/test-connection endpoint."""
    print("\n🔍 Testing GET /api/network/test-connection endpoint...")
    
    headers = {
        "Authorization": f"Bearer {get_auth_token()}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/network/test-connection",
            headers=headers,
            timeout=30
        )
        
        print(f"     Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"     Connected: {data.get('connected', False)}")
            print(f"     Service URL: {data.get('service_url', 'N/A')}")
            print(f"     Message: {data.get('message', 'N/A')}")
            print("     ✅ Connection test endpoint working")
            return True
        else:
            print(f"     ❌ Connection test failed: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Connection test failed: {e}")
        return False

def test_error_handling():
    """Test error handling scenarios."""
    print("\n⚠️  Testing error handling scenarios...")
    
    headers = {
        "Authorization": f"Bearer {get_auth_token()}"
    }
    
    # Test malformed JSON
    print("   Testing malformed JSON...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/network/consultation",
            data="invalid json",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {get_auth_token()}"},
            timeout=30
        )
        
        if response.status_code == 422 or response.status_code == 400:
            print("     ✅ Malformed JSON handling working")
        else:
            print(f"     ❌ Malformed JSON handling failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Malformed JSON test failed: {e}")
        return False
    
    # Test missing authorization
    print("   Testing missing authorization...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/network/consultation",
            json={"organization_ids": [1]},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 401:
            print("     ✅ Missing authorization handling working")
        else:
            print(f"     ❌ Missing authorization handling failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Missing authorization test failed: {e}")
        return False
    
    return True

def test_server_availability():
    """Test if the server is running and accessible."""
    print("🌐 Testing server availability...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=10)
        
        if response.status_code == 200:
            print("   ✅ Server is running and accessible")
            return True
        else:
            print(f"   ❌ Server responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Server is not accessible: {e}")
        print("   💡 Make sure the reports service is running on the expected port")
        return False

def main():
    """Run all REST API endpoint tests."""
    print("🧪 REST API Endpoints Functionality Test Suite")
    print("=" * 60)
    
    # First check if server is available
    if not test_server_availability():
        print("\n❌ Cannot proceed with tests - server is not available")
        print("💡 Please start the reports service and try again")
        return False
    
    tests = [
        ("POST /api/network/consultation", test_post_consultation_endpoint),
        ("GET /api/network/presidents/{id}", test_get_president_endpoint),
        ("GET /api/network/organizations/{id}", test_get_organization_endpoint),
        ("GET /api/network/test-connection", test_connection_test_endpoint),
        ("Error Handling", test_error_handling)
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
        print("🎉 All REST API endpoint tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        print("💡 Note: Some failures might be expected if authentication is not properly configured")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)