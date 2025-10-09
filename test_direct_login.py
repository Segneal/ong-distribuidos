#!/usr/bin/env python3
"""
Script para probar login directo en la base de datos
"""
import mysql.connector
import hashlib

def test_direct_login():
    try:
        # Conectar a MySQL
        connection = mysql.connector.connect(
            host='localhost',
            database='ong_management',
            user='root',
            password='root',
            port=3306
        )
        
        cursor = connection.cursor()
        
        print("🔍 PROBANDO LOGIN DIRECTO EN BASE DE DATOS")
        print("=" * 50)
        
        # Función para hashear password
        def hash_password(password):
            return hashlib.sha256(password.encode()).hexdigest()
        
        # Usuarios de prueba
        test_users = [
            ("esperanza_admin", "password123"),
            ("solidaria_admin", "password123"),
            ("centro_admin", "password123"),
            ("admin", "admin123")
        ]
        
        for username, password in test_users:
            print(f"\n🧪 Probando: {username}")
            
            # Buscar usuario
            cursor.execute("""
                SELECT id, nombre_usuario, nombre, apellido, email, telefono, rol, organizacion, activo, password_hash
                FROM usuarios 
                WHERE (nombre_usuario = %s OR email = %s) AND activo = true
            """, (username, username))
            
            user = cursor.fetchone()
            
            if user:
                print(f"   ✅ Usuario encontrado:")
                print(f"      ID: {user[0]}")
                print(f"      Username: {user[1]}")
                print(f"      Nombre: {user[2]} {user[3]}")
                print(f"      Email: {user[4]}")
                print(f"      Rol: {user[6]}")
                print(f"      Organización: {user[7]}")
                print(f"      Activo: {user[8]}")
                
                # Verificar password
                stored_hash = user[9]
                input_hash = hash_password(password)
                
                if stored_hash == input_hash:
                    print(f"   ✅ Password correcto")
                else:
                    print(f"   ❌ Password incorrecto")
                    print(f"      Stored: {stored_hash[:20]}...")
                    print(f"      Input:  {input_hash[:20]}...")
            else:
                print(f"   ❌ Usuario no encontrado")
        
        cursor.close()
        connection.close()
        
        print(f"\n✅ Prueba de login directo completada")
        
    except mysql.connector.Error as err:
        print(f"❌ Error de MySQL: {err}")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_direct_login()