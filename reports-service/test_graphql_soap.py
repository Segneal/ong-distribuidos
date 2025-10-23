#!/usr/bin/env python3
"""
Test GraphQL SOAP queries.
"""
import requests
import json

def test_graphql_soap():
    """Test GraphQL SOAP queries."""
    base_url = "http://localhost:8001/api/graphql"
    
    print("🧪 Testing GraphQL SOAP queries...")
    
    # Test 1: Connection test
    print("\n1. Testing SOAP connection via GraphQL...")
    query1 = """
    query {
        soapConnectionTest {
            connected
            serviceUrl
            message
        }
    }
    """
    
    response1 = requests.post(base_url, json={"query": query1})
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"   Response: {json.dumps(data1, indent=2)}")
    else:
        print(f"   ❌ Error: {response1.status_code} - {response1.text}")
    
    # Test 2: Network consultation
    print("\n2. Testing network consultation via GraphQL...")
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
    
    response2 = requests.post(base_url, json={"query": query2, "variables": variables2})
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"   Response: {json.dumps(data2, indent=2)}")
    else:
        print(f"   ❌ Error: {response2.status_code} - {response2.text}")
    
    print("\n✅ GraphQL SOAP test completed!")

if __name__ == "__main__":
    test_graphql_soap()