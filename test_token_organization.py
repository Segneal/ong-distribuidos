#!/usr/bin/env python3
"""
Script para probar que el token JWT incluya la organización
"""

import requests
import json
import jwt

def test_login_token():
    """Prueba que el login genere un token con organización"""
    
    # URL del API Gateway
    login_url = "http://localhost:3001/api/auth/login"
    
    # Credenciales de prueba
    credentials = {
        "usernameOrEmail": "admin",
        "password": "admin"
    }
    
    print("🔐 Probando login con credenciales:")
    print(f"   Usuario: {credentials['usernameOrEmail']}")
    print(f"   Password: {credentials['password']}")
    print()
    
    try:
        # Hacer login
        response = requests.post(login_url, json=credentials)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Login exitoso!")
            print(f"   Usuario: {data['user']['username']}")
            print(f"   Rol: {data['user']['role']}")
            print(f"   Organización: {data['user'].get('organization', 'NO DEFINIDA')}")
            print()
            
            # Decodificar el token JWT
            token = data['token']
            print("🔍 Decodificando token JWT:")
            
            try:
                # Decodificar sin verificar (solo para inspección)
                decoded = jwt.decode(token, options={"verify_signature": False})
                print(f"   Token payload: {json.dumps(decoded, indent=2, default=str)}")
                
                # Verificar si tiene organización
                if 'organization' in decoded:
                    print(f"✅ Token incluye organización: {decoded['organization']}")
                else:
                    print("❌ Token NO incluye organización")
                    
            except Exception as e:
                print(f"❌ Error decodificando token: {e}")
                
        else:
            print("❌ Login falló:")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al API Gateway")
        print("   Asegúrate de que esté ejecutándose en http://localhost:3001")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_login_token()