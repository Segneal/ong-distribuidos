#!/usr/bin/env python3
"""
Test simple del endpoint
"""
import requests

def test_endpoints():
    """Test de endpoints"""
    print("=== TESTING TEST ENDPOINT ===")
    try:
        response = requests.post(
            "http://localhost:50054/api/testTransferHistory",
            json={"test": "data"}
        )
        
        print(f"Test Status: {response.status_code}")
        print(f"Test Response: {response.text}")
        
    except Exception as e:
        print(f"Test Error: {e}")
    
    print("\n=== TESTING REAL ENDPOINT ===")
    try:
        response = requests.post(
            "http://localhost:50054/api/getTransferHistory",
            json={"organizationId": "esperanza-social", "limit": 10}
        )
        
        print(f"Real Status: {response.status_code}")
        print(f"Real Response: {response.text}")
        
    except Exception as e:
        print(f"Real Error: {e}")

if __name__ == "__main__":
    test_endpoints()