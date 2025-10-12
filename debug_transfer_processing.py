#!/usr/bin/env python3
"""
Debug específico del procesamiento de transferencias
"""

import mysql.connector
import json
from datetime import datetime, timedelta

def debug_transfer_processing():
    print("🔍 DEBUG TRANSFER PROCESSING")
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
        
        # 1. Verificar transferencias recientes (últimos 10 minutos)
        print("=== TRANSFERENCIAS RECIENTES (últimos 10 min) ===")
        
        ten_minutes_ago = datetime.now() - timedelta(minutes=10)
        
        cursor.execute("""
            SELECT 
                id,
                tipo,
                organizacion_contraparte,
                organizacion_propietaria,
                solicitud_id,
                fecha_transferencia,
                donaciones
            FROM transferencias_donaciones
            WHERE fecha_transferencia >= %s
            ORDER BY fecha_transferencia DESC
        """, (ten_minutes_ago,))
        
        recent_transfers = cursor.fetchall()
        
        if recent_transfers:
            print(f"📋 Encontradas {len(recent_transfers)} transferencias recientes:")
            
            for i, transfer in enumerate(recent_transfers, 1):
                transfer_id, tipo, contraparte, propietaria, solicitud_id, fecha, donaciones = transfer
                
                print(f"\n{i}. TRANSFERENCIA ID: {transfer_id}")
                print(f"   Tipo: {tipo}")
                print(f"   Contraparte: {contraparte}")
                print(f"   Propietaria: {propietaria}")
                print(f"   Solicitud: {solicitud_id}")
                print(f"   Fecha: {fecha}")
                
                # Parsear donaciones
                try:
                    donations_data = json.loads(donaciones) if isinstance(donaciones, str) else donaciones
                    print(f"   Donaciones: {len(donations_data)} items")
                    for j, donation in enumerate(donations_data[:2], 1):  # Mostrar primeras 2
                        desc = donation.get('descripcion', donation.get('description', 'N/A'))
                        cant = donation.get('cantidad', donation.get('quantity', 'N/A'))
                        print(f"      {j}. {desc} ({cant})")
                except:
                    print(f"   Donaciones: Error parseando JSON")
                
                # Si es ENVIADA, buscar la RECIBIDA correspondiente
                if tipo == 'ENVIADA':
                    cursor.execute("""
                        SELECT id, organizacion_propietaria, fecha_transferencia
                        FROM transferencias_donaciones
                        WHERE solicitud_id = %s AND tipo = 'RECIBIDA'
                        ORDER BY fecha_transferencia DESC
                        LIMIT 1
                    """, (solicitud_id,))
                    
                    received_result = cursor.fetchone()
                    if received_result:
                        rec_id, rec_prop, rec_fecha = received_result
                        print(f"   ✅ RECIBIDA correspondiente: ID {rec_id} ({rec_prop}) - {rec_fecha}")
                    else:
                        print(f"   ❌ NO hay RECIBIDA correspondiente")
                        print(f"      🔍 Esto indica que el consumer NO procesó el mensaje")
        else:
            print("📭 No se encontraron transferencias recientes")
        
        # 2. Verificar notificaciones recientes
        print(f"\n=== NOTIFICACIONES RECIENTES (últimos 10 min) ===")
        
        cursor.execute("""
            SELECT 
                n.id,
                n.usuario_id,
                n.titulo,
                n.mensaje,
                n.fecha_creacion,
                n.leida,
                u.nombre_usuario,
                u.organizacion
            FROM notificaciones_usuarios n
            LEFT JOIN usuarios u ON n.usuario_id = u.id
            WHERE n.fecha_creacion >= %s
            AND n.titulo LIKE '%donación%'
            ORDER BY n.fecha_creacion DESC
        """, (ten_minutes_ago,))
        
        recent_notifications = cursor.fetchall()
        
        if recent_notifications:
            print(f"📋 Encontradas {len(recent_notifications)} notificaciones recientes:")
            
            for i, notif in enumerate(recent_notifications, 1):
                notif_id, user_id, titulo, mensaje, fecha, leida, username, org = notif
                print(f"\n{i}. NOTIFICACIÓN ID: {notif_id}")
                print(f"   Usuario: {username} ({org})")
                print(f"   Título: {titulo}")
                print(f"   Fecha: {fecha}")
                print(f"   Leída: {'Sí' if leida else 'No'}")
                print(f"   Mensaje: {mensaje[:100]}...")
        else:
            print("📭 No se encontraron notificaciones recientes")
        
        # 3. Verificar solicitudes activas de fundacion-esperanza
        print(f"\n=== SOLICITUDES ACTIVAS DE FUNDACION-ESPERANZA ===")
        
        cursor.execute("""
            SELECT 
                solicitud_id,
                usuario_creacion,
                donaciones,
                fecha_creacion,
                estado
            FROM solicitudes_donaciones
            WHERE organization_id = 'fundacion-esperanza'
            AND estado = 'ACTIVA'
            ORDER BY fecha_creacion DESC
            LIMIT 5
        """)
        
        esperanza_requests = cursor.fetchall()
        
        if esperanza_requests:
            print(f"📋 Encontradas {len(esperanza_requests)} solicitudes activas:")
            
            for i, req in enumerate(esperanza_requests, 1):
                solicitud_id, user_id, donaciones, fecha, estado = req
                print(f"\n{i}. SOLICITUD: {solicitud_id}")
                print(f"   Usuario: {user_id}")
                print(f"   Estado: {estado}")
                print(f"   Fecha: {fecha}")
                
                # Verificar si tiene transferencias
                cursor.execute("""
                    SELECT COUNT(*) as enviadas, 
                           (SELECT COUNT(*) FROM transferencias_donaciones 
                            WHERE solicitud_id = %s AND tipo = 'RECIBIDA') as recibidas
                    FROM transferencias_donaciones
                    WHERE solicitud_id = %s AND tipo = 'ENVIADA'
                """, (solicitud_id, solicitud_id))
                
                transfer_counts = cursor.fetchone()
                if transfer_counts:
                    enviadas, recibidas = transfer_counts
                    print(f"   Transferencias: {enviadas} enviadas, {recibidas} recibidas")
                    
                    if enviadas > 0 and recibidas == 0:
                        print(f"   ⚠️  HAY TRANSFERENCIAS ENVIADAS PERO NO RECIBIDAS")
                        print(f"      Esto indica problema en el consumer")
        else:
            print("📭 No hay solicitudes activas de fundacion-esperanza")
        
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
    print("Si ves transferencias ENVIADAS sin RECIBIDAS correspondientes:")
    print("❌ El consumer dinámico NO está procesando correctamente")
    print("🔍 Posibles causas:")
    print("   1. Error en la lógica de filtrado por organización")
    print("   2. Problema en la conexión a base de datos del consumer")
    print("   3. Error en el procesamiento del mensaje")
    print("   4. El mensaje no llega al topic correcto")

if __name__ == "__main__":
    debug_transfer_processing()