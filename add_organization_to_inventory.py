#!/usr/bin/env python3
import mysql.connector

def add_organization_to_inventory():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306
        )
        
        cursor = connection.cursor()
        
        print("🔧 AGREGANDO ORGANIZACIÓN A INVENTARIO")
        print("=" * 40)
        
        # Verificar si el campo ya existe
        cursor.execute("DESCRIBE donaciones")
        columns = [col[0] for col in cursor.fetchall()]
        
        if 'organizacion' not in columns:
            print("Agregando campo organizacion a tabla donaciones...")
            cursor.execute("ALTER TABLE donaciones ADD COLUMN organizacion VARCHAR(100) DEFAULT 'empuje-comunitario'")
            print("✅ Campo organizacion agregado a donaciones")
        else:
            print("✅ Campo organizacion ya existe en donaciones")
        
        # Actualizar donaciones existentes sin organización
        cursor.execute("UPDATE donaciones SET organizacion = 'empuje-comunitario' WHERE organizacion IS NULL")
        print(f"✅ {cursor.rowcount} donaciones actualizadas")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ Inventario actualizado para multi-organización")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_organization_to_inventory()