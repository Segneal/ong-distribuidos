#!/usr/bin/env python3
"""
Script para debuggear el token que está usando el frontend
"""

import requests
import json
import jwt

def debug_frontend_flow():
    """Debug completo del flujo frontend"""
    
    # URLs
    login_url = "http://localhost:3001/api/auth/login"
    users_url = "http://localhost:3001/api/users"
    
    print("🔍 DEBUGGING FRONTEND TOKEN FLOW")
    print("=" * 50)
    
    # 1. Hacer login fresco
    credentials = {
        "usernameOrEmail": "admin",
        "password": "admin"
    }
    
    print("1️⃣ HACIENDO LOGIN FRESCO...")
    login_response = requests.post(login_url, json=credentials)
    
    if login_response.status_code != 200:
        print(f"❌ Login falló: {login_response.text}")
        return
        
    login_data = login_response.json()
    token = login_data['token']
    
    print(f"✅ Login exitoso")
    print(f"   Usuario: {login_data['user']['username']}")
    print(f"   Organización en respuesta: {login_data['user'].get('organization', 'NO DEFINIDA')}")
    print()
    
    # 2. Decodificar el token
    print("2️⃣ DECODIFICANDO TOKEN RECIÉN GENERADO...")
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        print(f"   Token payload: {json.dumps(decoded, indent=2, default=str)}")
        
        has_org = 'organization' in decoded
        print(f"   ✅ Token incluye organización: {has_org}")
        if has_org:
            print(f"   📍 Organización en token: {decoded['organization']}")
        print()
    except Exception as e:
        print(f"❌ Error decodificando token: {e}")
        return
    
    # 3. Usar el token para obtener usuarios
    print("3️⃣ USANDO TOKEN PARA OBTENER USUARIOS...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    users_response = requests.get(users_url, headers=headers)
    print(f"   Status: {users_response.status_code}")
    
    if users_response.status_code == 200:
        users_data = users_response.json()
        print(f"   ✅ Usuarios obtenidos: {len(users_data.get('users', []))}")
        
        # Mostrar primeros 3 usuarios
        for i, user in enumerate(users_data.get('users', [])[:3]):
            print(f"   - {user['username']} ({user.get('organization', 'Sin org')})")
    else:
        print(f"   ❌ Error: {users_response.text}")
    
    print()
    print("4️⃣ SIMULANDO REQUEST DEL FRONTEND...")
    
    # 4. Simular exactamente lo que hace el frontend
    # Verificar si el frontend está enviando el token correctamente
    frontend_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    frontend_response = requests.get(users_url, headers=frontend_headers)
    print(f"   Status: {frontend_response.status_code}")
    
    if frontend_response.status_code == 200:
        data = frontend_response.json()
        print(f"   ✅ Response recibida correctamente")
        print(f"   📊 Total usuarios: {len(data.get('users', []))}")
    else:
        print(f"   ❌ Error en request del frontend: {frontend_response.text}")

if __name__ == "__main__":
    debug_frontend_flow()