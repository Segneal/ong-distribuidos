#!/usr/bin/env python3
"""
Verificar usuarios de Esperanza Social
"""
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def check_users():
    """Verificar usuarios en la base de datos"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("=== TODOS LOS USUARIOS ===")
        cursor.execute("SELECT id, nombre_usuario, email, organizacion, rol FROM usuarios")
        users = cursor.fetchall()
        
        for user in users:
            print(f"ID: {user['id']}")
            print(f"Usuario: {user['nombre_usuario']}")
            print(f"Email: {user['email']}")
            print(f"Organización: {user['organizacion']}")
            print(f"Rol: {user['rol']}")
            print("-" * 30)
        
        print(f"\nTotal usuarios: {len(users)}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users()