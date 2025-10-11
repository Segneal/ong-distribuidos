#!/usr/bin/env python3
"""
Script para verificar la contraseña del usuario admin
"""
import mysql.connector
import bcrypt

def verify_admin_password():
    """Verifica la contraseña del usuario admin"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor()
        
        print("=== VERIFICANDO CONTRASEÑA DE ADMIN ===\n")
        
        # Obtener el hash de la contraseña del admin
        cursor.execute("SELECT nombre_usuario, password_hash FROM usuarios WHERE nombre_usuario = 'admin'")
        result = cursor.fetchone()
        
        if result:
            username, stored_hash = result
            print(f"Usuario encontrado: {username}")
            print(f"Hash almacenado: {stored_hash[:50]}...")
            
            # Probar diferentes contraseñas
            test_passwords = ['admin', 'password', '123456', 'admin123']
            
            for test_password in test_passwords:
                try:
                    # Verificar si es un hash bcrypt
                    if stored_hash.startswith('$2b$'):
                        is_valid = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8'))
                        print(f"Probando '{test_password}' con bcrypt: {'✅ VÁLIDA' if is_valid else '❌ Inválida'}")
                        if is_valid:
                            break
                    else:
                        # Podría ser un hash simple o texto plano
                        is_valid = stored_hash == test_password
                        print(f"Probando '{test_password}' como texto plano: {'✅ VÁLIDA' if is_valid else '❌ Inválida'}")
                        if is_valid:
                            break
                except Exception as e:
                    print(f"Error probando '{test_password}': {e}")
            
        else:
            print("Usuario 'admin' no encontrado")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    verify_admin_password()