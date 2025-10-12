#!/usr/bin/env python3
"""
Script para verificar usuarios existentes para notificaciones
"""

import mysql.connector

def check_users():
    """Verificar usuarios existentes"""
    
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
        print("=== Verificación de Usuarios ===")
        
        # Conectar a la base de datos
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        # Verificar usuarios existentes
        print("1. Usuarios existentes:")
        cursor.execute("""
            SELECT id, nombre, email, rol, organization_id, activo
            FROM usuarios 
            ORDER BY id
        """)
        
        users = cursor.fetchall()
        print(f"Total de usuarios: {len(users)}")
        
        for user in users:
            status = "✅ Activo" if user['activo'] else "❌ Inactivo"
            print(f"  - ID {user['id']}: {user['nombre']} ({user['rol']}) - {user['organization_id']} - {status}")
        
        # Verificar administradores
        print("\n2. Administradores por organización:")
        cursor.execute("""
            SELECT organization_id, rol, COUNT(*) as count
            FROM usuarios 
            WHERE rol IN ('PRESIDENTE', 'VOCAL') AND activo = true
            GROUP BY organization_id, rol
            ORDER BY organization_id, rol
        """)
        
        admins = cursor.fetchall()
        for admin in admins:
            print(f"  - {admin['organization_id']}: {admin['count']} {admin['rol']}(s)")
        
        # Verificar notificaciones existentes
        print("\n3. Notificaciones existentes:")
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN leida = false THEN 1 ELSE 0 END) as unread
            FROM notificaciones_usuarios
        """)
        
        notif_stats = cursor.fetchone()
        print(f"  - Total: {notif_stats['total']}")
        print(f"  - No leídas: {notif_stats['unread']}")
        
        return users
        
    except mysql.connector.Error as e:
        print(f"Error de base de datos: {e}")
        return []
    except Exception as e:
        print(f"Error inesperado: {e}")
        return []
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    check_users()