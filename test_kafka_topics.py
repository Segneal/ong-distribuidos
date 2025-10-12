#!/usr/bin/env python3
"""
Test para verificar topics de Kafka
"""
import requests

def test_publish_simple():
    """Test de publicación simple"""
    try:
        response = requests.post(
            "http://localhost:50054/test/publish",
            json={
                "message_type": "donation_offer",
                "data": {
                    "offer_id": "test-offer-123",
                    "donations": [{"test": "data"}]
                }
            }
        )
        
        print(f"Test Publish Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🧪 TESTING KAFKA TOPICS")
    print("=" * 30)
    
    test_publish_simple()