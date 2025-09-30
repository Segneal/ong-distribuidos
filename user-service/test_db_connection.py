#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
import os
import sys
import locale

# Configurar encoding para Windows
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        locale.setlocale(locale.LC_ALL, 'C')
    except:
        pass

def test_connection():
    try:
        print("Probando conexion a PostgreSQL...")
        
        # Parámetros de conexión básicos (sin encoding especial)
        connection_params = {
            'host': 'localhost',
            'database': 'ong_management',
            'user': 'ong_user',
            'password': 'ong_pass',
            'port': 5432
        }
        
        print(f"Conectando a: {connection_params['host']}:{connection_params['port']}")
        print(f"Base de datos: {connection_params['database']}")
        print(f"Usuario: {connection_params['user']}")
        
        # Intentar conexión básica
        conn = psycopg2.connect(**connection_params)
        
        print("Conexion exitosa!")
        
        # Probar query simple
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"PostgreSQL version: {str(version[0])[:50]}...")
            
            # Probar query con datos de usuarios
            cursor.execute("SELECT COUNT(*) FROM usuarios;")
            count = cursor.fetchone()
            print(f"Usuarios en la base: {count[0]}")
            
            # Probar query que podría tener caracteres especiales
            cursor.execute("SELECT nombre_usuario FROM usuarios LIMIT 1;")
            user = cursor.fetchone()
            if user:
                print(f"Usuario de prueba: {user[0]}")
        
        conn.close()
        print("Test completado exitosamente")
        return True
        
    except Exception as e:
        print(f"Error: {type(e).__name__}")
        try:
            print(f"Mensaje: {repr(e)}")
        except:
            print("Error al mostrar mensaje de error")
            
        return False

if __name__ == "__main__":
    test_connection()