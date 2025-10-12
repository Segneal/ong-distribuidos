#!/usr/bin/env python3
"""
Verificar la estructura de las tablas de transferencias
"""
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def check_tables():
    """Verificar estructura de tablas"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=== TABLAS EXISTENTES ===")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        for table in tables:
            print(f"- {table[0]}")
        
        print("\n=== ESTRUCTURA DE TRANSFERENCIAS_DONACIONES ===")
        try:
            cursor.execute("DESCRIBE transferencias_donaciones")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"- {col[0]} ({col[1]}) - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n=== ESTRUCTURA DE DONACIONES_TRANSFERIDAS ===")
        try:
            cursor.execute("DESCRIBE donaciones_transferidas")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"- {col[0]} ({col[1]}) - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n=== ESTRUCTURA DE NOTIFICACIONES ===")
        try:
            cursor.execute("DESCRIBE notificaciones")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"- {col[0]} ({col[1]}) - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n=== DATOS EN TRANSFERENCIAS_DONACIONES ===")
        try:
            cursor.execute("SELECT * FROM transferencias_donaciones LIMIT 5")
            transfers = cursor.fetchall()
            
            if transfers:
                # Obtener nombres de columnas
                cursor.execute("SHOW COLUMNS FROM transferencias_donaciones")
                columns = [col[0] for col in cursor.fetchall()]
                print(f"Columnas: {columns}")
                
                for transfer in transfers:
                    print(f"Registro: {transfer}")
            else:
                print("No hay datos en transferencias_donaciones")
        except Exception as e:
            print(f"Error: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    check_tables()