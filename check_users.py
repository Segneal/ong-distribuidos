#!/usr/bin/env python3
"""
Script para verificar qué usuarios existen en la base de datos
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_mysql import get_db_connection

def check_users():
    """Verificar usuarios existentes"""
    try:
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 USUARIOS EN LA BASE DE DATOS:")
        print("=" * 60)
        
        # Primero ver la estructura de la tabla
        cursor.execute("DESCRIBE usuarios")
        columns = cursor.fetchall()
        print("📋 ESTRUCTURA DE LA TABLA USUARIOS:")
        for col in columns:
            print(f"  - {col['Field']}: {col['Type']}")
        
        print("\n" + "=" * 60)
        
        cursor.execute("""
            SELECT id, nombre_usuario, email, organizacion, rol, activo 
            FROM usuarios 
            ORDER BY organizacion, rol, nombre_usuario
        """)
        
        users = cursor.fetchall()
        
        current_org = None
        for user in users:
            if user['organizacion'] != current_org:
                current_org = user['organizacion']
                print(f"\n🏢 {current_org.upper()}")
                print("-" * 40)
            
            status = "✅ ACTIVO" if user['activo'] else "❌ INACTIVO"
            print(f"  👤 {user['nombre_usuario']} ({user['email']})")
            print(f"     Rol: {user['rol']} | ID: {user['id']} | {status}")
        
        cursor.close()
        conn.close()
        
        print(f"\n📊 Total de usuarios: {len(users)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_users()