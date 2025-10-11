#!/usr/bin/env python3
"""
Script para probar directamente el messaging-service
"""
import requests
import json

def test_messaging_service_direct():
    """Prueba directamente el messaging-service"""
    
    # Configuración
    MESSAGING_URL = "http://localhost:50054"
    
    try:
        print("=== PROBANDO MESSAGING-SERVICE DIRECTAMENTE ===\n")
        
        # 1. Health check
        print("1. Health check...")
        health_response = requests.get(f"{MESSAGING_URL}/health")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Messaging-service está corriendo")
            print(f"   Organization ID: {health_data.get('organization_id')}")
        else:
            print(f"❌ Error en health check: {health_response.status_code}")
            return False
        
        # 2. Probar creación con organización específica
        print("\n2. Probando creación con userOrganization...")
        
        test_data = {
            "donations": [
                {"category": "ROPA", "description": "Prueba directa messaging-service"}
            ],
            "userId": 17,  # ID del usuario esperanza_admin
            "userOrganization": "fundacion-esperanza",
            "notes": "Prueba directa del messaging-service"
        }
        
        create_response = requests.post(
            f"{MESSAGING_URL}/api/createDonationRequest",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        
        if create_response.status_code in [200, 201]:
            response_data = create_response.json()
            request_id = response_data.get('request_id')
            print(f"✅ Solicitud creada: {request_id}")
            
            # Verificar si el ID tiene el prefijo correcto
            if request_id and request_id.startswith('req-fundacion-esperanza-'):
                print("✅ ID de solicitud tiene el prefijo correcto")
            else:
                print(f"❌ ID de solicitud tiene prefijo incorrecto: {request_id}")
                
        else:
            print(f"❌ Error creando solicitud: {create_response.status_code}")
            return False
        
        # 3. Probar sin userOrganization (debería usar configuración por defecto)
        print("\n3. Probando sin userOrganization...")
        
        test_data_no_org = {
            "donations": [
                {"category": "ALIMENTOS", "description": "Prueba sin organización"}
            ],
            "userId": 11,  # ID del usuario admin
            "notes": "Prueba sin userOrganization"
        }
        
        create_response2 = requests.post(
            f"{MESSAGING_URL}/api/createDonationRequest",
            json=test_data_no_org,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {create_response2.status_code}")
        print(f"Response: {create_response2.text}")
        
        if create_response2.status_code in [200, 201]:
            response_data2 = create_response2.json()
            request_id2 = response_data2.get('request_id')
            print(f"✅ Solicitud creada: {request_id2}")
            
            # Verificar si usa el prefijo por defecto
            if request_id2 and request_id2.startswith('req-empuje-comunitario-'):
                print("✅ ID de solicitud usa el prefijo por defecto correcto")
            else:
                print(f"❌ ID de solicitud no usa el prefijo por defecto: {request_id2}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está corriendo el messaging-service en el puerto 8000?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    if test_messaging_service_direct():
        print("\n🎉 Prueba directa del messaging-service completada!")
    else:
        print("\n❌ Prueba directa del messaging-service falló")