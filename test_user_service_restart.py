#!/usr/bin/env python3
"""
Script para verificar que el user-service funciona correctamente
"""
import requests
import time

def test_api_gateway():
    """Probar a través del API Gateway"""
    try:
        print("🧪 PROBANDO A TRAVÉS DEL API GATEWAY")
        print("=" * 50)
        
        # URL del API Gateway
        login_url = "http://localhost:3000/api/auth/login"
        
        # Usuarios de prueba
        test_users = [
            ("esperanza_admin", "password123", "fundacion-esperanza"),
            ("solidaria_admin", "password123", "ong-solidaria"),
            ("centro_admin", "password123", "centro-comunitario")
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
                    
                    # Verificar organización
                    if user.get('organization') == expected_org:
                        print(f"   ✅ Organización correcta")
                    else:
                        print(f"   ⚠ Organización: esperado {expected_org}, obtenido {user.get('organization')}")
                        
                else:
                    print(f"   ❌ Error HTTP {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    
            except requests.exceptions.ConnectionError:
                print(f"   ❌ No se puede conectar al API Gateway (puerto 3000)")
                print(f"   Asegúrate de que el API Gateway esté corriendo")
                break
            except requests.exceptions.Timeout:
                print(f"   ❌ Timeout - el servicio puede estar colgado")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n📋 INSTRUCCIONES:")
        print(f"   1. Asegúrate de que MySQL esté corriendo")
        print(f"   2. Inicia el user-service: cd user-service && python src/server.py")
        print(f"   3. Inicia el API Gateway: cd api-gateway && npm start")
        print(f"   4. Ejecuta este script nuevamente")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_api_gateway()