#!/usr/bin/env python3
"""
Script para verificar los datos de solicitudes en la base de datos
"""
import mysql.connector

def check_requests_data():
    """Verifica los datos de solicitudes en las tablas"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor(dictionary=True)
        
        print("=== VERIFICANDO DATOS DE SOLICITUDES ===\n")
        
        # Verificar tabla solicitudes_donaciones
        print("1. Tabla solicitudes_donaciones:")
        cursor.execute("""
            SELECT 
                solicitud_id, 
                organization_id,
                estado,
                fecha_creacion,
                donaciones
            FROM solicitudes_donaciones 
            ORDER BY fecha_creacion DESC 
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(f"  - ID: {row['solicitud_id']}")
                print(f"    Org ID: {row['organization_id']}")
                print(f"    Estado: {row['estado']}")
                print(f"    Fecha: {row['fecha_creacion']}")
                print(f"    Donaciones: {row['donaciones'][:100]}...")
                print()
        else:
            print("  No hay datos en solicitudes_donaciones")
        
        # Verificar tabla solicitudes_externas
        print("\n2. Tabla solicitudes_externas:")
        cursor.execute("""
            SELECT 
                solicitud_id, 
                organizacion_solicitante,
                estado,
                fecha_creacion,
                donaciones
            FROM solicitudes_externas 
            ORDER BY fecha_creacion DESC 
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(f"  - ID: {row['solicitud_id']}")
                print(f"    Org: {row['organizacion_solicitante']}")
                print(f"    Estado: {row['estado']}")
                print(f"    Fecha: {row['fecha_creacion']}")
                print(f"    Donaciones: {row['donaciones'][:100]}...")
                print()
        else:
            print("  No hay datos en solicitudes_externas")
        
        # Verificar organizaciones
        print("\n3. Organizaciones disponibles:")
        cursor.execute("SELECT id, nombre FROM organizaciones")
        orgs = cursor.fetchall()
        for org in orgs:
            print(f"  - ID: {org['id']}, Nombre: {org['nombre']}")
        
        # Verificar relación entre solicitudes y organizaciones
        print("\n4. Solicitudes por organización:")
        cursor.execute("""
            SELECT 
                o.nombre as organizacion,
                COUNT(sd.id) as total_solicitudes,
                COUNT(CASE WHEN sd.estado = 'ACTIVA' THEN 1 END) as activas
            FROM organizaciones o
            LEFT JOIN solicitudes_donaciones sd ON o.id = sd.organization_id
            GROUP BY o.id, o.nombre
        """)
        
        stats = cursor.fetchall()
        for stat in stats:
            print(f"  - {stat['organizacion']}: {stat['total_solicitudes']} total, {stat['activas']} activas")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_requests_data()