#!/usr/bin/env python3
"""
Script para probar el sistema de notificaciones
"""

import mysql.connector
import json
from datetime import datetime

def test_notifications_system():
    """Probar el sistema completo de notificaciones"""
    
    # Configuración de la base de datos
    config = {
        'host': 'localhost',
        'database': 'ong_management',
        'user': 'root',
        'password': 'root',
        'port': 3306,
        'charset': 'utf8mb4'
    }
    
    try:
        print("=== Prueba del Sistema de Notificaciones ===")
        
        # Conectar a la base de datos
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        # 1. Verificar estructura de la tabla
        print("\n1. Verificando tabla de notificaciones...")
        cursor.execute("DESCRIBE notificaciones_usuarios")
        columns = cursor.fetchall()
        
        print("Columnas de la tabla notificaciones_usuarios:")
        for col in columns:
            print(f"  - {col['Field']}: {col['Type']} ({col['Null']}, {col['Default']})")
        
        # 2. Crear notificaciones de prueba
        print("\n2. Creando notificaciones de prueba...")
        
        test_notifications = [
            {
                'usuario_id': 11,  # Usar ID de usuario existente
                'titulo': 'Nueva adhesión a evento',
                'mensaje': 'Juan Pérez (fundacion-esperanza) quiere participar en "Maratón Solidaria". Revisa las adhesiones pendientes.',
                'tipo': 'INFO'
            },
            {
                'usuario_id': 11,
                'titulo': 'Adhesión aprobada',
                'mensaje': '¡Genial! Tu solicitud para participar en "Evento de Prueba" ha sido aprobada. ¡Nos vemos en el evento!',
                'tipo': 'SUCCESS'
            },
            {
                'usuario_id': 11,
                'titulo': 'Evento cancelado',
                'mensaje': 'El evento "Evento de Prueba" ha sido cancelado. Motivo: Mal tiempo',
                'tipo': 'ERROR'
            },
            {
                'usuario_id': 11,
                'titulo': 'Donación recibida',
                'mensaje': 'Has recibido una donación de fundacion-esperanza: 10kg de alimentos',
                'tipo': 'SUCCESS'
            }
        ]
        
        for notif in test_notifications:
            cursor.execute("""
                INSERT INTO notificaciones_usuarios 
                (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
                VALUES (%(usuario_id)s, %(titulo)s, %(mensaje)s, %(tipo)s, NOW(), false)
            """, notif)
            
            print(f"✓ Creada: {notif['titulo']}")
        
        connection.commit()
        
        # 3. Verificar notificaciones creadas
        print("\n3. Verificando notificaciones creadas...")
        cursor.execute("""
            SELECT id, titulo, mensaje, tipo, fecha_creacion, leida
            FROM notificaciones_usuarios 
            WHERE usuario_id = 11
            ORDER BY fecha_creacion DESC
            LIMIT 10
        """)
        
        notifications = cursor.fetchall()
        print(f"Total de notificaciones para usuario 11: {len(notifications)}")
        
        for notif in notifications:
            status = "📖 No leída" if not notif['leida'] else "✅ Leída"
            print(f"  - [{notif['tipo']}] {notif['titulo']} - {status}")
        
        # 4. Probar marcar como leída
        print("\n4. Probando marcar notificaciones como leídas...")
        if notifications:
            first_notif_id = notifications[0]['id']
            cursor.execute("""
                UPDATE notificaciones_usuarios 
                SET leida = true, fecha_leida = NOW()
                WHERE id = %s
            """, (first_notif_id,))
            connection.commit()
            print(f"✓ Notificación {first_notif_id} marcada como leída")
        
        # 5. Verificar conteo de no leídas
        print("\n5. Verificando conteo de notificaciones no leídas...")
        cursor.execute("""
            SELECT COUNT(*) as unread_count
            FROM notificaciones_usuarios 
            WHERE usuario_id = 11 AND leida = false
        """)
        
        unread_result = cursor.fetchone()
        unread_count = unread_result['unread_count']
        print(f"Notificaciones no leídas para usuario 11: {unread_count}")
        
        # 6. Probar notificación para administradores
        print("\n6. Probando notificación para administradores...")
        cursor.execute("""
            SELECT id, rol FROM usuarios 
            WHERE organizacion = 'empuje-comunitario' 
            AND rol IN ('PRESIDENTE', 'VOCAL')
            AND activo = true
        """)
        
        admins = cursor.fetchall()
        print(f"Administradores encontrados: {len(admins)}")
        
        for admin in admins:
            cursor.execute("""
                INSERT INTO notificaciones_usuarios 
                (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
                VALUES (%s, %s, %s, %s, NOW(), false)
            """, (
                admin['id'],
                'Notificación para administradores',
                'Esta es una notificación de prueba para todos los administradores de la organización.',
                'INFO'
            ))
            print(f"✓ Notificación enviada a {admin['rol']} (ID: {admin['id']})")
        
        connection.commit()
        
        # 7. Resumen final
        print("\n7. Resumen del sistema de notificaciones:")
        cursor.execute("""
            SELECT 
                tipo,
                COUNT(*) as count,
                SUM(CASE WHEN leida = false THEN 1 ELSE 0 END) as unread_count
            FROM notificaciones_usuarios 
            GROUP BY tipo
            ORDER BY count DESC
        """)
        
        summary = cursor.fetchall()
        print("Estadísticas por tipo:")
        for stat in summary:
            print(f"  - {stat['tipo']}: {stat['count']} total, {stat['unread_count']} no leídas")
        
        print("\n✅ Sistema de notificaciones funcionando correctamente!")
        return True
        
    except mysql.connector.Error as e:
        print(f"Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    test_notifications_system()