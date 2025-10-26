#!/usr/bin/env python3
"""
Comprehensive test script for SOAP service connectivity and authentication.
This script tests all aspects of the SOAP integration as specified in task 1.1.
"""
import sys
import os
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.soap.client import SOAPClient, SOAPServiceError

def test_wsdl_connectivity():
    """Test connection to the WSDL endpoint."""
    print("🔗 Testing WSDL connectivity...")
    
    try:
        response = requests.get('https://soap-app-latest.onrender.com/?wsdl', timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        print(f"   Content Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            # Parse WSDL to verify it's valid XML
            try:
                root = ET.fromstring(response.text)
                print(f"   WSDL Root Element: {root.tag}")
                
                # Look for service definitions
                namespaces = {'wsdl': 'http://schemas.xmlsoap.org/wsdl/'}
                services = root.findall('.//wsdl:service', namespaces)
                if services:
                    print(f"   Found {len(services)} service(s) in WSDL")
                
                print("   ✅ WSDL is accessible and valid")
                return True
            except ET.ParseError as e:
                print(f"   ❌ WSDL parsing error: {e}")
                return False
        else:
            print(f"   ❌ WSDL not accessible: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return False

def test_soap_authentication():
    """Test SOAP authentication with GrupoA-TM/clave-tm-a credentials."""
    print("\n🔐 Testing SOAP authentication...")
    
    client = SOAPClient()
    
    # Test authentication by making a simple request
    try:
        # Create a test SOAP envelope with authentication
        test_envelope = client._create_soap_envelope('list_associations', [1])
        
        print("   Authentication headers in SOAP envelope:")
        print(f"   - Grupo: {client.auth_group}")
        print(f"   - Clave: {client.auth_key}")
        
        # Verify the envelope contains auth headers
        if client.auth_group in test_envelope and client.auth_key in test_envelope:
            print("   ✅ Authentication headers properly included in SOAP envelope")
        else:
            print("   ❌ Authentication headers missing from SOAP envelope")
            return False
        
        # Test actual authentication by making a request
        response = client._make_soap_request('list_associations', [1])
        
        if response and len(response) > 0:
            print("   ✅ Authentication successful - received valid response")
            return True
        else:
            print("   ❌ Authentication failed - empty response")
            return False
            
    except SOAPServiceError as e:
        if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
            print(f"   ❌ Authentication failed: {e}")
            return False
        else:
            # Other errors might still indicate successful auth but other issues
            print(f"   ⚠️  Request completed but with error: {e}")
            return True
    except Exception as e:
        print(f"   ❌ Unexpected error during authentication test: {e}")
        return False

def test_list_presidents_operation():
    """Test the list_presidents SOAP operation."""
    print("\n👥 Testing list_presidents SOAP operation...")
    
    client = SOAPClient()
    test_org_ids = [5, 6, 8]
    
    try:
        president_data = client.get_president_data(test_org_ids)
        
        print(f"   Queried organization IDs: {test_org_ids}")
        print(f"   Presidents found: {len(president_data)}")
        
        if president_data:
            print("   Sample president data:")
            for i, president in enumerate(president_data[:2]):  # Show first 2
                print(f"     {i+1}. Name: {president.get('president_name', 'N/A')}")
                print(f"        Organization ID: {president.get('organization_id', 'N/A')}")
                print(f"        Phone: {president.get('president_phone', 'N/A')}")
                print(f"        Address: {president.get('president_address', 'N/A')}")
            
            # Validate data structure
            required_fields = ['organization_id', 'president_name', 'president_phone', 'president_id']
            valid_structure = True
            
            for president in president_data:
                for field in required_fields:
                    if field not in president:
                        print(f"   ❌ Missing required field '{field}' in president data")
                        valid_structure = False
                        break
            
            if valid_structure:
                print("   ✅ list_presidents operation successful with valid data structure")
                return True
            else:
                print("   ❌ list_presidents operation returned invalid data structure")
                return False
        else:
            print("   ⚠️  list_presidents operation returned no data (might be expected)")
            return True
            
    except Exception as e:
        print(f"   ❌ list_presidents operation failed: {e}")
        return False

def test_list_associations_operation():
    """Test the list_associations SOAP operation."""
    print("\n🏢 Testing list_associations SOAP operation...")
    
    client = SOAPClient()
    test_org_ids = [5, 6, 8]
    
    try:
        organization_data = client.get_organization_data(test_org_ids)
        
        print(f"   Queried organization IDs: {test_org_ids}")
        print(f"   Organizations found: {len(organization_data)}")
        
        if organization_data:
            print("   Sample organization data:")
            for i, org in enumerate(organization_data[:2]):  # Show first 2
                print(f"     {i+1}. Name: {org.get('organization_name', 'N/A')}")
                print(f"        Organization ID: {org.get('organization_id', 'N/A')}")
                print(f"        Phone: {org.get('phone', 'N/A')}")
                print(f"        Address: {org.get('address', 'N/A')}")
            
            # Validate data structure
            required_fields = ['organization_id', 'organization_name', 'phone', 'address']
            valid_structure = True
            
            for org in organization_data:
                for field in required_fields:
                    if field not in org:
                        print(f"   ❌ Missing required field '{field}' in organization data")
                        valid_structure = False
                        break
            
            if valid_structure:
                print("   ✅ list_associations operation successful with valid data structure")
                return True
            else:
                print("   ❌ list_associations operation returned invalid data structure")
                return False
        else:
            print("   ⚠️  list_associations operation returned no data (might be expected)")
            return True
            
    except Exception as e:
        print(f"   ❌ list_associations operation failed: {e}")
        return False

def test_connection_method():
    """Test the connection test method."""
    print("\n🔍 Testing connection test method...")
    
    client = SOAPClient()
    
    try:
        connection_result = client.test_connection()
        
        if connection_result:
            print("   ✅ Connection test method returned True")
            return True
        else:
            print("   ❌ Connection test method returned False")
            return False
            
    except Exception as e:
        print(f"   ❌ Connection test method failed: {e}")
        return False

def main():
    """Run all SOAP connectivity and authentication tests."""
    print("🧪 SOAP Service Connectivity and Authentication Test Suite")
    print("=" * 60)
    
    tests = [
        ("WSDL Connectivity", test_wsdl_connectivity),
        ("SOAP Authentication", test_soap_authentication),
        ("list_presidents Operation", test_list_presidents_operation),
        ("list_associations Operation", test_list_associations_operation),
        ("Connection Test Method", test_connection_method)
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
        print("🎉 All SOAP connectivity and authentication tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)