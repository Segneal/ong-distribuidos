#!/usr/bin/env python3
"""
Script para aplicar la migración de notificaciones
"""

import mysql.connector
import sys
import os

def apply_migration():
    """Aplicar la migración de notificaciones"""
    
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
        # Conectar a la base de datos
        print("Conectando a la base de datos...")
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Leer el archivo de migración
        migration_file = 'database/notifications_migration.sql'
        if not os.path.exists(migration_file):
            print(f"Error: No se encontró el archivo {migration_file}")
            return False
        
        with open(migration_file, 'r', encoding='utf-8') as file:
            migration_sql = file.read()
        
        # Dividir en comandos individuales
        commands = [cmd.strip() for cmd in migration_sql.split(';') if cmd.strip()]
        
        print(f"Aplicando {len(commands)} comandos de migración...")
        
        for i, command in enumerate(commands, 1):
            if command.strip():
                try:
                    print(f"Ejecutando comando {i}/{len(commands)}...")
                    cursor.execute(command)
                    connection.commit()
                    print(f"✓ Comando {i} ejecutado exitosamente")
                except mysql.connector.Error as e:
                    if "already exists" in str(e) or "Duplicate" in str(e):
                        print(f"⚠ Comando {i} ya aplicado anteriormente: {e}")
                    else:
                        print(f"✗ Error en comando {i}: {e}")
                        return False
        
        print("\n✅ Migración de notificaciones aplicada exitosamente!")
        print("\nTabla creada:")
        print("- notificaciones_usuarios: Para almacenar notificaciones de usuarios")
        
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
            print("Conexión cerrada.")

if __name__ == "__main__":
    print("=== Migración de Sistema de Notificaciones ===")
    success = apply_migration()
    sys.exit(0 if success else 1)