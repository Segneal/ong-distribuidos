#!/usr/bin/env python3
"""
Comprehensive test script for GraphQL integration and queries.
This script tests all aspects of the GraphQL integration as specified in task 1.3.
"""
import sys
import os
import json
import requests
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:8002"
GRAPHQL_ENDPOINT = f"{BASE_URL}/api/graphql"
TEST_ORG_IDS = [5, 6, 8, 10]

def test_graphql_endpoint_availability():
    """Test GraphQL endpoint availability."""
    print("🌐 Testing GraphQL endpoint availability...")
    
    # Test GET request (should return GraphiQL interface)
    try:
        response = requests.get(GRAPHQL_ENDPOINT, timeout=10)
        
        print(f"   GET Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            if "graphiql" in response.text.lower() or "graphql" in response.text.lower():
                print("   ✅ GraphQL interface accessible")
                return True
            else:
                print("   ❌ GraphQL interface not found")
                return False
        else:
            print(f"   ❌ GraphQL endpoint not accessible: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ GraphQL endpoint failed: {e}")
        return False

def test_graphql_introspection():
    """Test GraphQL introspection query."""
    print("\n🔍 Testing GraphQL introspection...")
    
    introspection_query = """
    query IntrospectionQuery {
        __schema {
            queryType {
                name
                fields {
                    name
                    type {
                        name
                    }
                }
            }
        }
    }
    """
    
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={"query": introspection_query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if "data" in data and "__schema" in data["data"]:
                schema_data = data["data"]["__schema"]
                query_type = schema_data.get("queryType", {})
                fields = query_type.get("fields", [])
                
                print(f"   Available queries: {len(fields)}")
                
                # Look for SOAP-related queries
                soap_queries = [f["name"] for f in fields if "soap" in f["name"].lower() or "network" in f["name"].lower()]
                print(f"   SOAP-related queries: {soap_queries}")
                
                if soap_queries:
                    print("   ✅ GraphQL introspection successful with SOAP queries")
                    return True
                else:
                    print("   ⚠️  GraphQL introspection successful but no SOAP queries found")
                    return True
            else:
                print("   ❌ Invalid introspection response structure")
                return False
        else:
            print(f"   ❌ Introspection failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error text: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Introspection request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON response: {e}")
        return False

def test_network_consultation_query():
    """Test NetworkConsultation GraphQL query."""
    print("\n📡 Testing NetworkConsultation GraphQL query...")
    
    query = """
    query NetworkConsultation($organizationIds: [Int!]!) {
        networkConsultation(organizationIds: $organizationIds) {
            presidents {
                organizationId
                presidentName
                presidentPhone
                presidentAddress
                presidentId
                status
            }
            organizations {
                organizationId
                organizationName
                address
                phone
                organizationType
                status
            }
            queryIds
            totalPresidents
            totalOrganizations
            errors
        }
    }
    """
    
    variables = {"organizationIds": TEST_ORG_IDS}
    
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={"query": query, "variables": variables},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if "errors" in data and data["errors"]:
                print(f"   GraphQL Errors: {data['errors']}")
                return False
            
            if "data" in data and "networkConsultation" in data["data"]:
                consultation_data = data["data"]["networkConsultation"]
                
                print(f"   Total Presidents: {consultation_data.get('totalPresidents', 0)}")
                print(f"   Total Organizations: {consultation_data.get('totalOrganizations', 0)}")
                print(f"   Query IDs: {consultation_data.get('queryIds', [])}")
                print(f"   Errors: {consultation_data.get('errors', [])}")
                
                # Validate structure
                required_fields = ['presidents', 'organizations', 'totalPresidents', 'totalOrganizations']
                missing_fields = [field for field in required_fields if field not in consultation_data]
                
                if not missing_fields:
                    print("   ✅ NetworkConsultation query successful with correct structure")
                    
                    # Show sample data
                    presidents = consultation_data.get('presidents', [])
                    organizations = consultation_data.get('organizations', [])
                    
                    if presidents:
                        print(f"   Sample President: {presidents[0].get('presidentName', 'N/A')} (Org: {presidents[0].get('organizationId', 'N/A')})")
                    
                    if organizations:
                        print(f"   Sample Organization: {organizations[0].get('organizationName', 'N/A')} (ID: {organizations[0].get('organizationId', 'N/A')})")
                    
                    return True
                else:
                    print(f"   ❌ Missing fields in response: {missing_fields}")
                    return False
            else:
                print("   ❌ Invalid response structure")
                print(f"   Response: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"   ❌ Query failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error text: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Query request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON response: {e}")
        return False

def test_soap_connection_test_query():
    """Test SoapConnectionTest GraphQL query."""
    print("\n🔍 Testing SoapConnectionTest GraphQL query...")
    
    query = """
    query SoapConnectionTest {
        soapConnectionTest {
            connected
            serviceUrl
            message
        }
    }
    """
    
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if "errors" in data and data["errors"]:
                print(f"   GraphQL Errors: {data['errors']}")
                return False
            
            if "data" in data and "soapConnectionTest" in data["data"]:
                connection_data = data["data"]["soapConnectionTest"]
                
                print(f"   Connected: {connection_data.get('connected', False)}")
                print(f"   Service URL: {connection_data.get('serviceUrl', 'N/A')}")
                print(f"   Message: {connection_data.get('message', 'N/A')}")
                
                # Validate structure
                required_fields = ['connected', 'serviceUrl', 'message']
                missing_fields = [field for field in required_fields if field not in connection_data]
                
                if not missing_fields:
                    print("   ✅ SoapConnectionTest query successful with correct structure")
                    return True
                else:
                    print(f"   ❌ Missing fields in response: {missing_fields}")
                    return False
            else:
                print("   ❌ Invalid response structure")
                print(f"   Response: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"   ❌ Query failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error text: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Query request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON response: {e}")
        return False

def test_presidents_only_query():
    """Test presidentsOnly GraphQL query."""
    print("\n👤 Testing presidentsOnly GraphQL query...")
    
    query = """
    query PresidentsOnly($organizationIds: [Int!]!) {
        presidentsOnly(organizationIds: $organizationIds) {
            organizationId
            presidentName
            presidentPhone
            presidentAddress
            presidentId
            status
        }
    }
    """
    
    variables = {"organizationIds": TEST_ORG_IDS}
    
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={"query": query, "variables": variables},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if "errors" in data and data["errors"]:
                print(f"   GraphQL Errors: {data['errors']}")
                return False
            
            if "data" in data and "presidentsOnly" in data["data"]:
                presidents_data = data["data"]["presidentsOnly"]
                
                print(f"   Presidents found: {len(presidents_data)}")
                
                if presidents_data:
                    # Show sample data
                    sample_president = presidents_data[0]
                    print(f"   Sample President: {sample_president.get('presidentName', 'N/A')} (Org: {sample_president.get('organizationId', 'N/A')})")
                    
                    # Validate structure
                    required_fields = ['organizationId', 'presidentName']
                    missing_fields = [field for field in required_fields if field not in sample_president]
                    
                    if not missing_fields:
                        print("   ✅ PresidentsOnly query successful with correct structure")
                        return True
                    else:
                        print(f"   ❌ Missing fields in president data: {missing_fields}")
                        return False
                else:
                    print("   ⚠️  No presidents found (might be expected)")
                    return True
            else:
                print("   ❌ Invalid response structure")
                print(f"   Response: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"   ❌ Query failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error text: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Query request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON response: {e}")
        return False

def test_organizations_only_query():
    """Test organizationsOnly GraphQL query."""
    print("\n🏢 Testing organizationsOnly GraphQL query...")
    
    query = """
    query OrganizationsOnly($organizationIds: [Int!]!) {
        organizationsOnly(organizationIds: $organizationIds) {
            organizationId
            organizationName
            address
            phone
            organizationType
            status
        }
    }
    """
    
    variables = {"organizationIds": TEST_ORG_IDS}
    
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={"query": query, "variables": variables},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if "errors" in data and data["errors"]:
                print(f"   GraphQL Errors: {data['errors']}")
                return False
            
            if "data" in data and "organizationsOnly" in data["data"]:
                organizations_data = data["data"]["organizationsOnly"]
                
                print(f"   Organizations found: {len(organizations_data)}")
                
                if organizations_data:
                    # Show sample data
                    sample_org = organizations_data[0]
                    print(f"   Sample Organization: {sample_org.get('organizationName', 'N/A')} (ID: {sample_org.get('organizationId', 'N/A')})")
                    
                    # Validate structure
                    required_fields = ['organizationId', 'organizationName']
                    missing_fields = [field for field in required_fields if field not in sample_org]
                    
                    if not missing_fields:
                        print("   ✅ OrganizationsOnly query successful with correct structure")
                        return True
                    else:
                        print(f"   ❌ Missing fields in organization data: {missing_fields}")
                        return False
                else:
                    print("   ⚠️  No organizations found (might be expected)")
                    return True
            else:
                print("   ❌ Invalid response structure")
                print(f"   Response: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"   ❌ Query failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error text: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Query request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON response: {e}")
        return False

def test_graphql_error_handling():
    """Test GraphQL error handling."""
    print("\n⚠️  Testing GraphQL error handling...")
    
    # Test invalid query syntax
    print("   Testing invalid query syntax...")
    invalid_query = "query { invalidField }"
    
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={"query": invalid_query},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "errors" in data and data["errors"]:
                print("     ✅ Invalid query properly handled with errors")
            else:
                print("     ❌ Invalid query not properly handled")
                return False
        else:
            print(f"     ❌ Unexpected status code for invalid query: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Invalid query test failed: {e}")
        return False
    
    # Test malformed JSON
    print("   Testing malformed JSON...")
    
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code in [400, 422]:
            print("     ✅ Malformed JSON properly handled")
        else:
            print(f"     ❌ Malformed JSON not properly handled: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"     ❌ Malformed JSON test failed: {e}")
        return False
    
    return True

def main():
    """Run all GraphQL integration tests."""
    print("🧪 GraphQL Integration and Queries Test Suite")
    print("=" * 60)
    
    tests = [
        ("GraphQL Endpoint Availability", test_graphql_endpoint_availability),
        ("GraphQL Introspection", test_graphql_introspection),
        ("NetworkConsultation Query", test_network_consultation_query),
        ("SoapConnectionTest Query", test_soap_connection_test_query),
        ("PresidentsOnly Query", test_presidents_only_query),
        ("OrganizationsOnly Query", test_organizations_only_query),
        ("GraphQL Error Handling", test_graphql_error_handling)
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
        print("🎉 All GraphQL integration tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)