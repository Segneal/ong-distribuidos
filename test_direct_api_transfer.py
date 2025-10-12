#!/usr/bin/env python3
"""
Test de transferencia directa por API
"""
import requests
import time

def test_direct_transfer():
    """Test transferencia directa"""
    print("🎯 TESTING TRANSFERENCIA DIRECTA POR API")
    print("=" * 50)
    
    # Login
    login_data = {"usernameOrEmail": "admin", "password": "admin123"}
    response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Error login: {response.text}")
        return
    
    token = response.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Intentar transferencia
    transfer_data = {
        "targetOrganization": "esperanza-social",
        "requestId": f"api-test-{int(time.time())}",
        "donations": [
            {
                "category": "ALIMENTOS",
                "quantity": "1",
                "description": "Test API directo",
                "inventoryId": 12,
                "inventory_id": 12,
                "parsed_quantity": 1
            }
        ],
        "notes": "Test API directo"
    }
    
    print("📤 Enviando transferencia...")
    print(f"Data: {transfer_data}")
    
    response = requests.post(
        "http://localhost:3001/api/messaging/transfer-donations",
        json=transfer_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ ¡Transferencia exitosa!")
        
        # Verificar resultado
        time.sleep(2)
        print("\n🔍 Verificando resultado...")
        
        # Login esperanza
        login_data = {"usernameOrEmail": "admin_esperanza", "password": "admin123"}
        response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            token_esperanza = response.json().get('token')
            headers_esperanza = {'Authorization': f'Bearer {token_esperanza}'}
            
            response = requests.get(
                "http://localhost:3001/api/messaging/transfer-history?limit=1",
                headers=headers_esperanza
            )
            
            if response.status_code == 200:
                data = response.json()
                transfers = data.get('transfers', [])
                if transfers:
                    latest = transfers[0]
                    print(f"Última transferencia recibida:")
                    print(f"  - Request ID: {latest.get('request_id')}")
                    print(f"  - Tipo: {latest.get('tipo')}")
                    print(f"  - Notas: {latest.get('notas')}")
                    
                    if 'automático' in latest.get('notas', ''):
                        print("✅ ¡PROCESAMIENTO AUTOMÁTICO FUNCIONÓ!")
                    else:
                        print("⚠️  No se procesó automáticamente")
    else:
        print("❌ Error en transferencia")

if __name__ == "__main__":
    test_direct_transfer()