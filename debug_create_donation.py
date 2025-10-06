#!/usr/bin/env python3
"""
Script para debuggear la creación de donaciones
"""

import requests
import json

def debug_create_donation():
    """Debug específico de la creación de donaciones"""
    
    # URLs
    login_url = "http://localhost:3001/api/auth/login"
    inventory_url = "http://localhost:3001/api/inventory"
    
    print("🔍 DEBUGGING CREACIÓN DE DONACIONES")
    print("=" * 50)
    
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
        
        # 2. Intentar crear una donación
        print("\n2️⃣ Intentando crear donación...")
        
        donation_data = {
            "category": "ALIMENTOS",
            "description": "Prueba de donación multi-org",
            "quantity": 10
        }
        
        print(f"📦 Datos de donación: {json.dumps(donation_data, indent=2)}")
        
        create_response = requests.post(inventory_url, json=donation_data, headers=headers)
        
        print(f"📊 Status Code: {create_response.status_code}")
        print(f"📊 Headers: {dict(create_response.headers)}")
        
        if create_response.status_code == 201:
            create_data = create_response.json()
            print(f"✅ Donación creada exitosamente!")
            print(f"📦 ID: {create_data.get('donation', {}).get('id')}")
            print(f"📦 Organización: {create_data.get('donation', {}).get('organization')}")
        else:
            print(f"❌ Error creando donación:")
            print(f"   Response text: {create_response.text}")
            
            try:
                error_data = create_response.json()
                print(f"   Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                print("   No se pudo parsear JSON de error")
        
        # 3. Intentar obtener lista de donaciones
        print("\n3️⃣ Obteniendo lista de donaciones...")
        list_response = requests.get(inventory_url, headers=headers)
        
        print(f"📊 Status Code: {list_response.status_code}")
        
        if list_response.status_code == 200:
            list_data = list_response.json()
            print(f"✅ Lista obtenida - Total: {len(list_data.get('donations', []))}")
            
            # Mostrar últimas donaciones
            for i, donation in enumerate(list_data.get('donations', [])[:3]):
                print(f"   {i+1}. {donation.get('description', 'Sin descripción')} - {donation.get('organization', 'Sin org')}")
        else:
            print(f"❌ Error obteniendo lista: {list_response.text}")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    debug_create_donation()