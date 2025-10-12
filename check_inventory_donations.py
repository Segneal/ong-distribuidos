#!/usr/bin/env python3
"""
Verificar donaciones disponibles en el inventario
"""
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def check_inventory():
    """Verificar inventario de donaciones"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("=== DONACIONES DISPONIBLES ===")
        cursor.execute("""
            SELECT id, categoria, descripcion, cantidad, eliminado
            FROM donaciones 
            WHERE eliminado = 0 AND cantidad > 0
            ORDER BY id
        """)
        
        donations = cursor.fetchall()
        
        for donation in donations:
            print(f"ID: {donation['id']}")
            print(f"Categoría: {donation['categoria']}")
            print(f"Descripción: {donation['descripcion']}")
            print(f"Cantidad: {donation['cantidad']}")
            print("-" * 30)
        
        print(f"\nTotal donaciones disponibles: {len(donations)}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_inventory()