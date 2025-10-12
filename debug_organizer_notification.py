#!/usr/bin/env python3
"""
Debug de notificación al organizador
"""
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def debug_organizer_notification():
    """Debug por qué no se crea notificación al organizador"""
    print("🔍 DEBUG NOTIFICACIÓN AL ORGANIZADOR")
    print("=" * 50)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Verificar la consulta que se hace en el endpoint
        event_query = """
            SELECT er.nombre as event_name, er.organizacion_origen,
                   u.id as admin_id, u.nombre, u.apellido, u.rol
            FROM eventos_red er
            LEFT JOIN usuarios u ON u.organizacion = er.organizacion_origen 
                                 AND u.rol IN ('PRESIDENTE', 'COORDINADOR')
            WHERE er.evento_id = 27
        """
        
        cursor.execute(event_query)
        results = cursor.fetchall()
        
        print(f"Resultados de la consulta para evento 27:")
        print(f"Total resultados: {len(results)}")
        
        for result in results:
            print(f"  - Evento: {result['event_name']}")
            print(f"    Organización: {result['organizacion_origen']}")
            print(f"    Admin ID: {result['admin_id']}")
            print(f"    Admin: {result['nombre']} {result['apellido']}")
            print(f"    Rol: {result['rol']}")
        
        # Verificar si hay usuarios admin de fundacion-esperanza
        cursor.execute("""
            SELECT id, nombre, apellido, rol, organizacion
            FROM usuarios 
            WHERE organizacion = 'fundacion-esperanza'
            AND rol IN ('PRESIDENTE', 'COORDINADOR')
        """)
        
        admins = cursor.fetchall()
        print(f"\\nAdmins de fundacion-esperanza: {len(admins)}")
        
        for admin in admins:
            print(f"  - ID: {admin['id']}, {admin['nombre']} {admin['apellido']} ({admin['rol']})")
        
        # Verificar notificaciones recientes
        cursor.execute("""
            SELECT * FROM notificaciones 
            WHERE tipo = 'adhesion_evento'
            ORDER BY fecha_creacion DESC
            LIMIT 5
        """)
        
        notifications = cursor.fetchall()
        print(f"\\nNotificaciones de adhesión recientes: {len(notifications)}")
        
        for notif in notifications:
            print(f"  - ID: {notif['id']}")
            print(f"    Usuario: {notif['usuario_id']}")
            print(f"    Título: {notif['titulo']}")
            print(f"    Fecha: {notif['fecha_creacion']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_organizer_notification()