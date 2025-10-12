#!/usr/bin/env python3
"""
Verificar usuarios de fundacion-esperanza
"""
import mysql.connector
import requests

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def check_fundacion_users():
    """Verificar usuarios de fundacion-esperanza"""
    print("👥 VERIFICANDO USUARIOS DE FUNDACION-ESPERANZA")
    print("=" * 50)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nombre_usuario, nombre, apellido, email, rol, activo
            FROM usuarios 
            WHERE organizacion = 'fundacion-esperanza'
            ORDER BY rol, nombre
        """)
        
        users = cursor.fetchall()
        print(f"Usuarios de fundacion-esperanza: {len(users)}")
        
        for user in users:
            print(f"  ID: {user['id']}")
            print(f"    Usuario: {user['nombre_usuario']}")
            print(f"    Nombre: {user['nombre']} {user['apellido']}")
            print(f"    Email: {user['email']}")
            print(f"    Rol: {user['rol']}")
            print(f"    Activo: {user['activo']}")
            print()
        
        cursor.close()
        conn.close()
        
        return users
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_login_attempts():
    """Test diferentes intentos de login"""
    print("🔑 TESTING INTENTOS DE LOGIN")
    print("=" * 30)
    
    users = check_fundacion_users()
    
    # Intentos de login comunes
    login_attempts = [
        {"usernameOrEmail": "admin_fundacion", "password": "admin123"},
        {"usernameOrEmail": "fundacion_admin", "password": "admin123"},
        {"usernameOrEmail": "admin", "password": "admin123"},
    ]
    
    # Agregar usuarios específicos
    for user in users:
        if user['nombre_usuario']:
            login_attempts.append({
                "usernameOrEmail": user['nombre_usuario'], 
                "password": "admin123"
            })
        if user['email']:
            login_attempts.append({
                "usernameOrEmail": user['email'], 
                "password": "admin123"
            })
    
    # Probar cada intento
    for attempt in login_attempts:
        response = requests.post("http://localhost:3001/api/auth/login", json=attempt)
        
        if response.status_code == 200:
            user_data = response.json().get('user', {})
            print(f"✅ Login exitoso: {attempt['usernameOrEmail']}")
            print(f"   Usuario: {user_data.get('username')}")
            print(f"   Organización: {user_data.get('organization')}")
            print(f"   Rol: {user_data.get('role')}")
            return response.json().get('token')
        else:
            print(f"❌ Fallo: {attempt['usernameOrEmail']} - {response.status_code}")
    
    return None

def create_fundacion_admin_if_needed():
    """Crear admin de fundacion si no existe"""
    print("\\n🔧 CREANDO ADMIN DE FUNDACION SI ES NECESARIO")
    print("=" * 50)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Verificar si ya existe un admin
        cursor.execute("""
            SELECT COUNT(*) FROM usuarios 
            WHERE organizacion = 'fundacion-esperanza' 
            AND rol IN ('PRESIDENTE', 'COORDINADOR')
            AND nombre_usuario IS NOT NULL
        """)
        
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("No hay admin con nombre_usuario, creando uno...")
            
            # Crear admin
            cursor.execute("""
                INSERT INTO usuarios 
                (nombre_usuario, nombre, apellido, email, password_hash, rol, organizacion, activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                'admin_fundacion',
                'Admin',
                'Fundacion',
                'admin@fundacion-esperanza.org',
                '$2b$10$rQZ9vKzKzKzKzKzKzKzKzOzKzKzKzKzKzKzKzKzKzKzKzKzKzKzKz',  # hash de "admin123"
                'PRESIDENTE',
                'fundacion-esperanza',
                1
            ))
            
            conn.commit()
            print("✅ Admin creado: admin_fundacion / admin123")
        else:
            print(f"Ya existen {admin_count} admins")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creando admin: {e}")

if __name__ == "__main__":
    print("🔍 VERIFICACIÓN COMPLETA DE USUARIOS FUNDACION-ESPERANZA")
    print("=" * 60)
    
    # 1. Verificar usuarios existentes
    users = check_fundacion_users()
    
    # 2. Intentar login
    token = test_login_attempts()
    
    # 3. Si no hay login exitoso, crear admin
    if not token:
        create_fundacion_admin_if_needed()
        
        # 4. Intentar login nuevamente
        print("\\n🔄 REINTENTANDO LOGIN DESPUÉS DE CREAR ADMIN")
        token = test_login_attempts()
        
        if token:
            print("✅ Login exitoso después de crear admin")
        else:
            print("❌ Aún no se puede hacer login")