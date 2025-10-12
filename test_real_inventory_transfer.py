#!/usr/bin/env python3
"""
Test de transferencia usando donaciones reales del inventario
"""

import requests
import json
import time
import mysql.connector
from datetime import datetime

def test_real_inventory_transfer():
    print("🔍 TEST REAL INVENTORY TRANSFER")
    print("=" * 60)
    
    # URLs del API
    login_url = "http://localhost:3001/api/auth/login"
    transfer_url = "http://localhost:3001/api/messaging/transfer-donations"
    
    try:
        # 1. Login como admin (empuje-comunitario)
        print("=== STEP 1: LOGIN COMO ADMIN ===")
        login_response = requests.post(login_url, json={
            "usernameOrEmail": "admin",
            "password": "admin123"
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json().get("token")
        print("✅ Login exitoso como admin (empuje-comunitario)")
        
        # 2. Conectar a base de datos
        conn = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # 3. Verificar donaciones disponibles en inventario de empuje-comunitario
        print("\n=== STEP 2: VERIFICAR INVENTARIO ===")
        
        cursor.execute("""
            SELECT id, categoria, descripcion, cantidad
            FROM donaciones
            WHERE eliminado = FALSE
            AND cantidad > 0
            ORDER BY id DESC
            LIMIT 5
        """)
        
        inventory_items = cursor.fetchall()
        if not inventory_items:
            print("❌ No hay donaciones en el inventario")
            # Crear una donación de prueba
            print("🔧 Creando donación de prueba...")
            cursor.execute("""
                INSERT INTO donaciones (categoria, descripcion, cantidad, usuario_alta)
                VALUES ('Alimentos', 'Arroz para transferencia', 10, 1)
            """)
            conn.commit()
            
            # Obtener la donación recién creada
            cursor.execute("""
                SELECT id, categoria, descripcion, cantidad
                FROM donaciones
                WHERE eliminado = FALSE
                ORDER BY id DESC
                LIMIT 1
            """)
            inventory_items = cursor.fetchall()
        
        print("📦 Donaciones disponibles:")
        for item in inventory_items:
            item_id, categoria, descripcion, cantidad = item
            print(f"   • ID: {item_id} - {categoria}: {descripcion} ({cantidad})")
        
        # Usar la primera donación disponible
        selected_item = inventory_items[0]
        item_id, categoria, descripcion, cantidad = selected_item
        transfer_quantity = min(2, cantidad)  # Transferir máximo 2 o la cantidad disponible
        
        print(f"\n🎯 Seleccionada para transferir:")
        print(f"   ID: {item_id}")
        print(f"   Descripción: {descripcion}")
        print(f"   Cantidad a transferir: {transfer_quantity}")
        
        # 4. Crear solicitud real de fundacion-esperanza
        print("\n=== STEP 3: CREAR SOLICITUD REAL ===")
        
        cursor.execute("""
            SELECT id, nombre_usuario
            FROM usuarios 
            WHERE organizacion = 'fundacion-esperanza' 
            AND activo = TRUE 
            LIMIT 1
        """)
        
        user_result = cursor.fetchone()
        if not user_result:
            print("❌ No se encontró usuario de fundacion-esperanza")
            return
        
        user_id, username = user_result
        
        # Crear solicitud
        solicitud_id = f"req-real-{int(datetime.now().timestamp())}"
        donaciones_solicitadas = [
            {
                "categoria": categoria,
                "descripcion": descripcion,
                "cantidad": f"{transfer_quantity}",
                "urgencia": "ALTA"
            }
        ]
        
        cursor.execute("""
            INSERT INTO solicitudes_donaciones 
            (solicitud_id, organization_id, usuario_creacion, donaciones, estado, fecha_creacion, notas)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """, (
            solicitud_id,
            'fundacion-esperanza',
            user_id,
            json.dumps(donaciones_solicitadas),
            'ACTIVA',
            'Solicitud real para test de transferencia'
        ))
        
        conn.commit()
        print(f"✅ Solicitud creada: {solicitud_id}")
        print(f"   Usuario solicitante: {username} (ID: {user_id})")
        
        # 5. Hacer transferencia con formato correcto
        print("\n=== STEP 4: TRANSFERIR DONACIONES ===")
        
        transfer_data = {
            "targetOrganization": "fundacion-esperanza",
            "requestId": solicitud_id,
            "donations": [
                {
                    "inventoryId": item_id,  # ← Formato correcto
                    "quantity": str(transfer_quantity)
                }
            ],
            "notes": "Transferencia real para test de notificaciones"
        }
        
        print(f"📤 Enviando transferencia...")
        print(f"   Target: {transfer_data['targetOrganization']}")
        print(f"   Request ID: {transfer_data['requestId']}")
        print(f"   Inventory ID: {item_id}")
        print(f"   Quantity: {transfer_quantity}")
        
        headers = {"Authorization": f"Bearer {token}"}
        transfer_response = requests.post(transfer_url, json=transfer_data, headers=headers)
        
        if transfer_response.status_code == 200:
            print("✅ Transferencia enviada exitosamente")
            response_data = transfer_response.json()
            print(f"   Response: {response_data}")
            transfer_id = response_data.get('transfer_id')
        else:
            print(f"❌ Error en transferencia: {transfer_response.status_code}")
            print(f"   Response: {transfer_response.text}")
            return
        
        # 6. Esperar procesamiento de Kafka
        print("\n=== STEP 5: ESPERANDO KAFKA ===")
        print("⏳ Esperando 8 segundos para que Kafka procese...")
        time.sleep(8)
        
        # 7. Verificar transferencia ENVIADA
        print("\n=== STEP 6: VERIFICAR TRANSFERENCIA ENVIADA ===")
        
        cursor.execute("""
            SELECT id, tipo, organizacion_contraparte, solicitud_id, fecha_transferencia
            FROM transferencias_donaciones
            WHERE solicitud_id = %s AND tipo = 'ENVIADA'
            ORDER BY fecha_transferencia DESC
            LIMIT 1
        """, (solicitud_id,))
        
        sent_transfer = cursor.fetchone()
        if sent_transfer:
            print("✅ Transferencia ENVIADA encontrada")
        else:
            print("❌ No se encontró transferencia ENVIADA")
        
        # 8. Verificar transferencia RECIBIDA
        print("\n=== STEP 7: VERIFICAR TRANSFERENCIA RECIBIDA ===")
        
        cursor.execute("""
            SELECT id, tipo, organizacion_contraparte, solicitud_id, fecha_transferencia, organizacion_propietaria
            FROM transferencias_donaciones
            WHERE solicitud_id = %s AND tipo = 'RECIBIDA'
            ORDER BY fecha_transferencia DESC
            LIMIT 1
        """, (solicitud_id,))
        
        received_transfer = cursor.fetchone()
        if received_transfer:
            print("✅ Transferencia RECIBIDA encontrada")
            print("   🎉 ¡El transfer_consumer está funcionando!")
        else:
            print("❌ NO se encontró transferencia RECIBIDA")
            print("   🔍 El transfer_consumer NO está procesando mensajes")
        
        # 9. Verificar notificación
        print("\n=== STEP 8: VERIFICAR NOTIFICACIÓN ===")
        
        cursor.execute("""
            SELECT id, titulo, mensaje, fecha_creacion, leida
            FROM notificaciones_usuarios
            WHERE usuario_id = %s
            AND titulo LIKE '%donación%'
            ORDER BY fecha_creacion DESC
            LIMIT 1
        """, (user_id,))
        
        notification = cursor.fetchone()
        if notification:
            notif_id, titulo, mensaje, fecha, leida = notification
            print(f"✅ Notificación encontrada:")
            print(f"   ID: {notif_id}")
            print(f"   Título: {titulo}")
            print(f"   Fecha: {fecha}")
            print(f"   🎉 ¡Las notificaciones están funcionando!")
        else:
            print("❌ NO se encontró notificación")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
    
    print("\n" + "=" * 60)
    print("📋 RESULTADO FINAL")
    print("=" * 60)
    print("Si encontraste transferencia RECIBIDA y notificación:")
    print("✅ El sistema está funcionando correctamente")
    print("🔔 Inicia sesión como esperanza_admin para ver la notificación")
    print("")
    print("Si NO encontraste transferencia RECIBIDA:")
    print("❌ El transfer_consumer no está procesando mensajes de Kafka")
    print("🔄 Reinicia el messaging service")

if __name__ == "__main__":
    test_real_inventory_transfer()