#!/usr/bin/env python3
"""
Verificar estructura de tabla usuarios
"""
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def check_table_structure():
    """Verificar estructura de tablas"""
    print("🔍 VERIFICANDO ESTRUCTURA DE TABLAS")
    print("=" * 50)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Estructura de usuarios
        print("Tabla usuarios:")
        cursor.execute("DESCRIBE usuarios")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]} - {col[1]}")
        
        # Estructura de adhesiones_eventos_externos
        print("\nTabla adhesiones_eventos_externos:")
        cursor.execute("DESCRIBE adhesiones_eventos_externos")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]} - {col[1]}")
        
        # Datos de usuarios
        print("\nUsuarios existentes:")
        cursor.execute("SELECT id, nombre, apellido, email, organizacion, rol FROM usuarios LIMIT 10")
        users = cursor.fetchall()
        for user in users:
            print(f"  ID: {user[0]}, Nombre: {user[1]} {user[2]}, Org: {user[4]}, Rol: {user[5]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_table_structure()