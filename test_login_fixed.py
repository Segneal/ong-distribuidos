#!/usr/bin/env python3
"""
Probar login después de los fixes
"""
import requests
import time

def test_login_fixed():
    print("🧪 PROBANDO LOGIN DESPUÉS DE LOS FIXES")
    print("=" * 50)
    
    # URL del API Gateway
    login_url = "http://localhost:3001/api/auth/login"
    
    # Usuarios de prueba (todos con password 'admin')
    test_users = [
        ("esperanza_admin", "admin", "fundacion-esperanza"),
        ("solidaria_admin", "admin", "ong-solidaria"),
        ("centro_admin", "admin", "centro-comunitario"),
        ("admin", "admin", "empuje-comunitario")
    ]
    
    for username, password, expected_org in test_users:
        print(f"\n🔐 Probando: {username}")
        
        login_data = {
            "usernameOrEmail": username,
            "password": password
        }
        
        try:
            response = requests.post(login_url, json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                
                print(f"   ✅ Login exitoso")
                print(f"   Nombre: {user.get('firstName')} {user.get('lastName')}")
                print(f"   Organización: {user.get('organization')}")
                print(f"   Rol: {user.get('role')}")
                print(f"   Token: {data.get('token', '')[:20]}...")
                
                # Verificar organización
                if user.get('organization') == expected_org:
                    print(f"   ✅ Organización correcta")
                else:
                    print(f"   ⚠ Organización: esperado {expected_org}, obtenido {user.get('organization')}")
                    
            else:
                print(f"   ❌ Error HTTP {response.status_code}")
                if response.status_code == 404:
                    print(f"   API Gateway no está corriendo en puerto 3000")
                    break
                else:
                    print(f"   Response: {response.text[:200]}")
                    
        except requests.exceptions.ConnectionError:
            print(f"   ❌ No se puede conectar al API Gateway")
            print(f"   Asegúrate de que esté corriendo en puerto 3000")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📋 INSTRUCCIONES SI HAY ERRORES:")
    print(f"   1. Reiniciar user-service: cd user-service && python src/server.py")
    print(f"   2. Verificar API Gateway: cd api-gateway && npm start")
    print(f"   3. Los proto files ya fueron regenerados")

if __name__ == "__main__":
    test_login_fixed()