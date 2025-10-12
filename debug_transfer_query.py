#!/usr/bin/env python3
"""
Debug de la consulta de transferencias
"""
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def debug_transfer_query():
    """Debug de la consulta de transferencias"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("=== TODAS LAS TRANSFERENCIAS ===")
        cursor.execute("SELECT * FROM transferencias_donaciones ORDER BY id DESC LIMIT 5")
        all_transfers = cursor.fetchall()
        
        for transfer in all_transfers:
            print(f"ID: {transfer['id']}")
            print(f"Tipo: {transfer['tipo']}")
            print(f"Contraparte: {transfer['organizacion_contraparte']}")
            print(f"Propietaria: {transfer['organizacion_propietaria']}")
            print("-" * 30)
        
        print("\n=== CONSULTA ESPECÍFICA PARA ESPERANZA-SOCIAL ===")
        cursor.execute("""
            SELECT * FROM transferencias_donaciones 
            WHERE organizacion_propietaria = 'esperanza-social'
            ORDER BY fecha_transferencia DESC
        """)
        
        esperanza_transfers = cursor.fetchall()
        print(f"Transferencias encontradas: {len(esperanza_transfers)}")
        
        for transfer in esperanza_transfers:
            print(f"ID: {transfer['id']}")
            print(f"Tipo: {transfer['tipo']}")
            print(f"Contraparte: {transfer['organizacion_contraparte']}")
            print(f"Propietaria: {transfer['organizacion_propietaria']}")
            print("-" * 30)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_transfer_query()