#!/usr/bin/env python3
"""
Script para debuggear qué solicitudes ve el usuario de Fundación Esperanza
"""
import mysql.connector

def debug_esperanza_active_requests():
    """Debug de solicitudes activas que ve Fundación Esperanza"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor()
        
        print("=== DEBUG SOLICITUDES ACTIVAS FUNDACIÓN ESPERANZA ===\n")
        
        # Simular la consulta que hace el API Gateway para fundacion-esperanza
        print("1. Consulta que hace el API Gateway para fundacion-esperanza:")
        query = """
            SELECT 
              solicitud_id as request_id,
              donaciones as donations,
              activa as status,
              fecha_creacion as timestamp,
              '' as notes
            FROM solicitudes_externas 
            WHERE activa = 1
            AND organizacion_solicitante = 'fundacion-esperanza'
            ORDER BY fecha_creacion DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        print(f"Resultados encontrados: {len(rows)}")
        for row in rows:
            print(f"  - {row[0]} | Status: {row[2]} | Fecha: {row[3]}")
        
        # 2. Ver todas las solicitudes activas en solicitudes_externas
        print("\n2. Todas las solicitudes activas en solicitudes_externas:")
        cursor.execute("""
            SELECT 
                solicitud_id, 
                organizacion_solicitante,
                activa,
                fecha_creacion
            FROM solicitudes_externas 
            WHERE activa = 1
            ORDER BY fecha_creacion DESC
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        for row in rows:
            print(f"  - {row[0]} | Org: {row[1]} | Activa: {row[2]} | Fecha: {row[3]}")
        
        # 3. Verificar si hay solicitudes que deberían pertenecer a fundacion-esperanza
        # pero están mal etiquetadas
        print("\n3. Solicitudes recientes que podrían ser de fundacion-esperanza:")
        cursor.execute("""
            SELECT 
                solicitud_id, 
                organizacion_solicitante,
                donaciones,
                fecha_creacion
            FROM solicitudes_externas 
            WHERE fecha_creacion >= DATE_SUB(NOW(), INTERVAL 1 HOUR)
            ORDER BY fecha_creacion DESC
        """)
        
        rows = cursor.fetchall()
        for row in rows:
            donations_text = row[2][:100] if row[2] else ""
            print(f"  - {row[0]} | Org: {row[1]} | Fecha: {row[3]}")
            print(f"    Donaciones: {donations_text}...")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    debug_esperanza_active_requests()