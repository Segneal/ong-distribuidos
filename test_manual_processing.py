#!/usr/bin/env python3
"""
Test del endpoint manual de procesamiento
"""
import requests

def test_manual_processing():
    """Test del endpoint manual"""
    print("🔧 TESTING ENDPOINT MANUAL DE PROCESAMIENTO")
    print("=" * 50)
    
    response = requests.post("http://localhost:3001/api/messaging/process-pending-transfers")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_manual_processing()