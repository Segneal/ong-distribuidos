#!/usr/bin/env python3
"""
Test del consumer dinámico de transferencias
"""

import requests
import json
import time
import mysql.connector
from datetime import datetime

def test_dynamic_transfer_consumer():
    print("🔍 TEST DYNAMIC TRANSFER CONSUMER")
    print("=" * 60)
    
    try:
        # 1. Verificar que el messaging service está suscrito a múltiples topics
        print("=== STEP 1: VERIFICAR TOPICS SUSCRITOS ===")
        
        status_response = requests.get("http://localhost:50054/status")
        if status_response.status_code == 200:
            status_data = status_response.json()
            org_consumer = status_data.get('consumers', {}).get('organization_consumer', {})
            topics = org_consumer.get('topics', [])
            
            print(f"📡 Organization Consumer Topics:")
            transfer_topics = [t for t in topics if 'transferencia-donaciones' in t]
            adhesion_topics = [t for t in topics if 'adhesion-evento' in t]
            
            print(f"   🔄 Transfer Topics: {len(transfer_topics)}")
            for topic in transfer_topics:
                print(f"      • {topic}")
            
            print(f"   🎯 Adhesion Topics: {len(adhesion_topics)}")
            for topic in adhesion_topics:
                print(f"      • {topic}")
            
            if len(transfer_topics) > 1:
                print("✅ Consumer dinámico funcionando - suscrito a múltiples organizaciones")
            else:
                print("❌ Consumer NO dinámico - solo suscrito a una organización")
                
        else:
            print(f"❌ No se pudo obtener status: {status_response.status_code}")
            return
        
        # 2. Verificar organizaciones en base de datos
        print("\n=== STEP 2: VERIFICAR ORGANIZACIONES EN BD ===")
        
        conn = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT organizacion FROM usuarios WHERE activo = TRUE ORDER BY organizacion")
        organizations = cursor.fetchall()
        
        print(f"🏢 Organizaciones activas en BD:")
        org_list = []
        for org in organizations:
            org_id = org[0]
            org_list.append(org_id)
            print(f"   • {org_id}")
        
        # 3. Verificar que hay topics para cada organización
        print("\n=== STEP 3: VERIFICAR TOPICS ESPERADOS ===")
        
        expected_transfer_topics = [f"transferencia-donaciones-{org}" for org in org_list]
        
        print(f"📋 Topics de transferencia esperados:")
        for topic in expected_transfer_topics:
            if topic in transfer_topics:
                print(f"   ✅ {topic}")
            else:
                print(f"   ❌ {topic} - FALTANTE")
        
        # 4. Test de flujo completo
        print("\n=== STEP 4: TEST DE FLUJO COMPLETO ===")
        
        # Login como admin (empuje-comunitario)
        login_response = requests.post("http://localhost:3001/api/auth/login", json={
            "usernameOrEmail": "admin",
            "password": "admin123"
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json().get("token")
        print("✅ Login exitoso como admin (empuje-comunitario)")
        
        # Crear solicitud de fundacion-esperanza
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
        
        solicitud_id = f"req-dynamic-{int(datetime.now().timestamp())}"
        donaciones_solicitadas = [
            {
                "categoria": "Alimentos",
                "descripcion": "Test dinámico",
                "cantidad": "1",
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
            'Test consumer dinámico'
        ))
        
        conn.commit()
        print(f"✅ Solicitud creada: {solicitud_id}")
        
        # Obtener donación del inventario
        cursor.execute("""
            SELECT id FROM donaciones
            WHERE eliminado = FALSE AND cantidad > 0
            LIMIT 1
        """)
        
        inventory_result = cursor.fetchone()
        if not inventory_result:
            print("❌ No hay donaciones en inventario")
            return
        
        inventory_id = inventory_result[0]
        
        # Hacer transferencia
        transfer_data = {
            "targetOrganization": "fundacion-esperanza",
            "requestId": solicitud_id,
            "donations": [
                {
                    "inventoryId": inventory_id,
                    "quantity": "1"
                }
            ],
            "notes": "Test consumer dinámico"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        transfer_response = requests.post(
            "http://localhost:3001/api/messaging/transfer-donations", 
            json=transfer_data, 
            headers=headers
        )
        
        if transfer_response.status_code == 200:
            print("✅ Transferencia enviada exitosamente")
        else:
            print(f"❌ Error en transferencia: {transfer_response.status_code}")
            print(f"   Response: {transfer_response.text}")
            return
        
        # Esperar procesamiento
        print("⏳ Esperando 10 segundos para procesamiento...")
        time.sleep(10)
        
        # Verificar transferencia RECIBIDA
        cursor.execute("""
            SELECT id, tipo, organizacion_contraparte, organizacion_propietaria
            FROM transferencias_donaciones
            WHERE solicitud_id = %s AND tipo = 'RECIBIDA'
            ORDER BY fecha_transferencia DESC
            LIMIT 1
        """, (solicitud_id,))
        
        received_transfer = cursor.fetchone()
        if received_transfer:
            transfer_id, tipo, contraparte, propietaria = received_transfer
            print(f"✅ TRANSFERENCIA RECIBIDA ENCONTRADA:")
            print(f"   ID: {transfer_id}")
            print(f"   De: {contraparte}")
            print(f"   Para: {propietaria}")
            print("🎉 ¡CONSUMER DINÁMICO FUNCIONANDO!")
        else:
            print("❌ NO se encontró transferencia RECIBIDA")
            print("   El consumer dinámico NO está funcionando")
        
        # Verificar notificación
        cursor.execute("""
            SELECT id, titulo
            FROM notificaciones_usuarios
            WHERE usuario_id = %s
            AND titulo LIKE '%donación%'
            ORDER BY fecha_creacion DESC
            LIMIT 1
        """, (user_id,))
        
        notification = cursor.fetchone()
        if notification:
            print(f"✅ NOTIFICACIÓN CREADA: {notification[1]}")
        else:
            print("❌ NO se creó notificación")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
    
    print("\n" + "=" * 60)
    print("📋 RESULTADO")
    print("=" * 60)
    print("Si encontraste transferencia RECIBIDA:")
    print("✅ El consumer dinámico está funcionando correctamente")
    print("🔔 Las notificaciones de transferencias deberían funcionar")
    print("")
    print("Si NO encontraste transferencia RECIBIDA:")
    print("❌ Necesitas reiniciar el messaging service")
    print("🔄 Los cambios en el consumer requieren reinicio")

if __name__ == "__main__":
    test_dynamic_transfer_consumer()