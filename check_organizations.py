#!/usr/bin/env python3
"""
Script para verificar la estructura de organizaciones
"""
import mysql.connector

def check_organizations():
    """Verifica la estructura y datos de organizaciones"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor()
        
        print("=== VERIFICANDO ORGANIZACIONES ===\n")
        
        # Verificar estructura
        print("1. Estructura de la tabla organizaciones:")
        cursor.execute("DESCRIBE organizaciones")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[0]} ({col[1]}) - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
        
        # Verificar datos
        print("\n2. Datos en la tabla organizaciones:")
        cursor.execute("SELECT * FROM organizaciones")
        rows = cursor.fetchall()
        if rows:
            # Obtener nombres de columnas
            cursor.execute("SHOW COLUMNS FROM organizaciones")
            column_names = [col[0] for col in cursor.fetchall()]
            print(f"  Columnas: {column_names}")
            
            for row in rows:
                print(f"  - {dict(zip(column_names, row))}")
        else:
            print("  No hay datos en organizaciones")
        
        # Verificar si necesitamos crear la organización empuje-comunitario
        print("\n3. Buscando 'empuje-comunitario':")
        cursor.execute("SELECT * FROM organizaciones WHERE name = 'empuje-comunitario' OR nombre = 'empuje-comunitario'")
        result = cursor.fetchone()
        if result:
            print(f"  ✓ Encontrada: {result}")
        else:
            print("  ⚠ No encontrada")
            
            # Crear la organización si no existe
            try:
                cursor.execute("""
                    INSERT INTO organizaciones (name, description) 
                    VALUES ('empuje-comunitario', 'Organización Empuje Comunitario')
                """)
                conn.commit()
                print("  ✓ Organización 'empuje-comunitario' creada")
            except Exception as e:
                print(f"  Error creando organización: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_organizations()