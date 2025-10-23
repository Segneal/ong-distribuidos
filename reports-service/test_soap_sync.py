#!/usr/bin/env python3
"""
Test script for SOAP service functionality (synchronous version).
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.soap_service import get_soap_service

def test_soap_service_sync():
    """Test the SOAP service functionality synchronously."""
    print("🧪 Testing SOAP Service (Sync)...")
    
    soap_service = get_soap_service()
    
    # Test connection
    print("\n1. Testing SOAP connection...")
    connection_result = soap_service.test_soap_connection()
    print(f"   Connection: {connection_result}")
    
    if not connection_result['connected']:
        print("❌ SOAP service is not available. Exiting.")
        return
    
    # Test organization IDs from the Postman collection
    test_org_ids = [5, 6, 8, 10]
    
    # Test network consultation
    print(f"\n2. Testing network consultation with IDs: {test_org_ids}")
    try:
        consultation_result = soap_service.get_network_consultation(test_org_ids)
        print(f"   Total Presidents: {consultation_result.total_presidents}")
        print(f"   Total Organizations: {consultation_result.total_organizations}")
        print(f"   Errors: {consultation_result.errors}")
        
        if consultation_result.presidents:
            print("\n   Presidents found:")
            for president in consultation_result.presidents[:3]:  # Show first 3
                print(f"     - {president.president_name} (Org: {president.organization_id})")
        
        if consultation_result.organizations:
            print("\n   Organizations found:")
            for org in consultation_result.organizations[:3]:  # Show first 3
                print(f"     - {org.organization_name} (ID: {org.organization_id})")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ SOAP service test completed!")

if __name__ == "__main__":
    test_soap_service_sync()