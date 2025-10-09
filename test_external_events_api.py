#!/usr/bin/env python3
"""
Script para probar la API de eventos externos
"""
import requests
import json

def test_external_events_api():
    """Probar la API de eventos externos"""
    
    API_BASE = "http://localhost:3001/api"
    
    print("🌐 TESTING API DE EVENTOS EXTERNOS")
    print("=" * 50)
    
    # Organizaciones a probar
    organizaciones = [
        {
            "name": "Empuje Comunitario",
            "username": "admin",
            "password": "admin123",
            "expected_org": "empuje-comunitario"
        },
        {
            "name": "Fundación Esperanza", 
            "username": "esperanza_admin",
            "password": "password123",
            "expected_org": "fundacion-esperanza"
        }
    ]
    
    for org in organizaciones:
        print(f"\n🏢 TESTING ORGANIZACIÓN: {org['name']}")
        print("-" * 40)
        
        # 1. Login
        login_data = {
            "usernameOrEmail": org["username"],
            "password": org["password"]
        }
        
        try:
            login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                token = login_result.get('token')
                user_info = login_result.get('user', {})
                
                print(f"✅ Login exitoso")
                print(f"  👤 Usuario: {user_info.get('username')}")
                print(f"  🏢 Organización: {user_info.get('organization')}")
                
            else:
                print(f"❌ Error en login: {login_response.status_code}")
                continue
                
        except Exception as e:
            print(f"❌ Error en login: {e}")
            continue
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 2. Obtener eventos externos
        print(f"\n🌐 EVENTOS EXTERNOS:")
        try:
            external_events_response = requests.post(f"{API_BASE}/messaging/external-events", 
                                                   json={}, headers=headers)
            
            if external_events_response.status_code == 200:
                external_events_result = external_events_response.json()
                events = external_events_result.get('events', [])
                
                print(f"  📊 Total eventos externos: {len(events)}")
                
                for event in events:
                    is_own = event.get('source_organization') == org['expected_org']
                    status = "PROPIO" if is_own else "EXTERNO"
                    
                    print(f"    📝 ID {event.get('event_id')}: {event.get('name')} ({status})")
                    print(f"        🏢 Organización: {event.get('source_organization')}")
                    print(f"        📅 Fecha: {event.get('event_date')}")
                    print(f"        📅 Publicado: {event.get('published_date')}")
                    print()
                
            else:
                print(f"  ❌ Error obteniendo eventos externos: {external_events_response.status_code}")
                print(f"     Respuesta: {external_events_response.text}")
                
        except Exception as e:
            print(f"  ❌ Error obteniendo eventos externos: {e}")
    
    print(f"\n🎉 TESTING DE API COMPLETADO")

if __name__ == "__main__":
    test_external_events_api()