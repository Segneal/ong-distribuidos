#!/usr/bin/env python3
"""
Test simple para verificar la creación de donaciones
"""
import requests
import json

def test_donation_creation():
    """Test completo del flujo de creación de donaciones"""
    
    print("🧪 INICIANDO TEST DE CREACIÓN DE DONACIONES")
    print("=" * 60)
    
    # 1. Login para obtener token
    print("1. 🔐 Haciendo login...")
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
        print(f"❌ Error en login: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    token = login_response.json()["token"]
    organization = login_response.json()["user"]["organization"]
    user_id = login_response.json()["user"]["id"]
    
    print(f"✅ Login exitoso")
    print(f"   Token: {token[:20]}...")
    print(f"   Organization: {organization}")
    print(f"   User ID: {user_id}")
    
    # 2. Crear donación
    print("\n2. 📦 Creando donación...")
    donation_data = {
        "category": "ALIMENTOS",
        "description": "Test donation simple",
        "quantity": 5
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    donation_response = requests.post(
        "http://localhost:3001/api/inventory",
        json=donation_data,
        headers=headers
    )
    
    print(f"Status Code: {donation_response.status_code}")
    print(f"Response: {donation_response.text}")
    
    if donation_response.status_code == 201:
        response_data = donation_response.json()
        donation = response_data.get('donation', {})
        print(f"✅ Donación creada exitosamente!")
        print(f"   ID: {donation.get('id')}")
        print(f"   Category: {donation.get('category')}")
        print(f"   Description: {donation.get('description')}")
        print(f"   Quantity: {donation.get('quantity')}")
        print(f"   Organization: {donation.get('organization')}")
        
        # 3. Verificar que aparece en la lista
        print("\n3. 📋 Verificando lista de donaciones...")
        list_response = requests.get(
            "http://localhost:3001/api/inventory",
            headers=headers
        )
        
        if list_response.status_code == 200:
            donations = list_response.json()
            print(f"✅ Lista obtenida: {len(donations)} donaciones")
            
            # Buscar nuestra donación
            found = False
            for d in donations:
                if d.get('id') == donation.get('id'):
                    found = True
                    print(f"✅ Donación encontrada en la lista!")
                    break
            
            if not found:
                print(f"❌ Donación NO encontrada en la lista")
                return False
        else:
            print(f"❌ Error obteniendo lista: {list_response.status_code}")
            return False
        
        return True
    else:
        print(f"❌ Error creando donación: {donation_response.status_code}")
        return False

if __name__ == "__main__":
    success = test_donation_creation()
    if success:
        print("\n🎉 TEST COMPLETADO EXITOSAMENTE!")
    else:
        print("\n💥 TEST FALLÓ!")