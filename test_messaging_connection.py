#!/usr/bin/env python3
"""
Script para probar la conexión del messaging-service
"""
import os
import sys
sys.path.append('messaging-service/src')

from messaging.database.connection import test_database_connection, get_database_connection
from messaging.config import settings

def test_connection():
    """Prueba la conexión a la base de datos"""
    print("Configuración actual:")
    print(f"  DB_HOST: {settings.db_host}")
    print(f"  DB_PORT: {settings.db_port}")
    print(f"  DB_NAME: {settings.db_name}")
    print(f"  DB_USER: {settings.db_user}")
    print(f"  DB_PASSWORD: {'*' * len(settings.db_password)}")
    print()
    
    print("Probando conexión a la base de datos...")
    
    try:
        if test_database_connection():
            print("✓ Conexión exitosa!")
            
            # Probar una consulta simple
            with get_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print(f"✓ Tablas encontradas: {len(tables)}")
                for table in tables:
                    print(f"  - {table[0]}")
                    
                # Verificar tabla de solicitudes
                cursor.execute("SHOW TABLES LIKE 'solicitudes_donaciones'")
                if cursor.fetchone():
                    print("✓ Tabla 'solicitudes_donaciones' existe")
                    
                    # Contar registros
                    cursor.execute("SELECT COUNT(*) FROM solicitudes_donaciones")
                    count = cursor.fetchone()[0]
                    print(f"✓ Registros en solicitudes_donaciones: {count}")
                else:
                    print("⚠ Tabla 'solicitudes_donaciones' no existe")
                    
            return True
        else:
            print("✗ Error en la conexión")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    # Cargar variables de entorno desde .env
    env_path = "messaging-service/.env"
    if os.path.exists(env_path):
        print(f"Cargando variables de entorno desde {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print()
    
    if test_connection():
        print("\n🎉 Messaging-service puede conectarse correctamente!")
    else:
        print("\n❌ Error en la conexión del messaging-service")
        sys.exit(1)