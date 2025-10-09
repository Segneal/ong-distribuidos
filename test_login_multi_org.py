#!/usr/bin/env python3
"""
Script para probar login de usuarios multi-organización
"""
import requests
import json

# Configuración
API_BASE = "http://localhost:3000/api"
LOGIN_URL = f"{API_BASE}/auth/login"

def test_login(username, password, expected_org):
    """Probar login de usuario"""
    login_data = {
        "usernameOrEmail": username,
        "password": password
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            
            print(f"✅ {username}:")
            print(f"   Nombre: {user.get('firstName')} {user.get('lastName')}")
            print(f"   Organización: {user.get('organization')}")
            print(f"   Rol: {user.get('role')}")
            print(f"   Email: {user.get('email')}")
            
            # Verificar organización
            if user.get('organization') == expected_org:
                print(f"   ✓ Organización correcta: {expected_org}")
            else:
                print(f"   ❌ Organización incorrecta. Esperado: {expected_org}, Obtenido: {user.get('organization')}")
            
            return True, data.get('token'), user
        else:
            print(f"❌ {username}: Error {response.status_code} - {response.text}")
            return False, None, None
    except Exception as e:
        print(f"❌ {username}: Error de conexión - {e}")
        return False, None, None

def main():
    print("🧪 PROBANDO LOGIN MULTI-ORGANIZACIÓN")
    print("=" * 50)
    
    # Usuarios de prueba
    test_users = [
        ("esperanza_admin", "password123", "fundacion-esperanza"),
        ("esperanza_coord", "password123", "fundacion-esperanza"),
        ("solidaria_admin", "password123", "ong-solidaria"),
        ("solidaria_vol", "password123", "ong-solidaria"),
        ("centro_admin", "password123", "centro-comunitario"),
        ("centro_vocal", "password123", "centro-comunitario"),
        ("admin", "admin123", "empuje-comunitario")  # Usuario original
    ]
    
    successful_logins = 0
    
    for username, password, expected_org in test_users:
        success, token, user = test_login(username, password, expected_org)
        if success:
            successful_logins += 1
        print()
    
    print("=" * 50)
    print(f"✅ {successful_logins}/{len(test_users)} usuarios logueados exitosamente")
    
    if successful_logins == len(test_users):
        print("🎉 ¡Todos los usuarios funcionan correctamente!")
        print("\n🔧 Próximos pasos:")
        print("   1. Probar en el frontend que el header cambia")
        print("   2. Probar flujos de Kafka entre organizaciones")
        print("   3. Verificar creación de solicitudes/ofertas")
    else:
        print("⚠ Algunos usuarios tienen problemas")

if __name__ == "__main__":
    main()