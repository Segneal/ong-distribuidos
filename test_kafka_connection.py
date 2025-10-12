#!/usr/bin/env python3
"""
Test de conexión a Kafka
"""
import requests

def test_messaging_service_health():
    """Test del health check del messaging service"""
    try:
        response = requests.get("http://localhost:50054/health")
        print(f"Health Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Service Status: {data.get('status')}")
            print(f"Kafka Status: {data.get('kafka', {}).get('status')}")
            print(f"Consumers: {data.get('consumers')}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_messaging_service_status():
    """Test del status detallado"""
    try:
        response = requests.get("http://localhost:50054/status")
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🔍 TESTING KAFKA CONNECTION")
    print("=" * 40)
    
    test_messaging_service_health()
    test_messaging_service_status()