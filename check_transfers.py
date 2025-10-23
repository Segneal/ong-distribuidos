#!/usr/bin/env python3
"""
Script para revisar las transferencias en la base de datos
"""
import pymysql
import json

def check_transfers():
    try:
        # Conectar a la base de datos
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Verificar transferencias
        print("=== TRANSFERENCIAS DE DONACIONES ===")
        cursor.execute("""
            SELECT id, tipo, organizacion_contraparte, donaciones, estado, 
                   fecha_transferencia, usuario_registro, notas
            FROM transferencias_donaciones 
            ORDER BY fecha_transferencia DESC
        """)
        transfers = cursor.fetchall()
        
        for transfer in transfers:
            print(f"\n--- Transferencia ID: {transfer[0]} ---")
            print(f"  Tipo: {transfer[1]}")
            print(f"  Organización: {transfer[2]}")
            print(f"  Estado: {transfer[4]}")
            print(f"  Fecha: {transfer[5]}")
            print(f"  Usuario: {transfer[6]}")
            print(f"  Notas: {transfer[7]}")
            
            # Parse donaciones JSON
            try:
                donaciones = json.loads(transfer[3])
                print(f"  Donaciones:")
                for donacion in donaciones:
                    print(f"    - {donacion.get('categoria', 'N/A')}: {donacion.get('descripcion', 'N/A')} ({donacion.get('cantidad', 'N/A')})")
            except:
                print(f"  Donaciones (raw): {transfer[3]}")
        
        # Verificar si existe el campo organizacion_propietaria
        print("\n=== ESTRUCTURA DE TABLA ===")
        cursor.execute("DESCRIBE transferencias_donaciones")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]}: {col[1]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_transfers()