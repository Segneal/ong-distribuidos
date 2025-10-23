#!/usr/bin/env python3
"""
Test full integration through API Gateway.
"""
import requests
import json

def test_full_integration():
    """Test GraphQL SOAP queries through API Gateway."""
    base_url = "http://localhost:3001/api/graphql"
    
    print("🧪 Testing Full Integration (API Gateway -> Reports Service)...")
    
    # Note: For this test, we'll need a valid JWT token
    # In a real scenario, you'd get this from login
    headers = {
        'Content-Type': 'application/json',
        # 'Authorization': 'Bearer YOUR_JWT_TOKEN_HERE'  # Uncomment and add real token
    }
    
    # Test 1: Connection test
    print("\n1. Testing SOAP connection via API Gateway...")
    query1 = """
    query {
        soapConnectionTest {
            connected
            serviceUrl
            message
        }
    }
    """
    
    try:
        response1 = requests.post(base_url, json={"query": query1}, headers=headers)
        print(f"   Status: {response1.status_code}")
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"   Response: {json.dumps(data1, indent=2)}")
        else:
            print(f"   Error Response: {response1.text}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    # Test 2: Network consultation (requires PRESIDENTE role)
    print("\n2. Testing network consultation via API Gateway...")
    query2 = """
    query NetworkConsultation($organizationIds: [Int!]!) {
        networkConsultation(organizationIds: $organizationIds) {
            presidents {
                organizationId
                presidentName
                presidentPhone
                presidentAddress
            }
            organizations {
                organizationId
                organizationName
                address
                phone
            }
            totalPresidents
            totalOrganizations
            errors
        }
    }
    """
    
    variables2 = {"organizationIds": [5, 6, 8, 10]}
    
    try:
        response2 = requests.post(base_url, json={"query": query2, "variables": variables2}, headers=headers)
        print(f"   Status: {response2.status_code}")
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"   Response: {json.dumps(data2, indent=2)}")
        else:
            print(f"   Error Response: {response2.text}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    
    print("\n✅ Full integration test completed!")
    print("\n📝 Note: For authentication-protected queries, you'll need to:")
    print("   1. Login through the frontend or API")
    print("   2. Get a valid JWT token")
    print("   3. Add it to the Authorization header")

if __name__ == "__main__":
    test_full_integration()