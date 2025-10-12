#!/usr/bin/env python3
"""
Test completo del flujo de adhesiones
"""
import requests
import time
import mysql.connector

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

def create_test_event():
    """Crear evento de test"""
    print("📅 CREANDO EVENTO DE TEST")
    print("=" * 30)
    
    token_empuje, user_empuje = get_token('empuje-comunitario')
    headers = {'Authorization': f'Bearer {token_empuje}'}
    
    # Crear evento
    event_data = {
        "name": f"Test Adhesion Event {int(time.time())}",
        "description": "Evento para test de adhesiones",
        "date": "2025-12-25",
        "time": "10:00",
        "location": "Test Location",
        "maxParticipants": 10,
        "category": "SOCIAL"
    }
    
    response = requests.post(
        "http://localhost:3001/api/events",
        json=event_data,
        headers=headers
    )
    
    if response.status_code == 201:
        event = response.json()
        event_id = event.get('id')
        print(f"✅ Evento creado: ID {event_id}")
        
        # Exponer a la red
        expose_data = {
            "eventId": event_id,
            "expuesto_red": True
        }
        
        response = requests.post(
            "http://localhost:3001/api/messaging/toggle-event-exposure",
            json=expose_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Evento expuesto a la red")
            return event_id
        else:
            print(f"❌ Error exponiendo evento: {response.text}")
    else:
        print(f"❌ Error creando evento: {response.text}")
    
    return None

def test_adhesion_from_external_org(event_id):
    """Test adhesión desde organización externa"""
    print(f"\n👤 TESTING ADHESIÓN DESDE ESPERANZA-SOCIAL AL EVENTO {event_id}")
    print("=" * 60)
    
    token_esperanza, user_esperanza = get_token('esperanza-social')
    headers = {'Authorization': f'Bearer {token_esperanza}'}
    
    # Verificar que el evento aparece en eventos externos
    response = requests.post(
        "http://localhost:3001/api/messaging/external-events",
        headers=headers
    )
    
    if response.status_code == 200:
        events = response.json().get('events', [])
        target_event = None
        
        for event in events:
            if event.get('event_id') == event_id:
                target_event = event
                break
        
        if target_event:
            print(f"✅ Evento encontrado en lista externa: {target_event.get('name')}")
            
            # Crear adhesión
            adhesion_data = {
                "eventId": event_id,
                "targetOrganization": "empuje-comunitario",
                "volunteerData": {
                    "nombre": "Test Volunteer",
                    "email": "test@example.com",
                    "telefono": "123456789",
                    "experiencia": "Experiencia de test"
                }
            }
            
            response = requests.post(
                "http://localhost:3001/api/messaging/create-event-adhesion",
                json=adhesion_data,
                headers=headers
            )
            
            print(f"Status adhesión: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Adhesión creada exitosamente")
                return True
            else:
                print("❌ Error creando adhesión")
        else:
            print(f"❌ Evento {event_id} no encontrado en lista externa")
            print(f"Eventos disponibles: {[e.get('event_id') for e in events]}")
    else:
        print(f"❌ Error obteniendo eventos externos: {response.text}")
    
    return False

def test_adhesion_approval(event_id):
    """Test aprobación de adhesión"""
    print(f"\n✅ TESTING APROBACIÓN DE ADHESIÓN PARA EVENTO {event_id}")
    print("=" * 50)
    
    token_empuje, user_empuje = get_token('empuje-comunitario')
    headers = {'Authorization': f'Bearer {token_empuje}'}
    
    # Obtener adhesiones para el evento
    response = requests.post(
        "http://localhost:3001/api/messaging/event-adhesions",
        json={"eventId": event_id},
        headers=headers
    )
    
    print(f"Status event-adhesions: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        adhesions = data.get('adhesions', [])
        print(f"Adhesiones encontradas: {len(adhesions)}")
        
        pending_adhesions = [a for a in adhesions if a.get('status') == 'PENDIENTE']
        print(f"Adhesiones pendientes: {len(pending_adhesions)}")
        
        if pending_adhesions:
            adhesion = pending_adhesions[0]
            print(f"Aprobando adhesión ID: {adhesion.get('id')}")
            
            # Aquí debería haber un endpoint para aprobar/rechazar
            # Vamos a verificar si existe
            approval_data = {
                "adhesionId": adhesion.get('id'),
                "action": "approve"
            }
            
            # Intentar diferentes endpoints posibles
            endpoints_to_try = [
                "/api/messaging/approve-adhesion",
                "/api/messaging/update-adhesion-status",
                "/api/events/approve-adhesion"
            ]
            
            for endpoint in endpoints_to_try:
                response = requests.post(
                    f"http://localhost:3001{endpoint}",
                    json=approval_data,
                    headers=headers
                )
                print(f"Endpoint {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ Adhesión aprobada via {endpoint}")
                    return True
            
            print("❌ No se encontró endpoint de aprobación funcional")
        else:
            print("⚠️  No hay adhesiones pendientes")
    else:
        print(f"❌ Error obteniendo adhesiones: {response.text}")
    
    return False

def check_notifications():
    """Verificar notificaciones"""
    print("\n🔔 VERIFICANDO NOTIFICACIONES")
    print("=" * 30)
    
    # Verificar notificaciones para esperanza-social
    token_esperanza, user_esperanza = get_token('esperanza-social')
    headers = {'Authorization': f'Bearer {token_esperanza}'}
    
    response = requests.get("http://localhost:3001/api/notifications", headers=headers)
    
    if response.status_code == 200:
        notifications = response.json().get('notifications', [])
        adhesion_notifications = [
            n for n in notifications 
            if 'adhesion' in n.get('tipo', '').lower() or 'evento' in n.get('tipo', '').lower()
        ]
        
        print(f"Notificaciones de adhesión: {len(adhesion_notifications)}")
        
        for notif in adhesion_notifications[:3]:
            print(f"  - {notif.get('titulo')} ({notif.get('tipo')})")

if __name__ == "__main__":
    print("🔄 TEST COMPLETO DEL FLUJO DE ADHESIONES")
    print("=" * 60)
    
    # 1. Crear evento y exponerlo
    event_id = create_test_event()
    
    if event_id:
        # 2. Esperar un momento para que se propague
        time.sleep(2)
        
        # 3. Test adhesión desde org externa
        if test_adhesion_from_external_org(event_id):
            # 4. Test aprobación
            time.sleep(1)
            test_adhesion_approval(event_id)
            
            # 5. Verificar notificaciones
            check_notifications()
    else:
        print("❌ No se pudo crear evento de test")