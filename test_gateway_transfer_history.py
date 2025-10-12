#!/usr/bin/env python3
"""
Test del historial de transferencias via API Gateway
"""
import requests

def test_gateway_transfer_history():
    """Test del endpoint del API Gateway"""
    # Login como esperanza
    login_data = {
        "usernameOrEmail": "admin_esperanza",
        "password": "admin123"
    }
    
    try:
        response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('token')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test nuevo endpoint
            response = requests.get(
                "http://localhost:3001/api/messaging/transfer-history?limit=10",
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                transfers = data.get('transfers', [])
                print(f"\n✅ Transferencias encontradas: {len(transfers)}")
                
                for transfer in transfers:
                    print(f"  - ID: {transfer.get('id')}")
                    print(f"    Tipo: {transfer.get('tipo')}")
                    print(f"    Contraparte: {transfer.get('organizacion_contraparte')}")
                    print(f"    Fecha: {transfer.get('fecha_transferencia')}")
            
        else:
            print(f"Error en login: {response.status_code} - {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🧪 TEST HISTORIAL VIA API GATEWAY")
    print("=" * 40)
    
    test_gateway_transfer_history()