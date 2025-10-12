#!/usr/bin/env python3
"""
Debug del sistema de adhesiones a eventos
"""
import requests
import mysql.connector
import json

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def get_token(org='empuje-comunitario'):
    """Obtener token"""
    if org == 'empuje-comunitario':
        login_data = {"usernameOrEmail": "admin", "password": "admin123"}
    else:
        login_data = {"usernameOrEmail": "admin_esperanza", "password": "admin123"}
    
    response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json().get('token'), response.json().get('user')
    return None, None

def check_database_structure():
    """Verificar estructura de la base de datos"""
    print("🔍 VERIFICANDO ESTRUCTURA DE BASE DE DATOS")
    print("=" * 50)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Verificar tablas relacionadas con adhesiones
        tables_to_check = [
            'eventos_red',
            'adhesiones_eventos_externos',
            'notificaciones'
        ]
        
        for table in tables_to_check:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            result = cursor.fetchone()
            if result:
                print(f"✅ Tabla {table} existe")
                
                # Mostrar estructura
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                print(f"   Columnas: {[col[0] for col in columns]}")
            else:
                print(f"❌ Tabla {table} NO existe")
        
        # Verificar datos de ejemplo
        print("\n📊 DATOS ACTUALES:")
        
        # Eventos en la red
        cursor.execute("SELECT COUNT(*) FROM eventos_red WHERE activo = true")
        eventos_red = cursor.fetchone()[0]
        print(f"Eventos activos en la red: {eventos_red}")
        
        # Adhesiones
        cursor.execute("SELECT COUNT(*) FROM adhesiones_eventos_externos")
        adhesiones = cursor.fetchone()[0]
        print(f"Adhesiones totales: {adhesiones}")
        
        # Adhesiones pendientes
        cursor.execute("SELECT COUNT(*) FROM adhesiones_eventos_externos WHERE estado = 'PENDIENTE'")
        pendientes = cursor.fetchone()[0]
        print(f"Adhesiones pendientes: {pendientes}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")

def test_event_exposure():
    """Test de exposición de eventos"""
    print("\n🌐 TESTING EXPOSICIÓN DE EVENTOS")
    print("=" * 40)
    
    # Login empuje-comunitario
    token_empuje, user_empuje = get_token('empuje-comunitario')
    if not token_empuje:
        print("❌ Error obteniendo token empuje-comunitario")
        return
    
    headers = {'Authorization': f'Bearer {token_empuje}'}
    
    # Obtener eventos externos
    response = requests.post(
        "http://localhost:3001/api/messaging/external-events",
        headers=headers
    )
    
    print(f"Status external-events: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        events = data.get('events', [])
        print(f"Eventos externos encontrados: {len(events)}")
        
        for event in events[:3]:
            print(f"  - {event.get('name')} (Org: {event.get('source_organization')})")
    else:
        print(f"❌ Error: {response.text}")

def test_adhesion_creation():
    """Test de creación de adhesión"""
    print("\n📝 TESTING CREACIÓN DE ADHESIÓN")
    print("=" * 40)
    
    # Login esperanza-social (para adherirse a evento de empuje)
    token_esperanza, user_esperanza = get_token('esperanza-social')
    if not token_esperanza:
        print("❌ Error obteniendo token esperanza-social")
        return
    
    headers = {'Authorization': f'Bearer {token_esperanza}'}
    
    # Primero obtener eventos externos
    response = requests.post(
        "http://localhost:3001/api/messaging/external-events",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        events = data.get('events', [])
        
        if events:
            # Intentar adhesión al primer evento
            event = events[0]
            print(f"Intentando adhesión a: {event.get('name')}")
            
            adhesion_data = {
                "eventId": event.get('event_id'),
                "targetOrganization": event.get('source_organization'),
                "volunteerData": {
                    "nombre": "Test Volunteer",
                    "email": "test@example.com",
                    "telefono": "123456789",
                    "experiencia": "Test experience"
                }
            }
            
            response = requests.post(
                "http://localhost:3001/api/messaging/create-event-adhesion",
                json=adhesion_data,
                headers=headers
            )
            
            print(f"Status create-adhesion: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Adhesión creada exitosamente")
            else:
                print("❌ Error creando adhesión")
        else:
            print("❌ No hay eventos externos disponibles")
    else:
        print(f"❌ Error obteniendo eventos externos: {response.text}")

def test_adhesion_approval():
    """Test de aprobación de adhesiones"""
    print("\n✅ TESTING APROBACIÓN DE ADHESIONES")
    print("=" * 40)
    
    # Login empuje-comunitario (para aprobar adhesiones)
    token_empuje, user_empuje = get_token('empuje-comunitario')
    if not token_empuje:
        print("❌ Error obteniendo token empuje-comunitario")
        return
    
    headers = {'Authorization': f'Bearer {token_empuje}'}
    
    # Obtener adhesiones pendientes
    response = requests.post(
        "http://localhost:3001/api/messaging/event-adhesions",
        json={"eventId": 1},  # Usar ID de evento de ejemplo
        headers=headers
    )
    
    print(f"Status event-adhesions: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    print("🔧 DIAGNÓSTICO DEL SISTEMA DE ADHESIONES")
    print("=" * 60)
    
    check_database_structure()
    test_event_exposure()
    test_adhesion_creation()
    test_adhesion_approval()