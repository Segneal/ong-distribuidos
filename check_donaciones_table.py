#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla donaciones
"""
import mysql.connector

def check_donaciones_table():
    """Verifica la estructura de la tabla donaciones"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor()
        
        print("=== ESTRUCTURA DE TABLA DONACIONES ===\n")
        
        # Verificar estructura
        cursor.execute("DESCRIBE donaciones")
        columns = cursor.fetchall()
        
        print("Columnas en la tabla donaciones:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}) - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
        
        # Verificar algunos datos
        print("\nPrimeros 5 registros:")
        cursor.execute("SELECT * FROM donaciones LIMIT 5")
        rows = cursor.fetchall()
        
        if rows:
            # Obtener nombres de columnas
            cursor.execute("SHOW COLUMNS FROM donaciones")
            column_names = [col[0] for col in cursor.fetchall()]
            print(f"Columnas: {column_names}")
            
            for i, row in enumerate(rows):
                print(f"  Registro {i+1}: {dict(zip(column_names, row))}")
        else:
            print("No hay datos en la tabla")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_donaciones_table()