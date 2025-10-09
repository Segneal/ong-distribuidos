#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla solicitudes_externas
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_mysql import get_db_connection

def check_solicitudes_table():
    """Verificar la estructura de la tabla solicitudes_externas"""
    try:
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 VERIFICANDO TABLA solicitudes_externas")
        print("=" * 50)
        
        # Verificar si la tabla existe
        cursor.execute("SHOW TABLES LIKE 'solicitudes_externas'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ La tabla solicitudes_externas no existe")
            cursor.close()
            conn.close()
            return
        
        print("✅ La tabla solicitudes_externas existe")
        
        # Mostrar estructura de la tabla
        cursor.execute("DESCRIBE solicitudes_externas")
        columns = cursor.fetchall()
        
        print(f"\n📋 ESTRUCTURA DE LA TABLA:")
        for column in columns:
            print(f"  📝 {column['Field']}: {column['Type']} "
                  f"{'NULL' if column['Null'] == 'YES' else 'NOT NULL'} "
                  f"{column['Default'] if column['Default'] else ''}")
        
        # Verificar datos existentes
        cursor.execute("SELECT COUNT(*) as total FROM solicitudes_externas")
        count = cursor.fetchone()
        print(f"\n📊 Total registros: {count['total']}")
        
        if count['total'] > 0:
            cursor.execute("SELECT * FROM solicitudes_externas LIMIT 3")
            samples = cursor.fetchall()
            print(f"\n📋 EJEMPLOS DE DATOS:")
            for i, sample in enumerate(samples, 1):
                print(f"  {i}. ID: {sample['id']}")
                print(f"     Solicitud ID: {sample['solicitud_id']}")
                print(f"     Organización: {sample['organizacion_solicitante']}")
                print(f"     Activa: {sample['activa']}")
                print(f"     Fecha: {sample['fecha_creacion']}")
                print()
        
        cursor.close()
        conn.close()
        
        print(f"🎉 VERIFICACIÓN COMPLETADA")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_solicitudes_table()