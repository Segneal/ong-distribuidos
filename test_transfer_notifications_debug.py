#!/usr/bin/env python3
"""
Test para verificar si las notificaciones de transferencias se están creando correctamente
"""

import mysql.connector
import json
from datetime import datetime

def test_transfer_notifications():
    print("🔍 TESTING TRANSFER NOTIFICATIONS")
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
        
        # 1. Verificar notificaciones recientes
        print("\n=== VERIFICANDO NOTIFICACIONES RECIENTES ===")
        
        query = """
            SELECT 
                n.id,
                n.usuario_id,
                n.titulo,
                n.mensaje,
                n.tipo,
                n.fecha_creacion,
                n.leida,
                u.nombre_usuario,
                u.organizacion
            FROM notificaciones_usuarios n
            LEFT JOIN usuarios u ON n.usuario_id = u.id
            ORDER BY n.fecha_creacion DESC
            LIMIT 10
        """
        
        cursor.execute(query)
        notifications = cursor.fetchall()
        
        if notifications:
            print(f"📋 Encontradas {len(notifications)} notificaciones recientes:")
            for i, notif in enumerate(notifications, 1):
                notif_id, user_id, titulo, mensaje, tipo, fecha, leida, nombre_usuario, org = notif
                print(f"\n{i}. ID: {notif_id}")
                print(f"   Usuario: {nombre_usuario} ({org})")
                print(f"   Título: {titulo}")
                print(f"   Tipo: {tipo}")
                print(f"   Fecha: {fecha}")
                print(f"   Leída: {'Sí' if leida else 'No'}")
                print(f"   Mensaje: {mensaje[:100]}...")
        else:
            print("📭 No se encontraron notificaciones")
        
        # 2. Verificar transferencias recientes
        print("\n=== VERIFICANDO TRANSFERENCIAS RECIENTES ===")
        
        query = """
            SELECT 
                id,
                tipo,
                organizacion_contraparte,
                solicitud_id,
                organizacion_propietaria,
                fecha_transferencia,
                donaciones
            FROM transferencias_donaciones
            ORDER BY fecha_transferencia DESC
            LIMIT 5
        """
        
        cursor.execute(query)
        transfers = cursor.fetchall()
        
        if transfers:
            print(f"📋 Encontradas {len(transfers)} transferencias recientes:")
            for i, transfer in enumerate(transfers, 1):
                transfer_id, tipo, contraparte, solicitud_id, propietaria, fecha, donaciones = transfer
                print(f"\n{i}. ID: {transfer_id}")
                print(f"   Tipo: {tipo}")
                print(f"   Contraparte: {contraparte}")
                print(f"   Propietaria: {propietaria}")
                print(f"   Solicitud ID: {solicitud_id}")
                print(f"   Fecha: {fecha}")
                
                # Verificar si hay notificación asociada para transferencias RECIBIDAS
                if tipo == 'RECIBIDA' and solicitud_id:
                    # Buscar el usuario que hizo la solicitud original
                    user_query = """
                        SELECT usuario_creacion, organization_id
                        FROM solicitudes_donaciones
                        WHERE solicitud_id = %s
                    """
                    cursor.execute(user_query, (solicitud_id,))
                    user_result = cursor.fetchone()
                    
                    if user_result:
                        user_id, org_id = user_result
                        print(f"   👤 Usuario solicitante: {user_id} ({org_id})")
                        
                        # Buscar notificación para este usuario después de la transferencia
                        notif_query = """
                            SELECT id, titulo, fecha_creacion, leida
                            FROM notificaciones_usuarios
                            WHERE usuario_id = %s 
                            AND fecha_creacion >= %s
                            AND titulo LIKE '%donación%'
                            ORDER BY fecha_creacion DESC
                            LIMIT 1
                        """
                        cursor.execute(notif_query, (user_id, fecha))
                        notif_result = cursor.fetchone()
                        
                        if notif_result:
                            notif_id, notif_titulo, notif_fecha, notif_leida = notif_result
                            print(f"   ✅ Notificación encontrada: ID {notif_id}")
                            print(f"      Título: {notif_titulo}")
                            print(f"      Fecha: {notif_fecha}")
                            print(f"      Leída: {'Sí' if notif_leida else 'No'}")
                        else:
                            print(f"   ❌ NO se encontró notificación para este usuario")
                    else:
                        print(f"   ⚠️  No se encontró usuario solicitante para: {solicitud_id}")
        else:
            print("📭 No se encontraron transferencias")
        
        # 3. Verificar usuarios activos por organización
        print("\n=== VERIFICANDO USUARIOS POR ORGANIZACIÓN ===")
        
        query = """
            SELECT organizacion, COUNT(*) as user_count
            FROM usuarios
            WHERE activo = TRUE
            GROUP BY organizacion
            ORDER BY organizacion
        """
        
        cursor.execute(query)
        org_users = cursor.fetchall()
        
        if org_users:
            print("👥 Usuarios activos por organización:")
            for org, count in org_users:
                print(f"   • {org}: {count} usuarios")
        
        # 4. Verificar solicitudes activas
        print("\n=== VERIFICANDO SOLICITUDES ACTIVAS ===")
        
        query = """
            SELECT 
                solicitud_id,
                organization_id,
                usuario_creacion,
                estado,
                fecha_creacion
            FROM solicitudes_donaciones
            WHERE estado = 'ACTIVA'
            ORDER BY fecha_creacion DESC
            LIMIT 5
        """
        
        cursor.execute(query)
        active_requests = cursor.fetchall()
        
        if active_requests:
            print(f"📋 Encontradas {len(active_requests)} solicitudes activas:")
            for i, req in enumerate(active_requests, 1):
                solicitud_id, org_id, user_id, estado, fecha = req
                print(f"\n{i}. Solicitud: {solicitud_id}")
                print(f"   Organización: {org_id}")
                print(f"   Usuario: {user_id}")
                print(f"   Estado: {estado}")
                print(f"   Fecha: {fecha}")
        else:
            print("📭 No se encontraron solicitudes activas")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN")
    print("=" * 60)
    print("✅ Verificación completada")
    print("🔍 Si no ves notificaciones para transferencias RECIBIDAS:")
    print("   1. El transfer_consumer puede no estar corriendo")
    print("   2. El Kafka puede no estar procesando mensajes")
    print("   3. La notificación puede no estar llegando al frontend")
    print("   4. El usuario puede no estar asociado correctamente a la solicitud")

if __name__ == "__main__":
    test_transfer_notifications()