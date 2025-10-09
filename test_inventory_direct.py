#!/usr/bin/env python3
"""
Test directo del inventario
"""
import requests
import json

def test_inventory():
    """Test directo del inventario"""
    
    print("🧪 PROBANDO INVENTARIO DIRECTO...")
    
    # 1. Login
    login_data = {
        "usernameOrEmail": "admin",
        "password": "admin123"
    }
    
    login_response = requests.post(
        "http://localhost:3001/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login falló: {login_response.status_code}")
        return
    
    token = login_response.json()["token"]
    print(f"✅ Login exitoso")
    
    # 2. Obtener inventario
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    inventory_response = requests.get(
        "http://localhost:3001/api/inventory",
        headers=headers
    )
    
    print(f"Status Code: {inventory_response.status_code}")
    print(f"Response: {inventory_response.text[:200]}...")
    
    if inventory_response.status_code == 200:
        data = inventory_response.json()
        donations = data.get('donations', [])
        print(f"✅ Inventario obtenido: {len(donations)} donaciones")
        
        # Mostrar primeras 3 donaciones
        for i, donation in enumerate(donations[:3]):
            print(f"  {i+1}. ID: {donation.get('id')}, Org: {donation.get('organization')}, Desc: {donation.get('description')}")
    else:
        print(f"❌ Error obteniendo inventario")

if __name__ == "__main__":
    test_inventory()