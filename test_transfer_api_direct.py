#!/usr/bin/env python3
"""
Test directo del API de transferencias
"""
import requests

def test_transfer_api():
    """Test directo del API sin autenticación"""
    try:
        # Test directo al messaging service
        response = requests.post(
            "http://localhost:50054/api/getTransferHistory",
            json={"organizationId": "esperanza-social", "limit": 10}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            transfers = data.get('transfers', [])
            print(f"Transferencias encontradas: {len(transfers)}")
            
            for transfer in transfers:
                print(f"  - ID: {transfer.get('id')}")
                print(f"    Tipo: {transfer.get('tipo')}")
                print(f"    Contraparte: {transfer.get('organizacion_contraparte')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🧪 TEST DIRECTO API TRANSFERENCIAS")
    print("=" * 40)
    
    test_transfer_api()