#!/usr/bin/env python3
"""
Debug del flujo completo de transferencias y Kafka
"""

import requests
import json
import time
import mysql.connector
from datetime import datetime

def debug_kafka_transfer_flow():
    print("🔍 DEBUG KAFKA TRANSFER FLOW")
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
        
        # 2. Crear una solicitud real de fundacion-esperanza
        print("\n=== STEP 2: CREAR SOLICITUD REAL ===")
        
        conn = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # Buscar usuario de fundacion-esperanza
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
        solicitud_id = f"req-debug-{int(datetime.now().timestamp())}"
        donaciones_solicitadas = [
            {
                "categoria": "Alimentos",
                "descripcion": "Leche en polvo",
                "cantidad": "5 kg",
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
            'Solicitud para debug de Kafka'
        ))
        
        conn.commit()
        print(f"✅ Solicitud creada: {solicitud_id}")
        print(f"   Usuario solicitante: {username} (ID: {user_id})")
        
        # 3. Hacer transferencia desde empuje-comunitario
        print("\n=== STEP 3: TRANSFERIR DONACIONES ===")
        
        transfer_data = {
            "targetOrganization": "fundacion-esperanza",
            "requestId": solicitud_id,
            "donations": [
                {
                    "categoria": "Alimentos",
                    "descripcion": "Leche en polvo",
                    "cantidad": "3 kg"
                }
            ],
            "notes": "Transferencia de debug para Kafka"
        }
        
        print(f"📤 Enviando transferencia...")
        print(f"   Target: {transfer_data['targetOrganization']}")
        print(f"   Request ID: {transfer_data['requestId']}")
        print(f"   Donaciones: {len(transfer_data['donations'])}")
        
        headers = {"Authorization": f"Bearer {token}"}
        transfer_response = requests.post(transfer_url, json=transfer_data, headers=headers)
        
        if transfer_response.status_code == 200:
            print("✅ Transferencia enviada exitosamente")
            print(f"   Response: {transfer_response.json()}")
        else:
            print(f"❌ Error en transferencia: {transfer_response.status_code}")
            print(f"   Response: {transfer_response.text}")
            return
        
        # 4. Esperar un momento para que Kafka procese
        print("\n=== STEP 4: ESPERANDO PROCESAMIENTO KAFKA ===")
        print("⏳ Esperando 5 segundos para que Kafka procese el mensaje...")
        time.sleep(5)
        
        # 5. Verificar si se creó la transferencia ENVIADA
        print("\n=== STEP 5: VERIFICAR TRANSFERENCIA ENVIADA ===")
        
        cursor.execute("""
            SELECT id, tipo, organizacion_contraparte, solicitud_id, fecha_transferencia
            FROM transferencias_donaciones
            WHERE solicitud_id = %s AND tipo = 'ENVIADA'
            ORDER BY fecha_transferencia DESC
            LIMIT 1
        """, (solicitud_id,))
        
        sent_transfer = cursor.fetchone()
        if sent_transfer:
            transfer_id, tipo, contraparte, req_id, fecha = sent_transfer
            print(f"✅ Transferencia ENVIADA encontrada:")
            print(f"   ID: {transfer_id}")
            print(f"   Tipo: {tipo}")
            print(f"   Contraparte: {contraparte}")
            print(f"   Fecha: {fecha}")
        else:
            print("❌ No se encontró transferencia ENVIADA")
        
        # 6. Verificar si se creó la transferencia RECIBIDA
        print("\n=== STEP 6: VERIFICAR TRANSFERENCIA RECIBIDA ===")
        
        cursor.execute("""
            SELECT id, tipo, organizacion_contraparte, solicitud_id, fecha_transferencia, organizacion_propietaria
            FROM transferencias_donaciones
            WHERE solicitud_id = %s AND tipo = 'RECIBIDA'
            ORDER BY fecha_transferencia DESC
            LIMIT 1
        """, (solicitud_id,))
        
        received_transfer = cursor.fetchone()
        if received_transfer:
            transfer_id, tipo, contraparte, req_id, fecha, propietaria = received_transfer
            print(f"✅ Transferencia RECIBIDA encontrada:")
            print(f"   ID: {transfer_id}")
            print(f"   Tipo: {tipo}")
            print(f"   Contraparte: {contraparte}")
            print(f"   Propietaria: {propietaria}")
            print(f"   Fecha: {fecha}")
        else:
            print("❌ NO se encontró transferencia RECIBIDA")
            print("   🔍 Esto indica que el transfer_consumer NO está procesando mensajes")
        
        # 7. Verificar si se creó la notificación
        print("\n=== STEP 7: VERIFICAR NOTIFICACIÓN ===")
        
        cursor.execute("""
            SELECT id, titulo, mensaje, fecha_creacion, leida
            FROM notificaciones_usuarios
            WHERE usuario_id = %s
            AND fecha_creacion >= (SELECT fecha_transferencia FROM transferencias_donaciones WHERE solicitud_id = %s AND tipo = 'ENVIADA' LIMIT 1)
            ORDER BY fecha_creacion DESC
            LIMIT 1
        """, (user_id, solicitud_id))
        
        notification = cursor.fetchone()
        if notification:
            notif_id, titulo, mensaje, fecha, leida = notification
            print(f"✅ Notificación encontrada:")
            print(f"   ID: {notif_id}")
            print(f"   Título: {titulo}")
            print(f"   Fecha: {fecha}")
            print(f"   Leída: {'Sí' if leida else 'No'}")
        else:
            print("❌ NO se encontró notificación")
            print("   🔍 Esto confirma que el transfer_consumer NO está funcionando")
        
        # 8. Verificar estado del messaging service
        print("\n=== STEP 8: VERIFICAR MESSAGING SERVICE ===")
        
        try:
            messaging_response = requests.get("http://localhost:50054/health", timeout=2)
            if messaging_response.status_code == 200:
                print("✅ Messaging Service está corriendo")
            else:
                print(f"⚠️  Messaging Service responde con: {messaging_response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Messaging Service NO está corriendo")
        except requests.exceptions.Timeout:
            print("⚠️  Messaging Service no responde (timeout)")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
    
    print("\n" + "=" * 60)
    print("📋 DIAGNÓSTICO")
    print("=" * 60)
    print("Si NO se encontró transferencia RECIBIDA ni notificación:")
    print("1. ❌ El messaging service NO está corriendo")
    print("2. ❌ El transfer_consumer NO está procesando mensajes de Kafka")
    print("3. ❌ Kafka puede no estar funcionando correctamente")
    print("")
    print("SOLUCIÓN:")
    print("1. 🔄 Reinicia el messaging service")
    print("2. 🔍 Verifica que Kafka esté corriendo")
    print("3. 📋 Revisa los logs del messaging service")

if __name__ == "__main__":
    debug_kafka_transfer_flow()