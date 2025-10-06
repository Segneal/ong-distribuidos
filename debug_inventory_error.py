#!/usr/bin/env python3
"""
Script para debuggear errores de inventario
"""

import requests
import json

def debug_inventory():
    """Debug específico del inventario"""
    
    # URLs
    login_url = "http://localhost:3001/api/auth/login"
    inventory_url = "http://localhost:3001/api/inventory"
    
    print("🔍 DEBUGGING INVENTARIO")
    print("=" * 40)
    
    try:
        # 1. Login
        print("1️⃣ Haciendo login...")
        credentials = {"usernameOrEmail": "admin", "password": "admin"}
        login_response = requests.post(login_url, json=credentials)
        
        if login_response.status_code != 200:
            print(f"❌ Login falló: {login_response.text}")
            return
            
        login_data = login_response.json()
        token = login_data['token']
        
        print(f"✅ Login exitoso - Usuario: {login_data['user']['username']}")
        print(f"📍 Organización: {login_data['user']['organization']}")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 2. Probar inventario con detalles
        print("\n2️⃣ Probando inventario...")
        inventory_response = requests.get(inventory_url, headers=headers)
        
        print(f"📊 Status Code: {inventory_response.status_code}")
        print(f"📊 Headers: {dict(inventory_response.headers)}")
        
        if inventory_response.status_code == 200:
            inventory_data = inventory_response.json()
            print(f"✅ Inventario obtenido exitosamente")
            print(f"📦 Total donaciones: {len(inventory_data.get('donations', []))}")
            
            # Mostrar primeras donaciones
            for i, donation in enumerate(inventory_data.get('donations', [])[:3]):
                print(f"   {i+1}. {donation.get('description', 'Sin descripción')} - {donation.get('organization', 'Sin org')}")
        else:
            print(f"❌ Error obteniendo inventario:")
            print(f"   Response text: {inventory_response.text}")
            
            try:
                error_data = inventory_response.json()
                print(f"   Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                print("   No se pudo parsear JSON de error")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    debug_inventory()