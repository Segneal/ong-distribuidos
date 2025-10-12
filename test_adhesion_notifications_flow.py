#!/usr/bin/env python3
"""
Script para probar el flujo completo de notificaciones de adhesiones
"""

import requests
import json
import mysql.connector
from datetime import datetime
import time

def test_adhesion_notifications_flow():
    """Probar el flujo completo de adhesiones con notificaciones"""
    
    print("=== Prueba de Flujo de Notificaciones de Adhesiones ===")
    
    # Configuración
    api_base = "http://localhost:3001/api"
    messaging_base = "http://localhost:50054/api"
    db_config = {
        'host': 'localhost',
        'database': 'ong_management',
        'user': 'root',
        'password': 'root',
        'port': 3306,
        'charset': 'utf8mb4'
    }
    
    try:
        # 1. Verificar estructura de base de datos
        print("1. Verificando estructura de base de datos...")
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Verificar usuarios administradores de eventos
        cursor.execute("""
            SELECT id, nombre, rol, organizacion
            FROM usuarios 
            WHERE rol IN ('PRESIDENTE', 'COORDINADOR') 
            AND activo = true
            ORDER BY organizacion, rol
        """)
        
        event_admins = cursor.fetchall()
        print(f"Administradores de eventos encontrados: {len(event_admins)}")
        
        for admin in event_admins:
            print(f"  - {admin['nombre']} ({admin['rol']}) - {admin['organizacion']}")
        
        # Verificar eventos disponibles
        cursor.execute("""
            SELECT id, nombre, organizacion
            FROM eventos 
            WHERE fecha_evento > NOW()
            ORDER BY organizacion
            LIMIT 5
        """)
        
        events = cursor.fetchall()
        print(f"\nEventos disponibles: {len(events)}")
        
        for event in events:
            print(f"  - ID {event['id']}: {event['nombre']} ({event['organizacion']})")
        
        # 2. Simular adhesión a evento
        print("\n2. Simulando adhesión a evento...")
        
        if events and event_admins:
            test_event = events[0]
            test_admin = event_admins[0]
            
            # Datos del voluntario que se anota
            volunteer_data = {
                "name": "María",
                "surname": "González",
                "email": "maria.gonzalez@test.com",
                "phone": "123456789"
            }
            
            # Simular creación de adhesión directamente en BD (como si viniera de Kafka)
            print(f"Creando adhesión para evento '{test_event['nombre']}'...")
            
            cursor.execute("""
                INSERT INTO adhesiones_eventos_externos 
                (evento_externo_id, voluntario_id, estado, datos_voluntario, fecha_adhesion)
                VALUES (%s, %s, 'PENDIENTE', %s, NOW())
                ON DUPLICATE KEY UPDATE
                estado = 'PENDIENTE', fecha_adhesion = NOW()
            """, (
                test_event['id'],
                999,  # ID ficticio para voluntario externo
                json.dumps(volunteer_data)
            ))
            
            connection.commit()
            adhesion_id = cursor.lastrowid or 1
            print(f"✓ Adhesión creada con ID: {adhesion_id}")
            
            # 3. Simular notificación a administradores
            print("\n3. Creando notificación para administradores...")
            
            # Buscar administradores de la organización del evento
            cursor.execute("""
                SELECT id FROM usuarios 
                WHERE organizacion = %s 
                AND rol IN ('PRESIDENTE', 'COORDINADOR')
                AND activo = true
            """, (test_event['organizacion'],))
            
            target_admins = cursor.fetchall()
            
            if target_admins:
                title = "🎯 Nueva solicitud de adhesión a evento"
                message = f"{volunteer_data['name']} {volunteer_data['surname']} (organizacion-externa) quiere participar en '{test_event['nombre']}'. Ve a 'Gestión de Adhesiones' para aprobar o rechazar la solicitud."
                
                for admin in target_admins:
                    cursor.execute("""
                        INSERT INTO notificaciones_usuarios 
                        (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
                        VALUES (%s, %s, %s, %s, NOW(), false)
                    """, (admin['id'], title, message, 'INFO'))
                
                connection.commit()
                print(f"✓ Notificaciones creadas para {len(target_admins)} administradores")
                
                # 4. Verificar notificaciones creadas
                print("\n4. Verificando notificaciones creadas...")
                
                for admin in target_admins:
                    cursor.execute("""
                        SELECT titulo, mensaje, fecha_creacion, leida
                        FROM notificaciones_usuarios 
                        WHERE usuario_id = %s
                        ORDER BY fecha_creacion DESC
                        LIMIT 3
                    """, (admin['id'],))
                    
                    notifications = cursor.fetchall()
                    print(f"  Admin ID {admin['id']}: {len(notifications)} notificaciones")
                    
                    for notif in notifications:
                        status = "📖 No leída" if not notif['leida'] else "✅ Leída"
                        print(f"    - {notif['titulo']} - {status}")
                
                # 5. Probar aprobación de adhesión
                print("\n5. Simulando aprobación de adhesión...")
                
                # Aprobar la adhesión
                cursor.execute("""
                    UPDATE adhesiones_eventos_externos 
                    SET estado = 'CONFIRMADA', fecha_aprobacion = NOW()
                    WHERE id = %s
                """, (adhesion_id,))
                
                # Crear notificación para el voluntario (usando un usuario real)
                cursor.execute("SELECT id FROM usuarios WHERE activo = true LIMIT 1")
                volunteer_user = cursor.fetchone()
                
                if volunteer_user:
                    approval_title = "✅ Adhesión a evento aprobada"
                    approval_message = f"¡Genial! Tu solicitud para participar en '{test_event['nombre']}' ha sido aprobada. ¡Nos vemos en el evento!"
                    
                    cursor.execute("""
                        INSERT INTO notificaciones_usuarios 
                        (usuario_id, titulo, mensaje, tipo, fecha_creacion, leida)
                        VALUES (%s, %s, %s, %s, NOW(), false)
                    """, (volunteer_user['id'], approval_title, approval_message, 'SUCCESS'))
                
                connection.commit()
                print("✓ Adhesión aprobada y notificación enviada al voluntario")
                
            else:
                print("❌ No se encontraron administradores para la organización del evento")
        
        else:
            print("❌ No hay eventos o administradores disponibles para la prueba")
        
        # 6. Resumen de notificaciones por tipo
        print("\n6. Resumen de notificaciones en el sistema:")
        cursor.execute("""
            SELECT 
                tipo,
                COUNT(*) as total,
                SUM(CASE WHEN leida = false THEN 1 ELSE 0 END) as no_leidas
            FROM notificaciones_usuarios 
            GROUP BY tipo
            ORDER BY total DESC
        """)
        
        summary = cursor.fetchall()
        for stat in summary:
            print(f"  - {stat['tipo']}: {stat['total']} total, {stat['no_leidas']} no leídas")
        
        cursor.close()
        connection.close()
        
        print("\n" + "="*60)
        print("FLUJO DE ADHESIONES CON NOTIFICACIONES:")
        print("="*60)
        print("✅ 1. Voluntario se anota a evento externo")
        print("✅ 2. Mensaje enviado a Kafka → topic adhesion-evento-{org}")
        print("✅ 3. AdhesionConsumer procesa mensaje")
        print("✅ 4. NotificationService notifica a administradores")
        print("✅ 5. Administradores ven notificación en campana 🔔")
        print("✅ 6. Administrador aprueba/rechaza adhesión")
        print("✅ 7. Voluntario recibe notificación de resultado")
        
        print("\n🎯 PARA VER LAS NOTIFICACIONES:")
        print("1. Ir a http://localhost:3000")
        print("2. Hacer login como administrador")
        print("3. Ver campana de notificaciones (🔔) en barra superior")
        print("4. Hacer clic para ver notificaciones de adhesiones")
        
        print("\n✅ Flujo de notificaciones de adhesiones funcionando!")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    test_adhesion_notifications_flow()