#!/usr/bin/env python3
"""
Script para debuggear las solicitudes de Fundación Esperanza
"""
import mysql.connector

def debug_esperanza_requests():
    """Debug de solicitudes de Fundación Esperanza"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor()
        
        print("=== DEBUG SOLICITUDES FUNDACIÓN ESPERANZA ===\n")
        
        # 1. Últimas solicitudes en solicitudes_donaciones
        print("1. Últimas solicitudes en solicitudes_donaciones:")
        cursor.execute("""
            SELECT 
                solicitud_id, 
                organization_id,
                estado,
                fecha_creacion
            FROM solicitudes_donaciones 
            ORDER BY fecha_creacion DESC 
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        for row in rows:
            print(f"  - {row[0]} | Org: {row[1]} | Estado: {row[2]} | Fecha: {row[3]}")
        
        # 2. Últimas solicitudes en solicitudes_externas
        print("\n2. Últimas solicitudes en solicitudes_externas:")
        cursor.execute("""
            SELECT 
                solicitud_id, 
                organizacion_solicitante,
                activa,
                fecha_creacion
            FROM solicitudes_externas 
            ORDER BY fecha_creacion DESC 
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        for row in rows:
            print(f"  - {row[0]} | Org: {row[1]} | Activa: {row[2]} | Fecha: {row[3]}")
        
        # 3. Solicitudes de fundacion-esperanza específicamente
        print("\n3. Solicitudes de fundacion-esperanza:")
        cursor.execute("""
            SELECT 
                solicitud_id, 
                organizacion_solicitante,
                activa,
                fecha_creacion,
                donaciones
            FROM solicitudes_externas 
            WHERE organizacion_solicitante = 'fundacion-esperanza'
            ORDER BY fecha_creacion DESC
        """)
        
        rows = cursor.fetchall()
        print(f"Total encontradas: {len(rows)}")
        for row in rows:
            print(f"  - {row[0]} | Activa: {row[2]} | Fecha: {row[3]}")
            print(f"    Donaciones: {row[4][:100]}...")
        
        # 4. Verificar si hay solicitudes con IDs incorrectos
        print("\n4. Solicitudes con IDs que no coinciden con la organización:")
        cursor.execute("""
            SELECT 
                solicitud_id, 
                organizacion_solicitante,
                activa
            FROM solicitudes_externas 
            WHERE organizacion_solicitante = 'fundacion-esperanza'
            AND solicitud_id LIKE 'req-empuje-comunitario%'
        """)
        
        rows = cursor.fetchall()
        if rows:
            print(f"Encontradas {len(rows)} solicitudes con ID incorrecto:")
            for row in rows:
                print(f"  - {row[0]} | Org: {row[1]} | Activa: {row[2]}")
        else:
            print("No se encontraron solicitudes con IDs incorrectos")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    debug_esperanza_requests()