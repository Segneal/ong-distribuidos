#!/usr/bin/env python3
"""
Test de login con esperanza_admin
"""
import requests
import json

def test_esperanza_login():
    """Test de login con esperanza_admin"""
    
    print("🔐 PROBANDO LOGIN CON ESPERANZA_ADMIN...")
    
    login_data = {
        "usernameOrEmail": "esperanza_admin",
        "password": "password123"
    }
    
    try:
        login_response = requests.post(
            "http://localhost:3001/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        
        if login_response.status_code == 200:
            data = login_response.json()
            print(f"✅ Login exitoso!")
            print(f"Token: {data.get('token', 'N/A')[:20]}...")
            print(f"User: {data.get('user', {})}")
            
            # Probar inventario
            token = data.get('token')
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            inventory_response = requests.get(
                "http://localhost:3001/api/inventory",
                headers=headers
            )
            
            print(f"\n📦 INVENTARIO:")
            print(f"Status Code: {inventory_response.status_code}")
            
            if inventory_response.status_code == 200:
                inv_data = inventory_response.json()
                donations = inv_data.get('donations', [])
                print(f"✅ Ve {len(donations)} donaciones")
                for d in donations[:3]:
                    print(f"  - ID: {d.get('id')}, Org: {d.get('organization')}")
            else:
                print(f"❌ Error inventario: {inventory_response.text}")
                
        else:
            print(f"❌ Login falló")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_esperanza_login()