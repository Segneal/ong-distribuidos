#!/usr/bin/env python3
"""
Script para probar las rutas de solicitudes del API
"""
import requests
import json

def test_requests_api():
    """Prueba las rutas de solicitudes"""
    
    # Configuración
    API_BASE = "http://localhost:3001/api"
    
    # Credenciales de prueba
    login_data = {
        "usernameOrEmail": "admin",
        "password": "admin123"
    }
    
    try:
        print("=== PROBANDO API DE SOLICITUDES ===\n")
        
        # 1. Login para obtener token
        print("1. Haciendo login...")
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
        
        login_result = login_response.json()
        token = login_result.get('token')
        
        if not token:
            print("❌ No se recibió token en la respuesta")
            return False
        
        print(f"✅ Login exitoso, token obtenido")
        
        # Headers con token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 2. Probar solicitudes activas (propias)
        print("\n2. Probando solicitudes activas...")
        active_response = requests.post(f"{API_BASE}/messaging/active-requests", headers=headers)
        
        if active_response.status_code == 200:
            active_data = active_response.json()
            print(f"✅ Solicitudes activas: {len(active_data.get('requests', []))} encontradas")
            
            for req in active_data.get('requests', [])[:2]:  # Mostrar solo las primeras 2
                print(f"   - {req['request_id']}: {len(req['donations'])} donaciones")
        else:
            print(f"❌ Error en solicitudes activas: {active_response.status_code}")
            print(f"Response: {active_response.text}")
        
        # 3. Probar solicitudes externas
        print("\n3. Probando solicitudes externas...")
        external_response = requests.post(f"{API_BASE}/messaging/external-requests", headers=headers)
        
        if external_response.status_code == 200:
            external_data = external_response.json()
            print(f"✅ Solicitudes externas: {len(external_data.get('requests', []))} encontradas")
            
            for req in external_data.get('requests', [])[:2]:  # Mostrar solo las primeras 2
                print(f"   - {req['request_id']} de {req['requesting_organization']}: {len(req['donations'])} donaciones")
        else:
            print(f"❌ Error en solicitudes externas: {external_response.status_code}")
            print(f"Response: {external_response.text}")
        
        # 4. Probar creación de nueva solicitud
        print("\n4. Probando creación de nueva solicitud...")
        new_request_data = {
            "donations": [
                {"category": "ROPA", "description": "Ropa de prueba API"},
                {"category": "ALIMENTOS", "description": "Alimentos de prueba API"}
            ],
            "notes": "Solicitud creada desde prueba de API"
        }
        
        create_response = requests.post(
            f"{API_BASE}/messaging/create-donation-request", 
            headers=headers,
            json=new_request_data
        )
        
        if create_response.status_code == 200:
            create_data = create_response.json()
            print(f"✅ Nueva solicitud creada: {create_data.get('request_id')}")
        else:
            print(f"❌ Error creando solicitud: {create_response.status_code}")
            print(f"Response: {create_response.text}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está corriendo el API Gateway en el puerto 3001?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    if test_requests_api():
        print("\n🎉 Pruebas completadas!")
    else:
        print("\n❌ Algunas pruebas fallaron")