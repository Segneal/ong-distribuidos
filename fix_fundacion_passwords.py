#!/usr/bin/env python3
"""
Arreglar contraseñas de usuarios de fundacion-esperanza
"""
import mysql.connector
import bcrypt
import requests

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def reset_fundacion_passwords():
    """Resetear contraseñas de fundacion-esperanza"""
    print("🔧 RESETEANDO CONTRASEÑAS DE FUNDACION-ESPERANZA")
    print("=" * 50)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Hash de "admin123"
        password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Actualizar contraseñas de usuarios admin
        users_to_update = ['esperanza_admin', 'esperanza_coord']
        
        for username in users_to_update:
            cursor.execute("""
                UPDATE usuarios 
                SET password_hash = %s
                WHERE nombre_usuario = %s AND organizacion = 'fundacion-esperanza'
            """, (password_hash, username))
            
            if cursor.rowcount > 0:
                print(f"✅ Contraseña actualizada para: {username}")
            else:
                print(f"❌ No se encontró usuario: {username}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\\n🔑 Contraseñas actualizadas a: admin123")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_login_after_reset():
    """Test login después del reset"""
    print("\\n🔑 TESTING LOGIN DESPUÉS DEL RESET")
    print("=" * 40)
    
    login_attempts = [
        {"usernameOrEmail": "esperanza_admin", "password": "admin123"},
        {"usernameOrEmail": "esperanza_coord", "password": "admin123"}
    ]
    
    for attempt in login_attempts:
        response = requests.post("http://localhost:3001/api/auth/login", json=attempt)
        
        print(f"Login {attempt['usernameOrEmail']}: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json().get('user', {})
            print(f"✅ Login exitoso!")
            print(f"   Usuario: {user_data.get('username')}")
            print(f"   Organización: {user_data.get('organization')}")
            print(f"   Rol: {user_data.get('role')}")
            return response.json().get('token'), user_data
        else:
            print(f"   Error: {response.text}")
    
    return None, None

def test_adhesion_approval_after_fix():
    """Test aprobación después del fix"""
    print("\\n✅ TESTING APROBACIÓN DESPUÉS DEL FIX")
    print("=" * 40)
    
    # Login con credenciales fijas
    token, user = test_login_after_reset()
    
    if not token:
        print("❌ Aún no se puede hacer login")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Obtener adhesiones para evento 27
    response = requests.post(
        "http://localhost:3001/api/messaging/event-adhesions",
        json={"eventId": 27},
        headers=headers
    )
    
    print(f"\\nEvent adhesions - Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        adhesions = data.get('adhesions', [])
        print(f"Adhesiones: {len(adhesions)}")
        
        pending = [a for a in adhesions if a.get('status') == 'PENDIENTE']
        print(f"Pendientes: {len(pending)}")
        
        for adhesion in pending:
            print(f"  - ID: {adhesion.get('id')}")
            print(f"    Voluntario: {adhesion.get('volunteer_name')} {adhesion.get('volunteer_surname')}")
        
        if pending:
            print("\\n🎉 ¡SISTEMA DE ADHESIONES FUNCIONANDO!")
            print("✅ Se pueden obtener adhesiones pendientes")
            print("⚠️  Falta implementar endpoint de aprobación")
        else:
            print("⚠️  No hay adhesiones pendientes")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    print("🔧 ARREGLO COMPLETO DEL SISTEMA DE ADHESIONES")
    print("=" * 60)
    
    # 1. Resetear contraseñas
    reset_fundacion_passwords()
    
    # 2. Test login
    test_adhesion_approval_after_fix()