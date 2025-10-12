#!/usr/bin/env python3
"""
Simular transferencia completa con notificaciones
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

def simulate_complete_transfer():
    """Simular transferencia completa"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 1. Crear transferencia ENVIADA para empuje-comunitario
        donations_data = [
            {
                "categoria": "ALIMENTOS",
                "descripcion": "Arroz integral simulado",
                "cantidad": "10 kg",
                "inventoryId": 12
            }
        ]
        
        cursor.execute("""
            INSERT INTO transferencias_donaciones 
            (tipo, organizacion_contraparte, solicitud_id, donaciones, estado, fecha_transferencia, usuario_registro, notas, organizacion_propietaria)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            'ENVIADA',
            'esperanza-social',
            'simulated-request-001',
            json.dumps(donations_data),
            'COMPLETADA',
            datetime.now(),
            11,  # admin empuje-comunitario
            'Transferencia simulada completa',
            'empuje-comunitario'
        ))
        
        enviada_id = cursor.lastrowid
        print(f"✅ Transferencia ENVIADA creada: ID {enviada_id}")
        
        # 2. Crear transferencia RECIBIDA para esperanza-social
        cursor.execute("""
            INSERT INTO transferencias_donaciones 
            (tipo, organizacion_contraparte, solicitud_id, donaciones, estado, fecha_transferencia, usuario_registro, notas, organizacion_propietaria)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            'RECIBIDA',
            'empuje-comunitario',
            'simulated-request-001',
            json.dumps(donations_data),
            'COMPLETADA',
            datetime.now(),
            26,  # admin_esperanza
            'Transferencia simulada recibida',
            'esperanza-social'
        ))
        
        recibida_id = cursor.lastrowid
        print(f"✅ Transferencia RECIBIDA creada: ID {recibida_id}")
        
        # 3. Crear notificación para el que envió (empuje-comunitario)
        cursor.execute("""
            INSERT INTO notificaciones 
            (usuario_id, tipo, titulo, mensaje, datos_adicionales, leida, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, false, NOW())
        """, (
            11,  # admin empuje-comunitario
            'transferencia_enviada',
            '📤 Donación enviada',
            'Has enviado donaciones a Esperanza Social exitosamente. Las donaciones han sido entregadas.',
            json.dumps({
                'organizacion_destino': 'esperanza-social',
                'request_id': 'simulated-request-001',
                'cantidad_items': 1
            })
        ))
        
        notif_enviada_id = cursor.lastrowid
        print(f"✅ Notificación ENVIADA creada: ID {notif_enviada_id}")
        
        # 4. Crear notificación para el que recibió (esperanza-social)
        cursor.execute("""
            INSERT INTO notificaciones 
            (usuario_id, tipo, titulo, mensaje, datos_adicionales, leida, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, false, NOW())
        """, (
            26,  # admin_esperanza
            'transferencia_recibida',
            '🎁 ¡Donación recibida!',
            'Has recibido donaciones de Empuje Comunitario. Las donaciones ya están disponibles en tu inventario.',
            json.dumps({
                'organizacion_origen': 'empuje-comunitario',
                'request_id': 'simulated-request-001',
                'cantidad_items': 1
            })
        ))
        
        notif_recibida_id = cursor.lastrowid
        print(f"✅ Notificación RECIBIDA creada: ID {notif_recibida_id}")
        
        # 5. Agregar donaciones al inventario de esperanza-social (simular)
        # Nota: En un sistema real, esto se haría en el consumer
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎉 TRANSFERENCIA COMPLETA SIMULADA")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_apis_after_simulation():
    """Test de APIs después de la simulación"""
    import requests
    
    print("\n=== TESTING APIS DESPUÉS DE SIMULACIÓN ===")
    
    # Test historial para empuje-comunitario
    try:
        response = requests.post(
            "http://localhost:50054/api/getTransferHistory",
            json={"organizationId": "empuje-comunitario", "limit": 5}
        )
        
        print(f"Empuje Comunitario - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            transfers = data.get('transfers', [])
            print(f"Transferencias: {len(transfers)}")
        
    except Exception as e:
        print(f"Error Empuje: {e}")
    
    # Test historial para esperanza-social
    try:
        response = requests.post(
            "http://localhost:50054/api/getTransferHistory",
            json={"organizationId": "esperanza-social", "limit": 5}
        )
        
        print(f"Esperanza Social - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            transfers = data.get('transfers', [])
            print(f"Transferencias: {len(transfers)}")
        
    except Exception as e:
        print(f"Error Esperanza: {e}")
    
    # Test notificaciones para esperanza-social
    login_data = {
        "usernameOrEmail": "admin_esperanza",
        "password": "admin123"
    }
    
    try:
        response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('token')
            headers = {'Authorization': f'Bearer {token}'}
            
            response = requests.get(
                "http://localhost:3001/api/notifications",
                headers=headers
            )
            
            print(f"Notificaciones Esperanza - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('notifications', [])
                print(f"Notificaciones: {len(notifications)}")
                
                for notif in notifications[:2]:  # Mostrar las primeras 2
                    print(f"  - {notif.get('titulo')}")
        
    except Exception as e:
        print(f"Error notificaciones: {e}")

if __name__ == "__main__":
    print("🎭 SIMULANDO TRANSFERENCIA COMPLETA")
    print("=" * 50)
    
    if simulate_complete_transfer():
        test_apis_after_simulation()
    
    print("\n🏁 SIMULACIÓN COMPLETADA")