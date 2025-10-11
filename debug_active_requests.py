#!/usr/bin/env python3
"""
Script para debuggear las solicitudes activas
"""
import mysql.connector

def debug_active_requests():
    """Debug de solicitudes activas"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor()
        
        print("=== DEBUG SOLICITUDES ACTIVAS ===\n")
        
        # 1. Ver todas las solicitudes
        print("1. Todas las solicitudes en solicitudes_donaciones:")
        cursor.execute("""
            SELECT 
                solicitud_id, 
                organization_id,
                estado,
                fecha_creacion
            FROM solicitudes_donaciones 
            ORDER BY fecha_creacion DESC 
            LIMIT 10
        """)
        
        all_requests = cursor.fetchall()
        for req in all_requests:
            print(f"  - {req[0]} | Org: {req[1]} | Estado: {req[2]} | Fecha: {req[3]}")
        
        # 2. Solicitudes activas de empuje-comunitario
        print("\n2. Solicitudes activas de empuje-comunitario:")
        cursor.execute("""
            SELECT 
                solicitud_id, 
                organization_id,
                estado,
                fecha_creacion,
                donaciones
            FROM solicitudes_donaciones 
            WHERE estado = 'ACTIVA'
            AND organization_id = 'empuje-comunitario'
            ORDER BY fecha_creacion DESC
        """)
        
        active_requests = cursor.fetchall()
        print(f"Total encontradas: {len(active_requests)}")
        for req in active_requests:
            print(f"  - {req[0]} | Org: {req[1]} | Estado: {req[2]}")
            print(f"    Donaciones: {req[4][:100]}...")
        
        # 3. Verificar si hay problemas con los estados
        print("\n3. Estados únicos en la tabla:")
        cursor.execute("SELECT DISTINCT estado FROM solicitudes_donaciones")
        states = cursor.fetchall()
        for state in states:
            print(f"  - '{state[0]}'")
        
        # 4. Contar por estado y organización
        print("\n4. Conteo por estado y organización:")
        cursor.execute("""
            SELECT 
                organization_id,
                estado,
                COUNT(*) as count
            FROM solicitudes_donaciones 
            GROUP BY organization_id, estado
        """)
        
        counts = cursor.fetchall()
        for count in counts:
            print(f"  - Org: {count[0]} | Estado: {count[1]} | Count: {count[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    debug_active_requests()