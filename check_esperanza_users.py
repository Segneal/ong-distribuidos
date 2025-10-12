#!/usr/bin/env python3
"""
Verificar usuarios de esperanza-social
"""
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def check_users():
    """Verificar usuarios"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("=== USUARIOS DE ESPERANZA-SOCIAL ===")
        cursor.execute("""
            SELECT id, nombre_usuario, organizacion, rol 
            FROM usuarios 
            WHERE organizacion = 'esperanza-social'
        """)
        
        users = cursor.fetchall()
        
        for user in users:
            print(f"ID: {user['id']}, Usuario: {user['nombre_usuario']}, Rol: {user['rol']}")
        
        print(f"\nTotal: {len(users)}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users()