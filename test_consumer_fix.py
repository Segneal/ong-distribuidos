#!/usr/bin/env python3
"""
Test rápido para verificar el fix del consumer
"""

import requests
import json
import time
import mysql.connector
from datetime import datetime

def test_consumer_fix():
    print("🔍 TEST CONSUMER FIX")
    print("=" * 50)
    
    try:
        # Login y hacer transferencia rápida
        login_response = requests.post("http://localhost:3001/api/auth/login", json={
            "usernameOrEmail": "admin",
            "password": "admin123"
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed")
            return
        
        token = login_response.json().get("token")
        
        # Conectar a BD
        conn = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # Crear solicitud rápida
        solicitud_id = f"req-fix-{int(datetime.now().timestamp())}"
        
        cursor.execute("""
            INSERT INTO solicitudes_donaciones 
            (solicitud_id, organization_id, usuario_creacion, donaciones, estado, fecha_creacion, notas)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """, (
            solicitud_id,
            'fundacion-esperanza',
            17,  # esperanza_admin
            json.dumps([{"categoria": "Test", "descripcion": "Fix test", "cantidad": "1"}]),
            'ACTIVA',
            'Test fix consumer'
        ))
        
        conn.commit()
        
        # Obtener donación del inventario
        cursor.execute("SELECT id FROM donaciones WHERE eliminado = FALSE AND cantidad > 0 LIMIT 1")
        inventory_result = cursor.fetchone()
        
        if not inventory_result:
            print("❌ No hay inventario")
            return
        
        inventory_id = inventory_result[0]
        
        # Hacer transferencia
        transfer_data = {
            "targetOrganization": "fundacion-esperanza",
            "requestId": solicitud_id,
            "donations": [{"inventoryId": inventory_id, "quantity": "1"}],
            "notes": "Test fix"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        transfer_response = requests.post(
            "http://localhost:3001/api/messaging/transfer-donations", 
            json=transfer_data, 
            headers=headers
        )
        
        if transfer_response.status_code == 200:
            print("✅ Transferencia enviada")
        else:
            print(f"❌ Error: {transfer_response.status_code}")
            return
        
        # Esperar procesamiento
        print("⏳ Esperando 8 segundos...")
        time.sleep(8)
        
        # Verificar transferencia RECIBIDA
        cursor.execute("""
            SELECT id FROM transferencias_donaciones
            WHERE solicitud_id = %s AND tipo = 'RECIBIDA'
            LIMIT 1
        """, (solicitud_id,))
        
        received = cursor.fetchone()
        
        if received:
            print("✅ ¡TRANSFERENCIA RECIBIDA ENCONTRADA!")
            print("🎉 ¡EL FIX FUNCIONÓ!")
        else:
            print("❌ No se encontró transferencia RECIBIDA")
            print("🔄 Necesitas reiniciar el messaging service")
        
        # Verificar notificación
        cursor.execute("""
            SELECT id FROM notificaciones_usuarios
            WHERE usuario_id = 17
            AND titulo LIKE '%donación%'
            ORDER BY fecha_creacion DESC
            LIMIT 1
        """)
        
        notification = cursor.fetchone()
        if notification:
            print("✅ ¡NOTIFICACIÓN CREADA!")
        else:
            print("❌ No se creó notificación")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    test_consumer_fix()