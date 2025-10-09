#!/usr/bin/env python3
"""
Verificar password del usuario admin
"""
import mysql.connector
import hashlib
import sys
import os
sys.path.append('user-service/src')

def check_admin_password():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306
        )
        
        cursor = connection.cursor()
        
        print("🔍 VERIFICANDO PASSWORD DE ADMIN")
        print("=" * 40)
        
        # Buscar usuario admin
        cursor.execute("""
            SELECT nombre_usuario, password_hash, organizacion
            FROM usuarios 
            WHERE nombre_usuario = 'admin'
        """)
        
        user = cursor.fetchone()
        if user:
            username, stored_hash, org = user
            print(f"Usuario: {username}")
            print(f"Organización: {org}")
            print(f"Hash almacenado: {stored_hash[:50]}...")
            print(f"Tipo de hash: {'bcrypt' if stored_hash.startswith('$2b$') else 'SHA256'}")
            
            # Probar diferentes passwords
            test_passwords = ['admin123', 'password123']
            
            from crypto import verify_password
            
            for password in test_passwords:
                result = verify_password(password, stored_hash)
                print(f"Password '{password}': {'✅ CORRECTO' if result else '❌ INCORRECTO'}")
                
                # También mostrar hash manual
                if not stored_hash.startswith('$2b$'):
                    manual_hash = hashlib.sha256(password.encode()).hexdigest()
                    print(f"  SHA256 manual: {manual_hash[:20]}...")
                    print(f"  Match manual: {'✅' if manual_hash == stored_hash else '❌'}")
        else:
            print("❌ Usuario admin no encontrado")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_admin_password()