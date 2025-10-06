#!/usr/bin/env python3
"""
Script para probar el login de un usuario de Fundación Esperanza y verificar eventos
"""
import requests
import json

def test_esperanza_login_events():
    """Probar login de usuario de Esperanza y obtener eventos"""
    
    API_BASE = "http://localhost:3001/api"
    
    print("🔐 TESTING LOGIN Y EVENTOS DE FUNDACIÓN ESPERANZA")
    print("=" * 55)
    
    # 1. Login con usuario de Fundación Esperanza
    print("👤 PASO 1: LOGIN CON USUARIO DE ESPERANZA")
    
    login_data = {
        "usernameOrEmail": "esperanza_admin",
        "password": "password123"
    }
    
    try:
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('token')
            user_info = login_result.get('user', {})
            
            print(f"✅ Login exitoso")
            print(f"  👤 Usuario: {user_info.get('name')} ({user_info.get('email')})")
            print(f"  🏢 Organización: {user_info.get('organization')}")
            print(f"  🎭 Rol: {user_info.get('role')}")
            print(f"  🔑 Token: {token[:20]}...")
            
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"   Respuesta: {login_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error conectando al API: {e}")
        return
    
    # 2. Obtener eventos con el token
    print(f"\n📅 PASO 2: OBTENER EVENTOS CON TOKEN DE ESPERANZA")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        events_response = requests.get(f"{API_BASE}/events", headers=headers)
        
        if events_response.status_code == 200:
            events_result = events_response.json()
            events = events_result.get('events', [])
            
            print(f"✅ Eventos obtenidos exitosamente")
            print(f"  📊 Total eventos: {len(events)}")
            
            if len(events) > 0:
                print(f"\n📋 EVENTOS DE FUNDACIÓN ESPERANZA:")
                for event in events:
                    print(f"  📅 ID {event.get('id')}: {event.get('name')}")
                    print(f"      📅 Fecha: {event.get('eventDate')}")
                    print(f"      🏢 Organización: {event.get('organization')}")
                    print(f"      📝 Descripción: {event.get('description', 'N/A')}")
                    print()
            else:
                print(f"⚠️  No se encontraron eventos para Fundación Esperanza")
                
        else:
            print(f"❌ Error obteniendo eventos: {events_response.status_code}")
            print(f"   Respuesta: {events_response.text}")
            
    except Exception as e:
        print(f"❌ Error obteniendo eventos: {e}")
    
    # 3. Verificar eventos en la red (externos)
    print(f"\n🌐 PASO 3: OBTENER EVENTOS EXTERNOS (RED)")
    
    try:
        external_events_response = requests.get(f"{API_BASE}/messaging/externalEvents", headers=headers)
        
        if external_events_response.status_code == 200:
            external_events_result = external_events_response.json()
            external_events = external_events_result.get('events', [])
            
            print(f"✅ Eventos externos obtenidos exitosamente")
            print(f"  📊 Total eventos externos: {len(external_events)}")
            
            if len(external_events) > 0:
                print(f"\n📋 EVENTOS EXTERNOS DISPONIBLES:")
                for event in external_events:
                    print(f"  🌐 ID {event.get('id')}: {event.get('name')}")
                    print(f"      📅 Fecha: {event.get('eventDate')}")
                    print(f"      🏢 Organización: {event.get('organization')}")
                    print()
            else:
                print(f"⚠️  No se encontraron eventos externos")
                
        else:
            print(f"❌ Error obteniendo eventos externos: {external_events_response.status_code}")
            print(f"   Respuesta: {external_events_response.text}")
            
    except Exception as e:
        print(f"❌ Error obteniendo eventos externos: {e}")
    
    print(f"\n🎉 TESTING COMPLETADO")

if __name__ == "__main__":
    test_esperanza_login_events()