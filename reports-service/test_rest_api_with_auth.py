#!/usr/bin/env python3
"""
REST API endpoints test with proper authentication.
Tests the full functionality of the REST endpoints with authentication.
"""
import sys
import os
import json
import requests
import jwt
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configuration
BASE_URL = "http://localhost:8002"
TEST_ORG_IDS = [5, 6, 8, 10]

def create_test_jwt_token():
    """Create a test JWT token for a President user."""
    # This should match your JWT configuration
    secret_key = "your-secret-key-here"  # Replace with actual secret
    
    payload = {
        "sub": "test_president@example.com",
        "user_id": 1,
        "role": "President",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    
    try:
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token
    except Exception as e:
        print(f"Error creating JWT token: {e}")
        return None

def test_with_mock_auth():
    """Test endpoints with mock authentication bypass."""
    print("🔐 Testing with authentication bypass...")
    
    # First, let's check if there's a way to bypass auth for testing
    # or if we can create a test user directly in the database
    
    try:
        # Try to access the database directly to create a test user
        from src.models.database import get_database
        from src.models.user import User
        from src.utils.auth import create_access_token
        
        print("   Creating test user in database...")
        
        # This would create a test user - but we need to be careful about database state
        test_user_data = {
            "email": "test_president@example.com",
            "role": "President",
            "name": "Test President",
            "is_active": True
        }
        
        # Create a token for testing
        token = create_access_token(data={"sub": test_user_data["email"], "role": test_user_data["role"]})
        
        print(f"   Generated test token: {token[:50]}...")
        
        return token
        
    except ImportError as e:
        print(f"   ❌ Cannot import auth modules: {e}")
        return None
    except Exception as e:
        print(f"   ❌ Error creating test auth: {e}")
        return None

def test_consultation_endpoint_with_auth(token):
    """Test POST /api/network/consultation with authentication."""
    print("\n📡 Testing POST /api/network/consultation with auth...")
    
    if not token:
        print("   ❌ No authentication token available")
        return False
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Test valid request
    print("   Testing valid request...")
    payload = {"organization_ids": TEST_ORG_IDS}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/network/consultation",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"     Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"     Presidents found: {data.get('total_presidents', 0)}")
            print(f"     Organizations found: {data.get('total_organizations', 0)}")
            print(f"     Query IDs: {data.get('query_ids', [])}")
            print(f"     Errors: {len(data.get('errors', []))}")
            
            # Validate response structure
            required_fields = ['presidents', 'organizations', 'total_presidents', 'total_organizations']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("     ✅ Valid request successful with correct structure")
                return True
            else:
                print(f"     ❌ Missing fields in response: {missing_fields}")
                return False
                
        elif response.status_code == 401:
            print("     ❌ Authentication failed")
            return False
        elif response.status_code == 403:
            print("     ❌ Authorization failed (user might not have President role)")
            return False
        else:
            print(f"     ❌ Unexpected response: {response.status_code}")
            try:
                print(f"     Response: {response.json()}")
            except:
                print(f"     Response text: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Request failed: {e}")
        return False

def test_input_validation_with_auth(token):
    """Test input validation with authentication."""
    print("\n🔍 Testing input validation with auth...")
    
    if not token:
        print("   ❌ No authentication token available")
        return False
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Test empty organization IDs
    print("   Testing empty organization IDs...")
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
    
    # Test too many organization IDs
    print("   Testing maximum IDs limit...")
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
    
    # Test invalid organization IDs
    print("   Testing invalid organization IDs...")
    invalid_payload = {"organization_ids": [1, -5, 0]}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/network/consultation",
            json=invalid_payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 400:
            print("     ✅ Invalid IDs validation working")
        else:
            print(f"     ❌ Invalid IDs validation failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Invalid IDs test failed: {e}")
        return False
    
    return True

def test_individual_endpoints_with_auth(token):
    """Test individual endpoints with authentication."""
    print("\n👤 Testing individual endpoints with auth...")
    
    if not token:
        print("   ❌ No authentication token available")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test president endpoint
    print("   Testing president endpoint...")
    test_org_id = TEST_ORG_IDS[0]
    
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
            print("     ✅ President endpoint working")
        elif response.status_code == 404:
            print("     ⚠️  No president found (might be expected)")
        else:
            print(f"     ❌ President endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ President endpoint test failed: {e}")
        return False
    
    # Test organization endpoint
    print("   Testing organization endpoint...")
    
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
            print("     ✅ Organization endpoint working")
        elif response.status_code == 404:
            print("     ⚠️  No organization found (might be expected)")
        else:
            print(f"     ❌ Organization endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Organization endpoint test failed: {e}")
        return False
    
    # Test connection test endpoint
    print("   Testing connection test endpoint...")
    
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
            print("     ✅ Connection test endpoint working")
        else:
            print(f"     ❌ Connection test endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Connection test endpoint failed: {e}")
        return False
    
    return True

def main():
    """Run REST API tests with authentication."""
    print("🧪 REST API Endpoints Test Suite (With Authentication)")
    print("=" * 60)
    
    # Try to get authentication token
    print("🔐 Setting up authentication...")
    token = test_with_mock_auth()
    
    if not token:
        print("❌ Could not set up authentication. Testing basic structure only.")
        print("💡 This is expected if authentication system is not fully configured.")
        
        # Run basic structure tests
        from test_rest_api_basic import main as basic_main
        return basic_main()
    
    tests = [
        ("Consultation Endpoint with Auth", lambda: test_consultation_endpoint_with_auth(token)),
        ("Input Validation with Auth", lambda: test_input_validation_with_auth(token)),
        ("Individual Endpoints with Auth", lambda: test_individual_endpoints_with_auth(token))
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
        print("🎉 All REST API tests with authentication passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)