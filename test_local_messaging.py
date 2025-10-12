#!/usr/bin/env python3
"""
Test del messaging service local
"""
import requests

def test_local_messaging():
    """Test del messaging service local"""
    try:
        response = requests.post(
            "http://localhost:50055/api/getTransferHistory",
            json={"organizationId": "esperanza-social", "limit": 10}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_local_messaging()