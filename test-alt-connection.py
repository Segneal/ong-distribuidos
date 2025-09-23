#!/usr/bin/env python3
"""
Script para probar la conexión alternativa a la base de datos
"""
import sys
import os

# Agregar el directorio de user-service al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_alt import test_connection

def main():
    print("🔍 Probando conexión alternativa a la base de datos...")
    print("=" * 50)
    
    if test_connection():
        print("🎉 ¡Conexión exitosa!")
        return 0
    else:
        print("❌ Error de conexión")
        return 1

if __name__ == "__main__":
    exit(main())