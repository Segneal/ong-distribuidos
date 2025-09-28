#!/usr/bin/env python3
"""
Simple test script for the messaging service
"""

import requests
import json
import time
import sys

def test_messaging_service():
    """Test the messaging service endpoints"""
    base_url = "http://localhost:50054"
    
    print("Testing Messaging Service...")
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test status endpoint
    print("\n2. Testing status endpoint...")
    try:
        response = requests.get(f"{base_url}/status", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Status check failed: {e}")
        return False
    
    # Test message publishing
    print("\n3. Testing message publishing...")
    test_messages = [
        {
            "message_type": "donation_request",
            "data": {
                "request_id": "TEST-REQ-001",
                "donations": [
                    {
                        "category": "ALIMENTOS",
                        "description": "Puré de tomates"
                    }
                ]
            }
        },
        {
            "message_type": "donation_offer",
            "data": {
                "offer_id": "TEST-OFFER-001",
                "donations": [
                    {
                        "category": "ROPA",
                        "description": "Camisetas talla M",
                        "quantity": "10 unidades"
                    }
                ]
            }
        },
        {
            "message_type": "solidarity_event",
            "data": {
                "event_id": "TEST-EVENT-001",
                "name": "Evento de Prueba",
                "description": "Evento solidario de prueba",
                "event_date": "2024-02-15T10:00:00Z"
            }
        }
    ]
    
    for i, test_msg in enumerate(test_messages, 1):
        print(f"\n3.{i}. Testing {test_msg['message_type']} message...")
        try:
            response = requests.post(
                f"{base_url}/test/publish",
                params={"message_type": test_msg["message_type"]},
                json=test_msg["data"],
                timeout=10
            )
            print(f"Publish Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Message publish failed: {e}")
    
    print("\n✅ Messaging service test completed!")
    return True

if __name__ == "__main__":
    print("Waiting for service to start...")
    time.sleep(5)
    
    success = test_messaging_service()
    sys.exit(0 if success else 1)