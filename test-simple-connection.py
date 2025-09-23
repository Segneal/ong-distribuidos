#!/usr/bin/env python3
"""
Script simple para probar la conexión a la base de datos
"""
import psycopg2
import os

def test_simple_connection():
    try:
        # Configuración simple
        conn = psycopg2.connect(
            host='localhost',
            database='ong_management',
            user='ong_user',
            password='ong_pass',
            port='5432'
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print("✅ Conexión exitosa!")
        print(f"✅ Resultado de prueba: {result[0]}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Probando conexión simple...")
    if test_simple_connection():
        print("🎉 ¡La base de datos está lista!")
    else:
        print("❌ Problema de conexión")