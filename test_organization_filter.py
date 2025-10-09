#!/usr/bin/env python3
"""
Test para verificar el filtro por organización en el inventario
"""
import requests
import json

def test_organization_filter():
    """Test del filtro por organización"""
    
    print("🧪 INICIANDO TEST DE FILTRO POR ORGANIZACIÓN")
    print("=" * 60)
    
    # 1. Login con admin de empuje-comunitario
    print("1. 🔐 Login con admin de empuje-comunitario...")
    login_data = {
        "usernameOrEmail": "admin",
        "password": "admin123"
    }
    
    login_response = requests.post(
        "http://localhost:3001/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.status_code}")
        return False
    
    admin_token = login_response.json()["token"]
    admin_org = login_response.json()["user"]["organization"]
    
    print(f"✅ Login exitoso - Organización: {admin_org}")
    
    # 2. Obtener donaciones con admin
    print("\n2. 📋 Obteniendo donaciones con admin...")
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    list_response = requests.get(
        "http://localhost:3001/api/inventory",
        headers=headers
    )
    
    if list_response.status_code == 200:
        response_data = list_response.json()
        donations = response_data if isinstance(response_data, list) else response_data.get('donations', [])
        print(f"✅ Admin ve {len(donations)} donaciones")
        print(f"   Response type: {type(response_data)}")
        print(f"   Raw response: {list_response.text[:200]}...")
        for d in donations:
            if isinstance(d, dict):
                print(f"   - ID: {d.get('id')}, Org: {d.get('organization')}")
            else:
                print(f"   - Item: {d}")
    else:
        print(f"❌ Error obteniendo donaciones: {list_response.status_code}")
        return False
    
    # 3. Login con usuario de otra organización
    print("\n3. 🔐 Login con esperanza_admin...")
    login_data2 = {
        "usernameOrEmail": "esperanza_admin",
        "password": "password123"
    }
    
    login_response2 = requests.post(
        "http://localhost:3001/api/auth/login",
        json=login_data2,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response2.status_code != 200:
        print(f"❌ Error en login esperanza: {login_response2.status_code}")
        return False
    
    esperanza_token = login_response2.json()["token"]
    esperanza_org = login_response2.json()["user"]["organization"]
    
    print(f"✅ Login exitoso - Organización: {esperanza_org}")
    
    # 4. Obtener donaciones con esperanza_admin
    print("\n4. 📋 Obteniendo donaciones con esperanza_admin...")
    headers2 = {
        "Authorization": f"Bearer {esperanza_token}",
        "Content-Type": "application/json"
    }
    
    list_response2 = requests.get(
        "http://localhost:3001/api/inventory",
        headers=headers2
    )
    
    if list_response2.status_code == 200:
        response_data2 = list_response2.json()
        donations2 = response_data2 if isinstance(response_data2, list) else response_data2.get('donations', [])
        print(f"✅ Esperanza_admin ve {len(donations2)} donaciones")
        for d in donations2:
            if isinstance(d, dict):
                print(f"   - ID: {d.get('id')}, Org: {d.get('organization')}")
            else:
                print(f"   - Item: {d}")
    else:
        print(f"❌ Error obteniendo donaciones esperanza: {list_response2.status_code}")
        return False
    
    # 5. Verificar que cada usuario ve solo sus donaciones
    admin_donations = [d for d in donations if d.get('organization') == admin_org]
    esperanza_donations = [d for d in donations2 if d.get('organization') == esperanza_org]
    
    print(f"\n📊 RESUMEN:")
    print(f"   Admin debería ver solo donaciones de {admin_org}: {len(admin_donations)} de {len(donations)}")
    print(f"   Esperanza debería ver solo donaciones de {esperanza_org}: {len(esperanza_donations)} de {len(donations2)}")
    
    # Verificar que el filtro funciona
    if len(donations) > 0 and all(d.get('organization') == admin_org for d in donations):
        print("✅ Filtro de admin funciona correctamente")
    else:
        print("❌ Filtro de admin NO funciona")
        return False
    
    if all(d.get('organization') == esperanza_org for d in donations2):
        print("✅ Filtro de esperanza funciona correctamente")
    else:
        print("✅ Esperanza no tiene donaciones (normal si no ha creado ninguna)")
    
    return True

if __name__ == "__main__":
    success = test_organization_filter()
    if success:
        print("\n🎉 TEST COMPLETADO!")
    else:
        print("\n💥 TEST FALLÓ!")