#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos
"""
import sys
import os

# Agregar el directorio de user-service al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database import test_connection

def main():
    print("🔍 Probando conexión a la base de datos...")
    print("=" * 50)
    
    # Mostrar configuración
    print("📋 Configuración de conexión:")
    print(f"  Host: {os.getenv('DB_HOST', 'localhost')}")
    print(f"  Database: {os.getenv('DB_NAME', 'ong_management')}")
    print(f"  User: {os.getenv('DB_USER', 'ong_user')}")
    print(f"  Port: {os.getenv('DB_PORT', '5432')}")
    print()
    
    # Probar conexión
    if test_connection():
        print("🎉 ¡Conexión exitosa!")
        print("✅ La base de datos está lista para usar")
        return 0
    else:
        print("❌ Error de conexión")
        print("💡 Verifica que:")
        print("  1. PostgreSQL esté ejecutándose")
        print("  2. La base de datos 'ong_management' exista")
        print("  3. El usuario 'ong_user' tenga permisos")
        print("  4. Las credenciales en .env sean correctas")
        return 1

if __name__ == "__main__":
    exit(main())