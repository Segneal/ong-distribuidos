#!/usr/bin/env python3
"""
Script para probar la API de solicitudes de donación
"""
import requests
import json

def test_donation_request_api():
    """Probar la API de solicitudes de donación"""
    
    API_BASE = "http://localhost:3001/api"
    
    print("📋 TESTING API DE SOLICITUDES DE DONACIÓN")
    print("=" * 55)
    
    # 1. Login
    print("👤 PASO 1: LOGIN")
    
    login_data = {
        "usernameOrEmail": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('token')
            user_info = login_result.get('user', {})
            
            print(f"✅ Login exitoso")
            print(f"  👤 Usuario: {user_info.get('username')}")
            print(f"  🏢 Organización: {user_info.get('organization')}")
            
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"   Respuesta: {login_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. Crear solicitud de donación
    print(f"\n📋 PASO 2: CREAR SOLICITUD DE DONACIÓN")
    
    donation_request_data = {
        "donations": [
            {
                "categoria": "ALIMENTOS",
                "descripcion": "Arroz y fideos",
                "cantidad": 50
            },
            {
                "categoria": "ROPA",
                "descripcion": "Abrigos de invierno",
                "cantidad": 20
            }
        ],
        "notes": "Solicitud urgente para evento de invierno"
    }
    
    try:
        print(f"📤 Enviando solicitud...")
        print(f"   Datos: {json.dumps(donation_request_data, indent=2)}")
        
        request_response = requests.post(f"{API_BASE}/messaging/create-donation-request", 
                                       json=donation_request_data, headers=headers)
        
        print(f"📨 Respuesta del servidor:")
        print(f"   Status Code: {request_response.status_code}")
        print(f"   Headers: {dict(request_response.headers)}")
        
        if request_response.status_code == 200:
            request_result = request_response.json()
            print(f"✅ Solicitud creada exitosamente")
            print(f"  📋 Request ID: {request_result.get('request_id')}")
            print(f"  💬 Mensaje: {request_result.get('message')}")
            
        else:
            print(f"❌ Error creando solicitud: {request_response.status_code}")
            try:
                error_data = request_response.json()
                print(f"   Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Error Text: {request_response.text}")
                
    except Exception as e:
        print(f"❌ Error en solicitud: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Verificar que el messaging service esté corriendo
    print(f"\n🔍 PASO 3: VERIFICAR MESSAGING SERVICE")
    
    try:
        messaging_health = requests.get("http://localhost:50054/health")
        
        if messaging_health.status_code == 200:
            health_data = messaging_health.json()
            print(f"✅ Messaging service está corriendo")
            print(f"   Status: {health_data.get('status')}")
        else:
            print(f"❌ Messaging service no responde: {messaging_health.status_code}")
            
    except Exception as e:
        print(f"❌ Error conectando a messaging service: {e}")
        print(f"   ¿Está corriendo en puerto 50054?")
    
    # 4. Probar directamente el messaging service
    print(f"\n🔗 PASO 4: PROBAR MESSAGING SERVICE DIRECTAMENTE")
    
    try:
        direct_request_data = {
            "donations": [
                {
                    "categoria": "ALIMENTOS",
                    "descripcion": "Prueba directa",
                    "cantidad": 10
                }
            ],
            "userId": user_info.get('id'),
            "notes": "Prueba directa al messaging service"
        }
        
        direct_response = requests.post("http://localhost:50054/api/createDonationRequest", 
                                      json=direct_request_data)
        
        print(f"📨 Respuesta directa del messaging service:")
        print(f"   Status Code: {direct_response.status_code}")
        
        if direct_response.status_code == 200:
            direct_result = direct_response.json()
            print(f"✅ Messaging service funciona correctamente")
            print(f"   Resultado: {json.dumps(direct_result, indent=2)}")
        else:
            print(f"❌ Error en messaging service: {direct_response.status_code}")
            try:
                error_data = direct_response.json()
                print(f"   Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Error Text: {direct_response.text}")
                
    except Exception as e:
        print(f"❌ Error probando messaging service directamente: {e}")
    
    print(f"\n🎉 TESTING COMPLETADO")

if __name__ == "__main__":
    test_donation_request_api()