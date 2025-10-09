#!/usr/bin/env python3
import mysql.connector

def add_organization_to_events():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306
        )
        
        cursor = connection.cursor()
        
        print("🔧 AGREGANDO ORGANIZACIÓN A EVENTOS")
        print("=" * 40)
        
        # Verificar si el campo ya existe en eventos
        cursor.execute("DESCRIBE eventos")
        columns = [col[0] for col in cursor.fetchall()]
        
        if 'organizacion' not in columns:
            print("Agregando campo organizacion a tabla eventos...")
            cursor.execute("ALTER TABLE eventos ADD COLUMN organizacion VARCHAR(100) DEFAULT 'empuje-comunitario'")
            print("✅ Campo organizacion agregado a eventos")
        else:
            print("✅ Campo organizacion ya existe en eventos")
        
        # Actualizar eventos existentes sin organización
        cursor.execute("UPDATE eventos SET organizacion = 'empuje-comunitario' WHERE organizacion IS NULL")
        print(f"✅ {cursor.rowcount} eventos actualizados")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ Eventos actualizados para multi-organización")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_organization_to_events()