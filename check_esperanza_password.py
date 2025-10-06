#!/usr/bin/env python3
"""
Script para verificar el hash de la contraseña de esperanza_admin
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))

from database_mysql import get_db_connection
import bcrypt
import hashlib

def check_esperanza_password():
    """Verificar hash de contraseña de esperanza_admin"""
    try:
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT nombre_usuario, email, password_hash, organizacion
            FROM usuarios 
            WHERE nombre_usuario = 'esperanza_admin'
        """)
        
        user = cursor.fetchone()
        
        if user:
            print(f"👤 Usuario: {user['nombre_usuario']}")
            print(f"📧 Email: {user['email']}")
            print(f"🏢 Organización: {user['organizacion']}")
            print(f"🔐 Hash completo: {user['password_hash']}")
            
            # Probar diferentes contraseñas con MD5
            passwords_to_test = ['password123', 'admin123', 'admin', '123456']
            
            print("\n🧪 PROBANDO CONTRASEÑAS (MD5):")
            for pwd in passwords_to_test:
                md5_hash = hashlib.md5(pwd.encode('utf-8')).hexdigest()
                if md5_hash == user['password_hash']:
                    print(f"✅ '{pwd}' - CORRECTA! (MD5)")
                    return pwd
                else:
                    print(f"❌ '{pwd}' - Incorrecta (MD5: {md5_hash[:20]}...)")
            
            print("\n🧪 PROBANDO CONTRASEÑAS (bcrypt):")
            for pwd in passwords_to_test:
                try:
                    if bcrypt.checkpw(pwd.encode('utf-8'), user['password_hash'].encode('utf-8')):
                        print(f"✅ '{pwd}' - CORRECTA! (bcrypt)")
                        return pwd
                    else:
                        print(f"❌ '{pwd}' - Incorrecta (bcrypt)")
                except Exception as e:
                    print(f"❌ '{pwd}' - Error bcrypt: {e}")
            
            print("\n💡 Vamos a resetear la contraseña a 'password123'")
            
            # Generar nuevo hash
            new_password = 'password123'
            salt = bcrypt.gensalt()
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt)
            
            cursor.execute("""
                UPDATE usuarios 
                SET password_hash = %s 
                WHERE nombre_usuario = 'esperanza_admin'
            """, (new_hash.decode('utf-8'),))
            
            conn.commit()
            print(f"✅ Contraseña actualizada a: {new_password}")
            
        else:
            print("❌ Usuario esperanza_admin no encontrado")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_esperanza_password()