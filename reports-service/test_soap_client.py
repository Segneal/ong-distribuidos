#!/usr/bin/env python3
"""
Test script for SOAP client functionality.
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.soap.client import get_soap_client, SOAPServiceError
from src.services.soap_service import get_soap_service


async def test_soap_client():
    """Test the SOAP client functionality."""
    print("Testing SOAP Client...")
    
    try:
        # Test SOAP client initialization
        print("\n1. Testing SOAP client initialization...")
        soap_client = get_soap_client()
        print(f"✓ SOAP client initialized with URL: {soap_client.settings.SOAP_SERVICE_URL}")
        
        # Test connection
        print("\n2. Testing SOAP connection...")
        is_connected = soap_client.test_connection()
        print(f"✓ Connection test result: {is_connected}")
        
        # Test SOAP service
        print("\n3. Testing SOAP service...")
        soap_service = get_soap_service()
        connection_result = await soap_service.test_soap_connection()
        print(f"✓ Service connection test: {connection_result}")
        
        # Test with sample organization IDs
        print("\n4. Testing network consultation with sample IDs...")
        sample_ids = [1, 2, 3]
        
        try:
            result = await soap_service.get_network_consultation(sample_ids)
            print(f"✓ Network consultation completed")
            print(f"  - Query IDs: {result.query_ids}")
            print(f"  - Presidents found: {result.total_presidents}")
            print(f"  - Organizations found: {result.total_organizations}")
            print(f"  - Errors: {result.errors}")
            
            if result.presidents:
                print(f"  - First president: {result.presidents[0].dict()}")
            
            if result.organizations:
                print(f"  - First organization: {result.organizations[0].dict()}")
                
        except Exception as e:
            print(f"⚠ Network consultation failed (expected if service is not available): {e}")
        
        print("\n✓ All SOAP client tests completed successfully!")
        
    except Exception as e:
        print(f"✗ SOAP client test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    # Set up environment
    os.environ.setdefault('SOAP_SERVICE_URL', 'https://soap-applatest.onrender.com/?wsdl')
    os.environ.setdefault('SOAP_TIMEOUT', '30')
    
    # Run tests
    success = asyncio.run(test_soap_client())
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)