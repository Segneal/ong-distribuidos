#!/usr/bin/env python3
"""
Arreglar password del usuario admin
"""
import mysql.connector
import hashlib

def fix_admin_password():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306
        )
        
        cursor = connection.cursor()
        
        print("🔧 ARREGLANDO PASSWORD DE ADMIN")
        print("=" * 35)
        
        # Generar hash SHA256 para admin123
        password = "admin123"
        new_hash = hashlib.sha256(password.encode()).hexdigest()
        
        print(f"Nuevo hash SHA256 para '{password}': {new_hash[:20]}...")
        
        # Actualizar usuario admin
        cursor.execute("""
            UPDATE usuarios 
            SET password_hash = %s 
            WHERE nombre_usuario = 'admin'
        """, (new_hash,))
        
        print(f"✅ Password de admin actualizado")
        
        # También arreglar otros usuarios si es necesario
        users_to_fix = [
            ('esperanza_admin', 'password123'),
            ('solidaria_admin', 'password123'),
            ('centro_admin', 'password123')
        ]
        
        for username, pwd in users_to_fix:
            pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()
            cursor.execute("""
                UPDATE usuarios 
                SET password_hash = %s 
                WHERE nombre_usuario = %s
            """, (pwd_hash, username))
            print(f"✅ Password de {username} actualizado")
        
        connection.commit()
        
        # Verificar
        print(f"\n🧪 VERIFICANDO:")
        cursor.execute("""
            SELECT nombre_usuario, password_hash 
            FROM usuarios 
            WHERE nombre_usuario IN ('admin', 'esperanza_admin', 'solidaria_admin', 'centro_admin')
        """)
        
        users = cursor.fetchall()
        for username, hash_val in users:
            print(f"  {username}: {hash_val[:20]}...")
        
        cursor.close()
        connection.close()
        
        print(f"\n✅ Passwords arreglados")
        print(f"Credenciales:")
        print(f"  admin / admin123")
        print(f"  esperanza_admin / password123")
        print(f"  solidaria_admin / password123")
        print(f"  centro_admin / password123")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_admin_password()