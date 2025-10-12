#!/usr/bin/env python3
"""
Test para crear una transferencia real con notificación
"""

import mysql.connector
import json
import uuid
from datetime import datetime

def test_real_transfer_notification():
    print("🔍 TESTING REAL TRANSFER NOTIFICATION")
    print("=" * 60)
    
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        print("✅ Conexión a base de datos establecida")
        
        # 1. Crear una solicitud real de fundacion-esperanza
        print("\n=== CREANDO SOLICITUD REAL ===")
        
        # Buscar usuario de fundacion-esperanza
        cursor.execute("""
            SELECT id, nombre_usuario, organizacion
            FROM usuarios 
            WHERE organizacion = 'fundacion-esperanza' 
            AND activo = TRUE 
            LIMIT 1
        """)
        
        user_result = cursor.fetchone()
        if not user_result:
            print("❌ No se encontró usuario de fundacion-esperanza")
            return
        
        user_id, username, org = user_result
        print(f"👤 Usuario encontrado: {username} (ID: {user_id}) de {org}")
        
        # Crear solicitud
        solicitud_id = f"req-real-test-{int(datetime.now().timestamp())}"
        donaciones_solicitadas = [
            {
                "categoria": "Alimentos",
                "descripcion": "Arroz para comedor comunitario",
                "cantidad": "10 kg",
                "urgencia": "MEDIA"
            },
            {
                "categoria": "Ropa",
                "descripcion": "Abrigos para invierno",
                "cantidad": "5 unidades",
                "urgencia": "ALTA"
            }
        ]
        
        insert_query = """
            INSERT INTO solicitudes_donaciones 
            (solicitud_id, organization_id, usuario_creacion, donaciones, estado, fecha_creacion, notas)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """
        
        cursor.execute(insert_query, (
            solicitud_id,
            org,
            user_id,
            json.dumps(donaciones_solicitadas),
            'ACTIVA',
            'Solicitud de prueba para test de notificaciones'
        ))
        
        conn.commit()
        print(f"✅ Solicitud creada: {solicitud_id}")
        print(f"   Usuario solicitante: {user_id} ({username})")
        
        # 2. Simular transferencia RECIBIDA desde empuje-comunitario
        print("\n=== SIMULANDO TRANSFERENCIA RECIBIDA ===")
        
        donaciones_transferidas = [
            {
                "categoria": "Alimentos",
                "descripcion": "Arroz para comedor comunitario",
                "cantidad": "8 kg"
            },
            {
                "categoria": "Ropa", 
                "descripcion": "Abrigos para invierno",
                "cantidad": "3 unidades"
            }
        ]
        
        transfer_query = """
            INSERT INTO transferencias_donaciones 
            (tipo, organizacion_contraparte, solicitud_id, donaciones, usuario_registro, notas, organizacion_propietaria)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(transfer_query, (
            'RECIBIDA',
            'empuje-comunitario',
            solicitud_id,
            json.dumps(donaciones_transferidas),
            1,  # Usuario sistema
            'Transferencia de prueba para test de notificaciones',
            'fundacion-esperanza'
        ))
        
        transfer_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Transferencia creada: ID {transfer_id}")
        print(f"   Tipo: RECIBIDA")
        print(f"   De: empuje-comunitario")
        print(f"   Para: fundacion-esperanza")
        print(f"   Solicitud: {solicitud_id}")
        
        # 3. Crear notificación manualmente (simulando el transfer_consumer)
        print("\n=== CREANDO NOTIFICACIÓN ===")
        
        # Contar donaciones
        donations_count = len(donaciones_transferidas)
        donation_summary = []
        
        for donation in donaciones_transferidas:
            donation_summary.append(f"• {donation['descripcion']} ({donation['cantidad']})")
        
        donations_text = "\\n".join(donation_summary)
        
        # Crear notificación
        title = "🎁 ¡Donación recibida!"
        message = f"""¡Excelente noticia {username}!

La organización 'empuje-comunitario' ha respondido a tu solicitud de donaciones.

Donaciones recibidas:
{donations_text}

Las donaciones ya están disponibles en tu inventario. ¡Gracias por usar la red de colaboración!"""
        
        notification_query = """
            INSERT INTO notificaciones_usuarios 
            (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
            VALUES (%s, %s, %s, %s, NOW(), false)
        """
        
        cursor.execute(notification_query, (
            user_id,
            title,
            message,
            'SUCCESS'
        ))
        
        notification_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Notificación creada: ID {notification_id}")
        print(f"   Para usuario: {user_id} ({username})")
        print(f"   Título: {title}")
        
        # 4. Verificar que la notificación se creó correctamente
        print("\n=== VERIFICANDO NOTIFICACIÓN ===")
        
        verify_query = """
            SELECT 
                n.id,
                n.titulo,
                n.mensaje,
                n.tipo,
                n.fecha_creacion,
                n.leida,
                u.nombre_usuario,
                u.organizacion
            FROM notificaciones_usuarios n
            JOIN usuarios u ON n.usuario_id = u.id
            WHERE n.id = %s
        """
        
        cursor.execute(verify_query, (notification_id,))
        result = cursor.fetchone()
        
        if result:
            notif_id, titulo, mensaje, tipo, fecha, leida, user_name, user_org = result
            print(f"✅ Notificación verificada:")
            print(f"   ID: {notif_id}")
            print(f"   Usuario: {user_name} ({user_org})")
            print(f"   Título: {titulo}")
            print(f"   Tipo: {tipo}")
            print(f"   Fecha: {fecha}")
            print(f"   Leída: {'Sí' if leida else 'No'}")
            print(f"   Mensaje: {mensaje[:150]}...")
        else:
            print("❌ No se pudo verificar la notificación")
        
        print("\n" + "=" * 60)
        print("📋 RESULTADO")
        print("=" * 60)
        print("✅ Test completado exitosamente")
        print(f"📧 Notificación creada para {username} de {org}")
        print("🔔 La notificación debería aparecer en la campana del frontend")
        print(f"🎯 Inicia sesión como '{username}' para ver la notificación")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    test_real_transfer_notification()