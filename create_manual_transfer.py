#!/usr/bin/env python3
"""
Crear transferencia manual para testing
"""
import mysql.connector
import json
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def create_manual_transfer():
    """Crear transferencia manual RECIBIDA para esperanza-social"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Crear transferencia RECIBIDA para esperanza-social
        donations_data = [
            {
                "categoria": "ALIMENTOS",
                "descripcion": "Test manual transfer",
                "cantidad": "5 unidades"
            }
        ]
        
        cursor.execute("""
            INSERT INTO transferencias_donaciones 
            (tipo, organizacion_contraparte, solicitud_id, donaciones, estado, fecha_transferencia, usuario_registro, notas, organizacion_propietaria)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            'RECIBIDA',
            'empuje-comunitario',
            'manual-test-request',
            json.dumps(donations_data),
            'COMPLETADA',
            datetime.now(),
            26,  # admin_esperanza
            'Transferencia manual para testing',
            'esperanza-social'  # esperanza-social es la propietaria
        ))
        
        conn.commit()
        transfer_id = cursor.lastrowid
        
        print(f"✅ Transferencia manual creada con ID: {transfer_id}")
        
        # Crear notificación manual también
        cursor.execute("""
            INSERT INTO notificaciones 
            (usuario_id, tipo, titulo, mensaje, datos_adicionales, leida, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, false, NOW())
        """, (
            26,  # admin_esperanza
            'transferencia_recibida',
            '🎁 ¡Donación recibida!',
            'Has recibido una transferencia manual de prueba de Empuje Comunitario',
            json.dumps({
                'organizacion_origen': 'empuje-comunitario',
                'request_id': 'manual-test-request',
                'cantidad_items': 1
            })
        ))
        
        conn.commit()
        notification_id = cursor.lastrowid
        
        print(f"✅ Notificación manual creada con ID: {notification_id}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_transfer_history_api():
    """Test del API de historial después de crear transferencia manual"""
    import requests
    
    # Login como esperanza
    login_data = {
        "usernameOrEmail": "admin_esperanza",
        "password": "admin123"
    }
    
    try:
        response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('token')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test historial
            response = requests.post(
                "http://localhost:50054/api/getTransferHistory",
                json={"organizationId": "esperanza-social", "limit": 10},
                headers=headers
            )
            
            print(f"\nHistorial Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Test notificaciones
            response = requests.get(
                "http://localhost:3001/api/notifications",
                headers=headers
            )
            
            print(f"\nNotificaciones Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🔧 CREANDO TRANSFERENCIA MANUAL")
    print("=" * 40)
    
    if create_manual_transfer():
        test_transfer_history_api()
    
    print("\n🏁 COMPLETADO")