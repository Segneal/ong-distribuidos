#!/usr/bin/env python3
"""
Script para probar el sistema multi-organización completo
"""

import requests
import json

def test_organization_data(org_credentials, expected_org):
    """Probar datos de una organización específica"""
    
    # URLs
    login_url = "http://localhost:3001/api/auth/login"
    users_url = "http://localhost:3001/api/users"
    inventory_url = "http://localhost:3001/api/inventory"
    events_url = "http://localhost:3001/api/events"
    
    print(f"\n🏢 PROBANDO ORGANIZACIÓN: {expected_org}")
    print("=" * 60)
    
    try:
        # 1. Login
        print("1️⃣ Haciendo login...")
        login_response = requests.post(login_url, json=org_credentials)
        
        if login_response.status_code != 200:
            print(f"❌ Login falló: {login_response.text}")
            return False
            
        login_data = login_response.json()
        token = login_data['token']
        user_org = login_data['user']['organization']
        
        print(f"✅ Login exitoso - Usuario: {login_data['user']['username']}")
        print(f"📍 Organización: {user_org}")
        
        if user_org != expected_org:
            print(f"❌ Organización incorrecta. Esperada: {expected_org}, Obtenida: {user_org}")
            return False
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 2. Probar usuarios
        print("\n2️⃣ Probando usuarios...")
        users_response = requests.get(users_url, headers=headers)
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            users_count = len(users_data.get('users', []))
            print(f"✅ Usuarios obtenidos: {users_count}")
            
            # Verificar que todos los usuarios sean de la misma organización
            for user in users_data.get('users', []):
                if user.get('organization') != expected_org:
                    print(f"❌ Usuario {user['username']} tiene organización incorrecta: {user.get('organization')}")
                    return False
        else:
            print(f"❌ Error obteniendo usuarios: {users_response.status_code}")
            return False
        
        # 3. Probar inventario
        print("\n3️⃣ Probando inventario...")
        inventory_response = requests.get(inventory_url, headers=headers)
        
        if inventory_response.status_code == 200:
            inventory_data = inventory_response.json()
            donations_count = len(inventory_data.get('donations', []))
            print(f"✅ Donaciones obtenidas: {donations_count}")
            
            # Verificar que todas las donaciones sean de la misma organización
            for donation in inventory_data.get('donations', []):
                if donation.get('organization') != expected_org:
                    print(f"❌ Donación {donation['id']} tiene organización incorrecta: {donation.get('organization')}")
                    return False
        else:
            print(f"❌ Error obteniendo inventario: {inventory_response.status_code}")
            return False
        
        # 4. Probar eventos
        print("\n4️⃣ Probando eventos...")
        events_response = requests.get(events_url, headers=headers)
        
        if events_response.status_code == 200:
            events_data = events_response.json()
            events_count = len(events_data.get('events', []))
            print(f"✅ Eventos obtenidos: {events_count}")
            
            # Verificar que todos los eventos sean de la misma organización
            for event in events_data.get('events', []):
                if event.get('organization') != expected_org:
                    print(f"❌ Evento {event['id']} tiene organización incorrecta: {event.get('organization')}")
                    return False
        else:
            print(f"❌ Error obteniendo eventos: {events_response.status_code}")
            return False
        
        print(f"\n🎉 ¡Organización {expected_org} funciona correctamente!")
        print(f"   👥 Usuarios: {users_count}")
        print(f"   📦 Donaciones: {donations_count}")
        print(f"   📅 Eventos: {events_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 PRUEBA COMPLETA SISTEMA MULTI-ORGANIZACIÓN")
    print("=" * 70)
    
    # Credenciales de las organizaciones
    organizations = [
        {
            "credentials": {"usernameOrEmail": "admin", "password": "admin"},
            "expected_org": "empuje-comunitario"
        },
        {
            "credentials": {"usernameOrEmail": "esperanza_admin", "password": "admin"},
            "expected_org": "fundacion-esperanza"
        },
        {
            "credentials": {"usernameOrEmail": "solidaria_admin", "password": "admin"},
            "expected_org": "ong-solidaria"
        },
        {
            "credentials": {"usernameOrEmail": "centro_admin", "password": "admin"},
            "expected_org": "centro-comunitario"
        }
    ]
    
    results = []
    
    for org in organizations:
        success = test_organization_data(org["credentials"], org["expected_org"])
        results.append({
            "org": org["expected_org"],
            "success": success
        })
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL")
    print("=" * 70)
    
    successful = 0
    for result in results:
        status = "✅ EXITOSO" if result["success"] else "❌ FALLÓ"
        print(f"   {result['org']}: {status}")
        if result["success"]:
            successful += 1
    
    print(f"\n🎯 Organizaciones exitosas: {successful}/{len(results)}")
    
    if successful == len(results):
        print("🎉 ¡SISTEMA MULTI-ORGANIZACIÓN COMPLETAMENTE FUNCIONAL!")
    else:
        print("⚠️  Algunas organizaciones tienen problemas")

if __name__ == "__main__":
    main()