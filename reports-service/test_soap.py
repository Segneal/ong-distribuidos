#!/usr/bin/env python3
"""
Test script for SOAP service functionality.
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.soap_service import get_soap_service

async def test_soap_service():
    """Test the SOAP service functionality."""
    print("🧪 Testing SOAP Service...")
    
    soap_service = get_soap_service()
    
    # Test connection
    print("\n1. Testing SOAP connection...")
    connection_result = await soap_service.test_soap_connection()
    print(f"   Connection: {connection_result}")
    
    if not connection_result['connected']:
        print("❌ SOAP service is not available. Exiting.")
        return
    
    # Test organization IDs from the Postman collection
    test_org_ids = [5, 6, 8, 10]
    
    # Test network consultation
    print(f"\n2. Testing network consultation with IDs: {test_org_ids}")
    try:
        consultation_result = await soap_service.get_network_consultation(test_org_ids)
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
    
    # Test presidents only
    print(f"\n3. Testing presidents only query...")
    try:
        presidents = await soap_service.get_president_data_only(test_org_ids)
        print(f"   Found {len(presidents)} presidents")
        for president in presidents[:2]:  # Show first 2
            print(f"     - {president.president_name} (Phone: {president.president_phone})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test organizations only
    print(f"\n4. Testing organizations only query...")
    try:
        organizations = await soap_service.get_organization_data_only(test_org_ids)
        print(f"   Found {len(organizations)} organizations")
        for org in organizations[:2]:  # Show first 2
            print(f"     - {org.organization_name} (Phone: {org.phone})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n✅ SOAP service test completed!")

if __name__ == "__main__":
    asyncio.run(test_soap_service())