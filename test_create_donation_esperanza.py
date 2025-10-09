#!/usr/bin/env python3
"""
Test directo de creación de donación con esperanza_admin
"""
import requests
import json

def test_create_donation():
    """Test directo de creación de donación"""
    
    print("🧪 PROBANDO CREACIÓN DE DONACIÓN CON ESPERANZA_ADMIN...")
    
    # 1. Login
    login_data = {
        "usernameOrEmail": "esperanza_admin",
        "password": "password123"
    }
    
    login_response = requests.post(
        "http://localhost:3001/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login falló: {login_response.status_code}")
        return
    
    token = login_response.json()["token"]
    user = login_response.json()["user"]
    print(f"✅ Login exitoso")
    print(f"   Usuario: {user['username']}")
    print(f"   Organización: {user['organization']}")
    
    # 2. Crear donación
    donation_data = {
        "category": "ALIMENTOS",
        "description": "TEST ESPERANZA DIRECT",
        "quantity": 99
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📦 CREANDO DONACIÓN...")
    print(f"   Data: {json.dumps(donation_data, indent=2)}")
    
    create_response = requests.post(
        "http://localhost:3001/api/inventory",
        json=donation_data,
        headers=headers
    )
    
    print(f"Status Code: {create_response.status_code}")
    print(f"Response: {create_response.text}")
    
    if create_response.status_code == 201:
        response_data = create_response.json()
        donation = response_data.get('donation', {})
        print(f"✅ Donación creada!")
        print(f"   ID: {donation.get('id')}")
        print(f"   Organización: {donation.get('organization')}")
        print(f"   Created by: {donation.get('createdBy')}")
        
        # Verificar en base de datos
        print(f"\n🔍 VERIFICANDO EN BASE DE DATOS...")
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))
        
        from database_mysql import get_db_connection
        
        db = get_db_connection()
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT d.id, d.organizacion, d.descripcion, d.usuario_alta,
                   u.nombre_usuario, u.organizacion as user_org
            FROM donaciones d
            LEFT JOIN usuarios u ON d.usuario_alta = u.id
            WHERE d.descripcion = %s
            ORDER BY d.id DESC
            LIMIT 1
        """, ("TEST ESPERANZA DIRECT",))
        
        result = cursor.fetchone()
        if result:
            print(f"   DB ID: {result['id']}")
            print(f"   DB Organización: {result['organizacion']}")
            print(f"   DB Usuario: {result['nombre_usuario']} (ID: {result['usuario_alta']})")
            print(f"   DB Usuario Org: {result['user_org']}")
            
            if result['organizacion'] == result['user_org']:
                print(f"   ✅ Organización correcta!")
            else:
                print(f"   ❌ PROBLEMA: {result['organizacion']} != {result['user_org']}")
        
        cursor.close()
        conn.close()
        
    else:
        print(f"❌ Error creando donación")

if __name__ == "__main__":
    test_create_donation()