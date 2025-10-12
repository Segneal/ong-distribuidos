#!/usr/bin/env python3
"""
Debug de notificaciones de adhesiones
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

def check_notification_tables():
    """Verificar estructura de tablas de notificaciones"""
    print("🔍 VERIFICANDO TABLAS DE NOTIFICACIONES")
    print("=" * 50)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Verificar qué tablas de notificaciones existen
        cursor.execute("SHOW TABLES LIKE '%notif%'")
        tables = cursor.fetchall()
        
        print("Tablas de notificaciones encontradas:")
        for table in tables:
            print(f"  - {table[0]}")
            
            # Mostrar estructura
            cursor.execute(f"DESCRIBE {table[0]}")
            columns = cursor.fetchall()
            print(f"    Columnas: {[col[0] for col in columns]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def check_adhesion_notifications():
    """Verificar notificaciones de adhesiones"""
    print("\n📋 VERIFICANDO NOTIFICACIONES DE ADHESIONES")
    print("=" * 50)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Verificar notificaciones en la tabla principal
        cursor.execute("""
            SELECT * FROM notificaciones 
            WHERE tipo LIKE '%adhesion%' OR mensaje LIKE '%adhesion%' OR mensaje LIKE '%evento%'
            ORDER BY fecha_creacion DESC
            LIMIT 10
        """)
        
        notifications = cursor.fetchall()
        print(f"Notificaciones de adhesión en tabla 'notificaciones': {len(notifications)}")
        
        for notif in notifications:
            print(f"  - ID: {notif['id']}")
            print(f"    Usuario: {notif['usuario_id']}")
            print(f"    Tipo: {notif['tipo']}")
            print(f"    Título: {notif['titulo']}")
            print(f"    Leída: {notif['leida']}")
            print()
        
        # Verificar si existe tabla notificaciones_usuarios
        cursor.execute("SHOW TABLES LIKE 'notificaciones_usuarios'")
        if cursor.fetchone():
            cursor.execute("""
                SELECT * FROM notificaciones_usuarios 
                WHERE tipo LIKE '%adhesion%' OR mensaje LIKE '%adhesion%' OR mensaje LIKE '%evento%'
                ORDER BY fecha_creacion DESC
                LIMIT 10
            """)
            
            user_notifications = cursor.fetchall()
            print(f"Notificaciones en tabla 'notificaciones_usuarios': {len(user_notifications)}")
            
            for notif in user_notifications:
                print(f"  - ID: {notif.get('id')}")
                print(f"    Usuario: {notif.get('usuario_id')}")
                print(f"    Tipo: {notif.get('tipo')}")
                print(f"    Título: {notif.get('titulo')}")
                print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_create_adhesion_and_check_notification():
    """Test crear adhesión y verificar notificación"""
    print("\n🧪 TEST: CREAR ADHESIÓN Y VERIFICAR NOTIFICACIÓN")
    print("=" * 60)
    
    # 1. Login esperanza-social (para crear adhesión)
    login_data = {"usernameOrEmail": "admin_esperanza", "password": "admin123"}
    response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Error login esperanza: {response.text}")
        return
    
    token_esperanza = response.json().get('token')
    headers_esperanza = {'Authorization': f'Bearer {token_esperanza}'}
    
    # 2. Crear adhesión a evento de fundacion-esperanza
    adhesion_data = {
        "eventId": 27,  # Evento de fundacion-esperanza
        "targetOrganization": "fundacion-esperanza",
        "volunteerData": {
            "nombre": "Test Notification",
            "email": "test.notification@example.com",
            "telefono": "111222333",
            "experiencia": "Test para verificar notificaciones"
        }
    }
    
    print("Creando adhesión...")
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
    
    # 3. Verificar si se creó notificación para fundacion-esperanza
    print("\n🔔 Verificando notificaciones para fundacion-esperanza...")
    
    # Login fundacion-esperanza
    login_data = {"usernameOrEmail": "esperanza_admin", "password": "admin123"}
    response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Error login fundacion: {response.text}")
        return
    
    token_fundacion = response.json().get('token')
    headers_fundacion = {'Authorization': f'Bearer {token_fundacion}'}
    
    # Obtener notificaciones via API
    response = requests.get("http://localhost:3001/api/notifications", headers=headers_fundacion)
    
    print(f"Status notificaciones API: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        notifications = data.get('notifications', [])
        print(f"Notificaciones via API: {len(notifications)}")
        
        # Buscar notificaciones recientes de adhesión
        recent_adhesion_notifs = [
            n for n in notifications 
            if 'adhesion' in n.get('tipo', '').lower() or 'evento' in n.get('mensaje', '').lower()
        ]
        
        print(f"Notificaciones de adhesión: {len(recent_adhesion_notifs)}")
        
        for notif in recent_adhesion_notifs[:3]:
            print(f"  - {notif.get('titulo')}")
            print(f"    Tipo: {notif.get('tipo')}")
            print(f"    Fecha: {notif.get('fecha_creacion')}")
    else:
        print(f"❌ Error obteniendo notificaciones: {response.text}")
    
    # 4. Verificar directamente en base de datos
    print("\n💾 Verificando directamente en base de datos...")
    check_adhesion_notifications()

def test_notification_creation_when_adhesion_created():
    """Test específico de creación de notificación"""
    print("\n🔧 VERIFICANDO CREACIÓN DE NOTIFICACIÓN AL CREAR ADHESIÓN")
    print("=" * 60)
    
    # Verificar el código del endpoint create-event-adhesion
    print("El problema puede estar en:")
    print("1. El endpoint create-event-adhesion no crea notificación")
    print("2. La notificación se crea en tabla incorrecta")
    print("3. El usuario destinatario no es el correcto")
    print("4. El API de notificaciones no lee de la tabla correcta")

if __name__ == "__main__":
    print("🔔 DEBUG COMPLETO DE NOTIFICACIONES DE ADHESIONES")
    print("=" * 70)
    
    check_notification_tables()
    check_adhesion_notifications()
    test_create_adhesion_and_check_notification()
    test_notification_creation_when_adhesion_created()