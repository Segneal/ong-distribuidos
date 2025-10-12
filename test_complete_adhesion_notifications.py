#!/usr/bin/env python3
"""
Test completo del sistema de notificaciones de adhesiones
"""
import requests
import time

def get_token(org='empuje-comunitario'):
    """Obtener token"""
    if org == 'empuje-comunitario':
        login_data = {"usernameOrEmail": "admin", "password": "admin123"}
    elif org == 'esperanza-social':
        login_data = {"usernameOrEmail": "admin_esperanza", "password": "admin123"}
    elif org == 'fundacion-esperanza':
        login_data = {"usernameOrEmail": "esperanza_admin", "password": "admin123"}
    
    response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json().get('token'), response.json().get('user')
    return None, None

def test_complete_adhesion_notification_flow():
    """Test completo del flujo de notificaciones"""
    print("🔔 TEST COMPLETO DE NOTIFICACIONES DE ADHESIONES")
    print("=" * 60)
    
    # 1. Verificar notificaciones iniciales de fundacion-esperanza
    print("\\n📊 ESTADO INICIAL DE NOTIFICACIONES")
    token_fundacion, user_fundacion = get_token('fundacion-esperanza')
    
    if not token_fundacion:
        print("❌ Error login fundacion-esperanza")
        return
    
    headers_fundacion = {'Authorization': f'Bearer {token_fundacion}'}
    
    response = requests.get("http://localhost:3001/api/notifications", headers=headers_fundacion)
    
    initial_count = 0
    if response.status_code == 200:
        notifications = response.json().get('notifications', [])
        initial_count = len(notifications)
        print(f"Notificaciones iniciales: {initial_count}")
        
        unread_count = len([n for n in notifications if not n.get('leida')])
        print(f"No leídas: {unread_count}")
    else:
        print(f"❌ Error obteniendo notificaciones: {response.text}")
        return
    
    # 2. Crear adhesión desde esperanza-social
    print("\\n👤 CREANDO ADHESIÓN DESDE ESPERANZA-SOCIAL")
    token_esperanza, user_esperanza = get_token('esperanza-social')
    
    if not token_esperanza:
        print("❌ Error login esperanza-social")
        return
    
    headers_esperanza = {'Authorization': f'Bearer {token_esperanza}'}
    
    # Crear adhesión a evento 27 (de fundacion-esperanza)
    adhesion_data = {
        "eventId": 27,
        "targetOrganization": "fundacion-esperanza",
        "volunteerData": {
            "nombre": f"Test Notification {int(time.time())}",
            "email": "test.notification@example.com",
            "telefono": "555666777",
            "experiencia": "Test completo de notificaciones"
        }
    }
    
    response = requests.post(
        "http://localhost:3001/api/messaging/create-event-adhesion",
        json=adhesion_data,
        headers=headers_esperanza
    )
    
    print(f"Status crear adhesión: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        print("❌ No se pudo crear adhesión")
        return
    
    print("✅ Adhesión creada exitosamente")
    
    # 3. Verificar nueva notificación en fundacion-esperanza
    print("\\n🔔 VERIFICANDO NUEVA NOTIFICACIÓN")
    time.sleep(1)  # Esperar un momento
    
    response = requests.get("http://localhost:3001/api/notifications", headers=headers_fundacion)
    
    if response.status_code == 200:
        notifications = response.json().get('notifications', [])
        new_count = len(notifications)
        
        print(f"Notificaciones después: {new_count}")
        print(f"Nuevas notificaciones: {new_count - initial_count}")
        
        if new_count > initial_count:
            # Mostrar la nueva notificación
            latest_notification = notifications[0]
            print(f"\\n📩 NUEVA NOTIFICACIÓN:")
            print(f"  Título: {latest_notification.get('titulo')}")
            print(f"  Mensaje: {latest_notification.get('mensaje')}")
            print(f"  Tipo: {latest_notification.get('tipo')}")
            print(f"  Fecha: {latest_notification.get('fecha_creacion')}")
            print(f"  Leída: {latest_notification.get('leida')}")
            
            if 'adhesion' in latest_notification.get('tipo', '').lower() or 'solicitud' in latest_notification.get('titulo', '').lower():
                print("✅ ¡NOTIFICACIÓN DE ADHESIÓN CREADA CORRECTAMENTE!")
            else:
                print("⚠️  Nueva notificación pero no es de adhesión")
        else:
            print("❌ No se creó nueva notificación")
    else:
        print(f"❌ Error verificando notificaciones: {response.text}")
    
    # 4. Test aprobación y notificación al voluntario
    print("\\n✅ TESTING APROBACIÓN Y NOTIFICACIÓN AL VOLUNTARIO")
    
    # Obtener adhesiones pendientes
    response = requests.post(
        "http://localhost:3001/api/messaging/event-adhesions",
        json={"eventId": 27},
        headers=headers_fundacion
    )
    
    if response.status_code == 200:
        adhesions = response.json().get('adhesions', [])
        pending = [a for a in adhesions if a.get('status') == 'PENDIENTE']
        
        if pending:
            # Aprobar la primera adhesión pendiente
            adhesion_to_approve = pending[0]
            
            response = requests.post(
                "http://localhost:3001/api/messaging/approve-event-adhesion",
                json={"adhesionId": adhesion_to_approve.get('id')},
                headers=headers_fundacion
            )
            
            print(f"Status aprobación: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Adhesión aprobada")
                
                # Verificar notificación al voluntario
                time.sleep(1)
                
                response = requests.get("http://localhost:3001/api/notifications", headers=headers_esperanza)
                
                if response.status_code == 200:
                    volunteer_notifications = response.json().get('notifications', [])
                    
                    approval_notifications = [
                        n for n in volunteer_notifications 
                        if 'aprobada' in n.get('titulo', '').lower()
                    ]
                    
                    if approval_notifications:
                        latest_approval = approval_notifications[0]
                        print(f"\\n📩 NOTIFICACIÓN DE APROBACIÓN AL VOLUNTARIO:")
                        print(f"  Título: {latest_approval.get('titulo')}")
                        print(f"  Mensaje: {latest_approval.get('mensaje')}")
                        print("✅ ¡NOTIFICACIÓN DE APROBACIÓN FUNCIONANDO!")
                    else:
                        print("❌ No se encontró notificación de aprobación")
            else:
                print(f"❌ Error aprobando: {response.text}")
        else:
            print("⚠️  No hay adhesiones pendientes")
    else:
        print(f"❌ Error obteniendo adhesiones: {response.text}")

if __name__ == "__main__":
    test_complete_adhesion_notification_flow()