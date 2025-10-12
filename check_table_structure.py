#!/usr/bin/env python3
"""
Script para verificar estructura de tablas
"""

import mysql.connector

def check_table_structure():
    """Verificar estructura de tablas"""
    
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
        print("=== Verificación de Estructura de Tablas ===")
        
        # Conectar a la base de datos
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Verificar estructura de usuarios
        print("1. Estructura de tabla usuarios:")
        cursor.execute("DESCRIBE usuarios")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"  - {col[0]}: {col[1]} ({col[2]}, {col[4]})")
        
        # Verificar algunos usuarios
        print("\n2. Algunos usuarios de ejemplo:")
        cursor.execute("SELECT * FROM usuarios LIMIT 3")
        users = cursor.fetchall()
        
        if users:
            # Obtener nombres de columnas
            cursor.execute("SHOW COLUMNS FROM usuarios")
            column_names = [col[0] for col in cursor.fetchall()]
            print(f"Columnas: {column_names}")
            
            for user in users:
                print(f"  - Usuario: {user}")
        else:
            print("  - No hay usuarios en la tabla")
        
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
    check_table_structure()