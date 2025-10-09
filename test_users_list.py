#!/usr/bin/env python3
"""
Script para probar que la lista de usuarios funcione con la organización
"""

import requests
import json

def test_users_list():
    """Prueba que la lista de usuarios funcione con el token que incluye organización"""
    
    # URLs
    login_url = "http://localhost:3001/api/auth/login"
    users_url = "http://localhost:3001/api/users"
    
    # Credenciales de prueba - probemos con otro usuario
    credentials = {
        "usernameOrEmail": "esperanza_admin",
        "password": "admin"
    }
    
    print("🔐 Haciendo login...")
    
    try:
        # Hacer login
        login_response = requests.post(login_url, json=credentials)
        
        if login_response.status_code != 200:
            print(f"❌ Login falló: {login_response.text}")
            return
            
        login_data = login_response.json()
        token = login_data['token']
        user_org = login_data['user']['organization']
        
        print(f"✅ Login exitoso!")
        print(f"   Usuario: {login_data['user']['username']}")
        print(f"   Organización: {user_org}")
        print()
        
        # Probar lista de usuarios
        print("📋 Obteniendo lista de usuarios...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        users_response = requests.get(users_url, headers=headers)
        
        print(f"📊 Status Code: {users_response.status_code}")
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            
            print("✅ Lista de usuarios obtenida exitosamente!")
            print(f"   Total usuarios: {len(users_data.get('users', []))}")
            
            # Mostrar usuarios
            for user in users_data.get('users', []):
                print(f"   - {user['username']} ({user.get('organization', 'Sin org')}) - {user['role']}")
                
        else:
            print("❌ Error obteniendo usuarios:")
            print(f"   Response: {users_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al API Gateway")
        print("   Asegúrate de que esté ejecutándose en http://localhost:3001")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_users_list()