#!/usr/bin/env python3
"""
Script para agregar la columna organization_id a solicitudes_donaciones
"""
import mysql.connector

def add_organization_column():
    """Agrega la columna organization_id a solicitudes_donaciones"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor()
        
        print("=== AGREGANDO COLUMNA ORGANIZATION_ID ===\n")
        
        # Verificar si la columna ya existe
        cursor.execute("SHOW COLUMNS FROM solicitudes_donaciones LIKE 'organization_id'")
        if cursor.fetchone():
            print("✓ La columna organization_id ya existe")
        else:
            # Agregar la columna
            cursor.execute("""
                ALTER TABLE solicitudes_donaciones 
                ADD COLUMN organization_id INT NOT NULL DEFAULT 1,
                ADD INDEX idx_solicitudes_organization (organization_id)
            """)
            print("✓ Columna organization_id agregada")
        
        # Verificar que existe la organización 'empuje-comunitario'
        cursor.execute("SELECT id FROM organizaciones WHERE id = 'empuje-comunitario'")
        org_result = cursor.fetchone()
        
        if org_result:
            org_id = org_result[0]
            print(f"✓ Organización 'empuje-comunitario' encontrada con ID: {org_id}")
            
            # Como organization_id es INT pero el id de organizaciones es VARCHAR,
            # vamos a cambiar la columna para que sea VARCHAR
            cursor.execute("ALTER TABLE solicitudes_donaciones MODIFY organization_id VARCHAR(100) NOT NULL DEFAULT 'empuje-comunitario'")
            print("✓ Columna organization_id cambiada a VARCHAR")
            
            # Actualizar todas las solicitudes existentes para que pertenezcan a empuje-comunitario
            cursor.execute("""
                UPDATE solicitudes_donaciones 
                SET organization_id = %s 
                WHERE organization_id = '1' OR organization_id = 'empuje-comunitario'
            """, (org_id,))
            
            affected = cursor.rowcount
            print(f"✓ {affected} solicitudes actualizadas con organization_id = {org_id}")
        else:
            print("⚠ Organización 'empuje-comunitario' no encontrada, usando ID por defecto")
        
        # Verificar el resultado
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                organization_id,
                estado
            FROM solicitudes_donaciones 
            GROUP BY organization_id, estado
        """)
        
        results = cursor.fetchall()
        print("\n=== RESUMEN DE SOLICITUDES POR ORGANIZACIÓN ===")
        for result in results:
            print(f"  - Org ID {result[1]}: {result[0]} solicitudes en estado {result[2]}")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    add_organization_column()