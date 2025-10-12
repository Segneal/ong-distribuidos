#!/usr/bin/env python3
"""
Debug específico del problema de transferencias
"""
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def check_recent_transfers():
    """Verificar las transferencias más recientes"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("=== ÚLTIMAS 5 TRANSFERENCIAS ===")
        cursor.execute("""
            SELECT * FROM transferencias_donaciones 
            ORDER BY fecha_transferencia DESC 
            LIMIT 5
        """)
        
        transfers = cursor.fetchall()
        
        for transfer in transfers:
            print(f"ID: {transfer['id']}")
            print(f"Tipo: {transfer['tipo']}")
            print(f"Contraparte: {transfer['organizacion_contraparte']}")
            print(f"Propietaria: {transfer['organizacion_propietaria']}")
            print(f"Fecha: {transfer['fecha_transferencia']}")
            print(f"Donaciones: {transfer['donaciones']}")
            print("-" * 50)
        
        print("\n=== TRANSFERENCIAS POR ORGANIZACIÓN ===")
        cursor.execute("""
            SELECT organizacion_propietaria, tipo, COUNT(*) as total
            FROM transferencias_donaciones 
            GROUP BY organizacion_propietaria, tipo
            ORDER BY organizacion_propietaria, tipo
        """)
        
        stats = cursor.fetchall()
        for stat in stats:
            print(f"{stat['organizacion_propietaria']} - {stat['tipo']}: {stat['total']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_recent_transfers()