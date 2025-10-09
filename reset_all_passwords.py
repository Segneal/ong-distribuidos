#!/usr/bin/env python3
"""
Resetear todas las passwords a 'admin'
"""
import mysql.connector
import hashlib

def reset_all_passwords():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306
        )
        
        cursor = connection.cursor()
        
        print("🔧 RESETEANDO TODAS LAS PASSWORDS A 'admin'")
        print("=" * 45)
        
        # Generar hash SHA256 para 'admin'
        password = "admin"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        print(f"Hash SHA256 para '{password}': {password_hash[:20]}...")
        
        # Actualizar TODOS los usuarios
        cursor.execute("""
            UPDATE usuarios 
            SET password_hash = %s
        """, (password_hash,))
        
        affected_rows = cursor.rowcount
        connection.commit()
        
        print(f"✅ {affected_rows} usuarios actualizados")
        
        # Mostrar todos los usuarios
        cursor.execute("""
            SELECT nombre_usuario, organizacion, rol
            FROM usuarios 
            ORDER BY organizacion, rol
        """)
        
        users = cursor.fetchall()
        
        print(f"\n📋 USUARIOS ACTUALIZADOS (password: 'admin'):")
        current_org = None
        
        for username, org, role in users:
            if org != current_org:
                current_org = org
                print(f"\n  🏢 {org.upper()}:")
            print(f"    - {username} | {role}")
        
        cursor.close()
        connection.close()
        
        print(f"\n✅ TODAS LAS PASSWORDS RESETEADAS")
        print(f"🔑 Password universal: admin")
        print(f"📝 Ejemplos de login:")
        print(f"   - admin / admin")
        print(f"   - esperanza_admin / admin")
        print(f"   - solidaria_admin / admin")
        print(f"   - centro_admin / admin")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    reset_all_passwords()