#!/usr/bin/env python3
"""
Script para probar la creación de usuarios en diferentes organizaciones
"""
import requests
import json

# Configuración
API_BASE = "http://localhost:3000/api"
LOGIN_URL = f"{API_BASE}/auth/login"
USERS_URL = f"{API_BASE}/users"

def login_as_admin():
    """Login como admin para obtener token"""
    login_data = {
        "usernameOrEmail": "admin",
        "password": "admin123"
    }
    
    response = requests.post(LOGIN_URL, json=login_data)
    if response.status_code == 200:
        data = response.json()
        return data.get('token')
    else:
        print(f"❌ Error en login: {response.text}")
        return None

def create_test_user(token, user_data):
    """Crear usuario de prueba"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(USERS_URL, json=user_data, headers=headers)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Usuario {user_data['username']} creado en {user_data['organization']}")
        return data
    else:
        print(f"❌ Error creando {user_data['username']}: {response.text}")
        return None

def main():
    print("🧪 PROBANDO CREACIÓN DE USUARIOS MULTI-ORGANIZACIÓN")
    print("=" * 60)
    
    # Login como admin
    token = login_as_admin()
    if not token:
        print("❌ No se pudo obtener token de autenticación")
        return
    
    print("✅ Login exitoso, token obtenido")
    
    # Usuarios de prueba para diferentes organizaciones
    test_users = [
        {
            "username": "esperanza_test",
            "firstName": "Test",
            "lastName": "Esperanza",
            "email": "test@esperanza.org",
            "phone": "+54-11-9999-0001",
            "role": "COORDINADOR",
            "organization": "fundacion-esperanza"
        },
        {
            "username": "solidaria_test",
            "firstName": "Test",
            "lastName": "Solidaria", 
            "email": "test@solidaria.org",
            "phone": "+54-11-9999-0002",
            "role": "VOCAL",
            "organization": "ong-solidaria"
        },
        {
            "username": "centro_test",
            "firstName": "Test",
            "lastName": "Centro",
            "email": "test@centro.org", 
            "phone": "+54-11-9999-0003",
            "role": "VOLUNTARIO",
            "organization": "centro-comunitario"
        },
        {
            "username": "empuje_test",
            "firstName": "Test",
            "lastName": "Empuje",
            "email": "test@empuje.org",
            "phone": "+54-11-9999-0004", 
            "role": "COORDINADOR",
            "organization": "empuje-comunitario"
        }
    ]
    
    print("\\n🔧 Creando usuarios de prueba...")
    
    created_users = []
    for user_data in test_users:
        result = create_test_user(token, user_data)
        if result:
            created_users.append(result)
    
    print(f"\\n✅ {len(created_users)} usuarios creados exitosamente")
    
    # Mostrar resumen
    print("\\n📋 RESUMEN DE USUARIOS CREADOS:")
    for user in created_users:
        user_info = user.get('user', {})
        print(f"  • {user_info.get('username')} | {user_info.get('organization')} | {user_info.get('role')}")
    
    print("\\n🎯 PRÓXIMOS PASOS:")
    print("  1. Probar login con estos usuarios")
    print("  2. Verificar que el header muestre la organización correcta")
    print("  3. Probar flujos de Kafka entre organizaciones")
    print("\\n🔑 Password para todos los usuarios de prueba: Se envió por email")

if __name__ == "__main__":
    main()