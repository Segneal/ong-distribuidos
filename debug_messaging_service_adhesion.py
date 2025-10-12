#!/usr/bin/env python3
"""
Debug del messaging service para adhesiones
"""
import requests

def test_messaging_service():
    """Test del messaging service"""
    print("🔧 TESTING MESSAGING SERVICE")
    print("=" * 40)
    
    # Test básico de conectividad
    try:
        response = requests.get("http://localhost:50054/health", timeout=5)
        print(f"Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Error conectando al messaging service: {e}")
        return False
    
    # Test endpoint de adhesión directamente
    adhesion_data = {
        "eventId": 27,
        "volunteerId": 26,  # ID del usuario esperanza
        "targetOrganization": "fundacion-esperanza",
        "volunteerData": {
            "nombre": "Test Direct",
            "email": "test.direct@example.com",
            "telefono": "123456789",
            "experiencia": "Test directo"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:50054/api/createEventAdhesion",
            json=adhesion_data,
            timeout=10
        )
        print(f"Direct adhesion - Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Messaging service funcionando")
            return True
        else:
            print("❌ Error en messaging service")
    except Exception as e:
        print(f"❌ Error llamando messaging service: {e}")
    
    return False

def test_direct_db_adhesion():
    """Test creación directa en DB"""
    print("\n💾 TESTING CREACIÓN DIRECTA EN DB")
    print("=" * 40)
    
    import mysql.connector
    import json
    from datetime import datetime
    
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root',
        'database': 'ong_management'
    }
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Crear adhesión directamente
        volunteer_data = {
            "nombre": "Test DB Direct",
            "email": "test.db@example.com",
            "telefono": "555666777",
            "experiencia": "Test DB directo"
        }
        
        cursor.execute("""
            INSERT INTO adhesiones_eventos_externos 
            (evento_externo_id, voluntario_id, fecha_adhesion, estado, datos_voluntario)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            27,  # event_id
            26,  # volunteer_id (esperanza admin)
            datetime.now(),
            'PENDIENTE',
            json.dumps(volunteer_data)
        ))
        
        adhesion_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Adhesión creada directamente en DB: ID {adhesion_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error creando adhesión en DB: {e}")
        return False

def test_adhesion_approval_endpoints():
    """Test endpoints de aprobación"""
    print("\n✅ TESTING ENDPOINTS DE APROBACIÓN")
    print("=" * 40)
    
    # Login fundacion-esperanza (dueña del evento 27)
    login_data = {"usernameOrEmail": "admin_fundacion", "password": "admin123"}
    response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("❌ Error login fundacion-esperanza")
        return
    
    token = response.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Obtener adhesiones
    response = requests.post(
        "http://localhost:3001/api/messaging/event-adhesions",
        json={"eventId": 27},
        headers=headers
    )
    
    print(f"Event adhesions - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        adhesions = data.get('adhesions', [])
        print(f"Adhesiones encontradas: {len(adhesions)}")
        
        pending = [a for a in adhesions if a.get('status') == 'PENDIENTE']
        print(f"Adhesiones pendientes: {len(pending)}")
        
        if pending:
            # Intentar aprobar una
            adhesion = pending[0]
            print(f"Intentando aprobar adhesión ID: {adhesion.get('id')}")
            
            # Buscar endpoint de aprobación
            endpoints = [
                "/api/messaging/approve-adhesion",
                "/api/messaging/update-adhesion-status",
                "/api/events/approve-adhesion",
                "/api/adhesions/approve"
            ]
            
            for endpoint in endpoints:
                approval_data = {
                    "adhesionId": adhesion.get('id'),
                    "action": "approve",
                    "status": "CONFIRMADA"
                }
                
                response = requests.post(
                    f"http://localhost:3001{endpoint}",
                    json=approval_data,
                    headers=headers
                )
                
                print(f"  {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"  ✅ Funciona: {response.text}")
                elif response.status_code != 404:
                    print(f"  ⚠️  Error: {response.text}")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    print("🔧 DEBUG COMPLETO DEL SISTEMA DE ADHESIONES")
    print("=" * 60)
    
    # 1. Test messaging service
    messaging_ok = test_messaging_service()
    
    # 2. Si messaging service falla, crear adhesión directa
    if not messaging_ok:
        test_direct_db_adhesion()
    
    # 3. Test endpoints de aprobación
    test_adhesion_approval_endpoints()