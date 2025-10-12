#!/usr/bin/env python3
"""
Debug script para verificar el flujo completo de donaciones recibidas
"""
import requests
import json
import mysql.connector
from datetime import datetime

# Configuración
API_BASE = "http://localhost:3001/api"
MESSAGING_BASE = "http://localhost:50054/api"
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def get_db_connection():
    """Obtener conexión a la base de datos"""
    return mysql.connector.connect(**DB_CONFIG)

def check_transfer_history_api():
    """Verificar el endpoint de historial de transferencias"""
    print("\n=== VERIFICANDO API DE HISTORIAL DE TRANSFERENCIAS ===")
    
    # Simular token de Esperanza
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjMsInVzZXJuYW1lIjoiYWRtaW5fZXNwZXJhbnphIiwib3JnYW5pemF0aW9uIjoiZXNwZXJhbnphLXNvY2lhbCIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTczNDEwNzI5NCwiZXhwIjoxNzM0MTA4MTk0fQ.example'
    }
    
    try:
        # Probar endpoint directo del messaging service
        response = requests.post(
            f"{MESSAGING_BASE}/getTransferHistory",
            json={"organizationId": "esperanza-social", "limit": 50},
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            transfers = data.get('transfers', [])
            print(f"Transferencias encontradas: {len(transfers)}")
            
            for transfer in transfers:
                print(f"  - ID: {transfer.get('id')}")
                print(f"    Origen: {transfer.get('organizacion_origen')}")
                print(f"    Destino: {transfer.get('organizacion_destino')}")
                print(f"    Fecha: {transfer.get('fecha_transferencia')}")
                print(f"    Donaciones: {len(transfer.get('donaciones', []))}")
        
    except Exception as e:
        print(f"Error: {e}")

def check_database_transfers():
    """Verificar transferencias en la base de datos"""
    print("\n=== VERIFICANDO TRANSFERENCIAS EN BASE DE DATOS ===")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar tabla transferencias_donaciones
        cursor.execute("""
            SELECT * FROM transferencias_donaciones 
            WHERE organizacion_destino = 'esperanza-social' 
            ORDER BY fecha_transferencia DESC
        """)
        
        transfers = cursor.fetchall()
        print(f"Transferencias recibidas por Esperanza: {len(transfers)}")
        
        for transfer in transfers:
            print(f"  - ID: {transfer['id']}")
            print(f"    Origen: {transfer['organizacion_origen']}")
            print(f"    Destino: {transfer['organizacion_destino']}")
            print(f"    Fecha: {transfer['fecha_transferencia']}")
            print(f"    Request ID: {transfer['request_id']}")
            print(f"    Usuario: {transfer['usuario_id']}")
            
            # Verificar donaciones asociadas
            cursor.execute("""
                SELECT * FROM donaciones_transferidas 
                WHERE transferencia_id = %s
            """, (transfer['id'],))
            
            donations = cursor.fetchall()
            print(f"    Donaciones: {len(donations)}")
            
            for donation in donations:
                print(f"      - {donation['nombre']}: {donation['cantidad']} {donation['unidad']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error en base de datos: {e}")

def check_notifications_api():
    """Verificar notificaciones"""
    print("\n=== VERIFICANDO NOTIFICACIONES ===")
    
    # Token de usuario de Esperanza
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjMsInVzZXJuYW1lIjoiYWRtaW5fZXNwZXJhbnphIiwib3JnYW5pemF0aW9uIjoiZXNwZXJhbnphLXNvY2lhbCIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTczNDEwNzI5NCwiZXhwIjoxNzM0MTA4MTk0fQ.example'
    }
    
    try:
        response = requests.get(
            f"{API_BASE}/notifications",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            notifications = data.get('notifications', [])
            print(f"Notificaciones encontradas: {len(notifications)}")
            
            for notif in notifications:
                print(f"  - Tipo: {notif.get('tipo')}")
                print(f"    Mensaje: {notif.get('mensaje')}")
                print(f"    Fecha: {notif.get('fecha_creacion')}")
                print(f"    Leída: {notif.get('leida')}")
        
    except Exception as e:
        print(f"Error: {e}")

def check_database_notifications():
    """Verificar notificaciones en la base de datos"""
    print("\n=== VERIFICANDO NOTIFICACIONES EN BASE DE DATOS ===")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar notificaciones para usuarios de Esperanza
        cursor.execute("""
            SELECT n.*, u.username, u.organizacion 
            FROM notificaciones n
            JOIN usuarios u ON n.usuario_id = u.id
            WHERE u.organizacion = 'esperanza-social'
            AND n.tipo = 'transferencia_recibida'
            ORDER BY n.fecha_creacion DESC
        """)
        
        notifications = cursor.fetchall()
        print(f"Notificaciones de transferencia para Esperanza: {len(notifications)}")
        
        for notif in notifications:
            print(f"  - ID: {notif['id']}")
            print(f"    Usuario: {notif['username']} ({notif['organizacion']})")
            print(f"    Tipo: {notif['tipo']}")
            print(f"    Mensaje: {notif['mensaje']}")
            print(f"    Fecha: {notif['fecha_creacion']}")
            print(f"    Leída: {notif['leida']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error en base de datos: {e}")

def simulate_transfer():
    """Simular una transferencia para probar el flujo"""
    print("\n=== SIMULANDO TRANSFERENCIA ===")
    
    # Token de usuario de Empuje Comunitario
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEsInVzZXJuYW1lIjoiYWRtaW4iLCJvcmdhbml6YXRpb24iOiJlbXB1amUtY29tdW5pdGFyaW8iLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3MzQxMDcyOTQsImV4cCI6MTczNDEwODE5NH0.example'
    }
    
    transfer_data = {
        "targetOrganization": "esperanza-social",
        "requestId": "test-request-" + str(int(datetime.now().timestamp())),
        "donations": [
            {
                "nombre": "Arroz de prueba",
                "cantidad": 10,
                "unidad": "kg",
                "categoria": "Alimentos",
                "descripcion": "Transferencia de prueba"
            }
        ],
        "userId": 1
    }
    
    try:
        response = requests.post(
            f"{MESSAGING_BASE}/transferDonations",
            json=transfer_data,
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Transferencia simulada exitosamente")
            return True
        else:
            print("❌ Error en la transferencia simulada")
            return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 DEBUGGING DONACIONES RECIBIDAS")
    print("=" * 50)
    
    # 1. Verificar transferencias existentes en BD
    check_database_transfers()
    
    # 2. Verificar API de historial
    check_transfer_history_api()
    
    # 3. Verificar notificaciones en BD
    check_database_notifications()
    
    # 4. Verificar API de notificaciones
    check_notifications_api()
    
    # 5. Simular una nueva transferencia
    print("\n¿Desea simular una nueva transferencia? (y/n): ", end="")
    if input().lower() == 'y':
        if simulate_transfer():
            print("\n⏳ Esperando 5 segundos para que se procese...")
            import time
            time.sleep(5)
            
            print("\n🔄 Verificando resultados después de la transferencia:")
            check_database_transfers()
            check_database_notifications()

if __name__ == "__main__":
    main()