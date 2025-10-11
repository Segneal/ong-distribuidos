#!/usr/bin/env python3
"""
Script para verificar usuarios existentes
"""
import mysql.connector

def check_users():
    """Verifica usuarios existentes"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor()
        
        print("=== VERIFICANDO USUARIOS ===\n")
        
        # Verificar estructura de usuarios
        cursor.execute("DESCRIBE usuarios")
        columns = cursor.fetchall()
        print("Estructura de usuarios:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        # Verificar usuarios
        cursor.execute("SELECT * FROM usuarios LIMIT 5")
        users = cursor.fetchall()
        
        if users:
            # Obtener nombres de columnas
            cursor.execute("SHOW COLUMNS FROM usuarios")
            column_names = [col[0] for col in cursor.fetchall()]
            print(f"\nColumnas: {column_names}")
        
        # Buscar usuarios específicos
        cursor.execute("SELECT id, nombre_usuario, organizacion FROM usuarios WHERE nombre_usuario IN ('admin', 'esperanza_admin')")
        specific_users = cursor.fetchall()
        
        if users:
            print("\nPrimeros usuarios:")
            for i, user in enumerate(users):
                print(f"  - Usuario {i+1}: {user}")
        else:
            print("No hay usuarios en la base de datos")
        
        if specific_users:
            print("\nUsuarios específicos encontrados:")
            for user in specific_users:
                print(f"  - ID: {user[0]}, Username: {user[1]}, Org: {user[2]}")
        
        conn.close()
        return specific_users[0][0] if specific_users else (users[0][0] if users else None)
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    user_id = check_users()
    if user_id:
        print(f"\nUsando usuario ID: {user_id} para las pruebas")
    else:
        print("\nNo se encontraron usuarios válidos")