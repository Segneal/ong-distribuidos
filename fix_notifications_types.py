#!/usr/bin/env python3
"""
Script para corregir los tipos de notificación
"""

import mysql.connector
import sys

def fix_notification_types():
    """Corregir los tipos de notificación en la tabla"""
    
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
        print("=== Corrección de Tipos de Notificación ===")
        
        # Conectar a la base de datos
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Corregir el ENUM de tipos
        print("1. Corrigiendo tipos de notificación...")
        cursor.execute("""
            ALTER TABLE notificaciones_usuarios 
            MODIFY COLUMN tipo ENUM('INFO', 'SUCCESS', 'WARNING', 'ERROR') DEFAULT 'INFO'
        """)
        
        connection.commit()
        print("✓ Tipos de notificación corregidos")
        
        # Verificar la corrección
        print("\n2. Verificando corrección...")
        cursor.execute("DESCRIBE notificaciones_usuarios")
        columns = cursor.fetchall()
        
        for col in columns:
            if col[0] == 'tipo':
                print(f"✓ Columna tipo: {col[1]}")
                break
        
        print("\n✅ Corrección aplicada exitosamente!")
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
    fix_notification_types()