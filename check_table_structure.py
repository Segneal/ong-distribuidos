#!/usr/bin/env python3
"""
Script para verificar la estructura de las tablas
"""
import mysql.connector

def check_table_structure():
    """Verifica la estructura de las tablas"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor()
        
        print("=== ESTRUCTURA DE TABLAS ===\n")
        
        # Verificar estructura de solicitudes_donaciones
        print("1. Estructura de solicitudes_donaciones:")
        cursor.execute("DESCRIBE solicitudes_donaciones")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[0]} ({col[1]}) - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
        
        # Verificar estructura de solicitudes_externas
        print("\n2. Estructura de solicitudes_externas:")
        try:
            cursor.execute("DESCRIBE solicitudes_externas")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[0]} ({col[1]}) - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Verificar datos actuales en solicitudes_donaciones
        print("\n3. Datos actuales en solicitudes_donaciones:")
        cursor.execute("SELECT * FROM solicitudes_donaciones ORDER BY fecha_creacion DESC LIMIT 3")
        rows = cursor.fetchall()
        if rows:
            # Obtener nombres de columnas
            cursor.execute("SHOW COLUMNS FROM solicitudes_donaciones")
            column_names = [col[0] for col in cursor.fetchall()]
            print(f"  Columnas: {column_names}")
            
            for row in rows:
                print(f"  - {dict(zip(column_names, row))}")
        else:
            print("  No hay datos")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_table_structure()