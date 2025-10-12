#!/usr/bin/env python3
"""
Verificar el hash de contraseña del usuario admin_esperanza
"""
import mysql.connector
import bcrypt

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def check_password():
    """Verificar contraseña del usuario admin_esperanza"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nombre_usuario, email, password_hash 
            FROM usuarios 
            WHERE nombre_usuario = 'admin_esperanza'
        """)
        
        user = cursor.fetchone()
        
        if user:
            print(f"Usuario encontrado: {user['nombre_usuario']}")
            print(f"Email: {user['email']}")
            print(f"Hash actual: {user['password_hash']}")
            
            # Probar diferentes contraseñas
            passwords_to_test = ['password123', 'admin123', 'admin', '123456']
            
            for pwd in passwords_to_test:
                try:
                    if bcrypt.checkpw(pwd.encode('utf-8'), user['password_hash'].encode('utf-8')):
                        print(f"✅ Contraseña correcta: {pwd}")
                        return pwd
                    else:
                        print(f"❌ Contraseña incorrecta: {pwd}")
                except Exception as e:
                    print(f"⚠️  Error verificando {pwd}: {e}")
            
            # Generar nuevo hash para password123
            print("\n=== ACTUALIZANDO CONTRASEÑA ===")
            new_password = 'password123'
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                UPDATE usuarios 
                SET password_hash = %s 
                WHERE nombre_usuario = 'admin_esperanza'
            """, (new_hash,))
            
            conn.commit()
            print(f"✅ Contraseña actualizada para admin_esperanza: {new_password}")
            
        else:
            print("❌ Usuario admin_esperanza no encontrado")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_password()