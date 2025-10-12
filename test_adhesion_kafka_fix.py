#!/usr/bin/env python3
"""
Script para probar la corrección del envío de adhesiones a Kafka
"""

import requests
import json

def test_adhesion_creation():
    """Probar la creación de adhesiones con envío a Kafka"""
    
    print("=== Prueba de Creación de Adhesiones con Kafka ===")
    
    # Datos de prueba
    adhesion_data = {
        "eventId": "101",
        "targetOrganization": "fundacion-esperanza",
        "volunteerData": {
            "name": "Juan",
            "surname": "Pérez",
            "email": "juan.perez@test.com",
            "phone": "123456789"
        }
    }
    
    # Headers con token de autenticación (usar token real)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiIsImVtYWlsIjoiYWRtaW5AZW1wdWplLWNvbXVuaXRhcmlvLm9yZyIsInJvbGUiOiJQUkVTSURFTlRFIiwib3JnYW5pemF0aW9uIjoiZW1wdWplLWNvbXVuaXRhcmlvIiwiaWF0IjoxNzI4NjcxNzAyLCJleHAiOjE3Mjg2NzUzMDJ9.example"
    }
    
    try:
        print("1. Enviando solicitud de adhesión...")
        print(f"Datos: {json.dumps(adhesion_data, indent=2)}")
        
        # Llamar a la API
        response = requests.post(
            "http://localhost:3001/api/messaging/create-event-adhesion",
            json=adhesion_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Adhesión creada exitosamente")
                print(f"Mensaje: {result.get('message')}")
                return True
            else:
                print("❌ Error en la respuesta")
                print(f"Error: {result.get('error')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_messaging_service_direct():
    """Probar el servicio de messaging directamente"""
    
    print("\n=== Prueba Directa del Servicio de Messaging ===")
    
    adhesion_data = {
        "eventId": "101",
        "volunteerId": 1,
        "targetOrganization": "fundacion-esperanza",
        "volunteerData": {
            "name": "Juan",
            "surname": "Pérez",
            "email": "juan.perez@test.com",
            "phone": "123456789"
        }
    }
    
    try:
        print("1. Enviando solicitud directa al servicio de messaging...")
        print(f"Datos: {json.dumps(adhesion_data, indent=2)}")
        
        response = requests.post(
            "http://localhost:50054/api/createEventAdhesion",
            json=adhesion_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Adhesión creada exitosamente en messaging service")
                print(f"Mensaje: {result.get('message')}")
                return True
            else:
                print("❌ Error en la respuesta del messaging service")
                return False
        else:
            print(f"❌ Error HTTP en messaging service: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión con messaging service: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("Iniciando pruebas de adhesiones con Kafka...")
    
    # Probar API Gateway
    success1 = test_adhesion_creation()
    
    # Probar servicio directo
    success2 = test_messaging_service_direct()
    
    print(f"\n=== Resumen ===")
    print(f"API Gateway: {'✅ OK' if success1 else '❌ FALLO'}")
    print(f"Messaging Service: {'✅ OK' if success2 else '❌ FALLO'}")
    
    if success1 and success2:
        print("🎉 Todas las pruebas pasaron!")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar logs.")