#!/usr/bin/env python3
"""
Script para probar el filtrado correcto de eventos por organización
"""
import requests
import json

def test_event_filtering():
    """Probar que los eventos se filtran correctamente por organización"""
    
    API_BASE = "http://localhost:3001/api"
    
    print("🔍 TESTING FILTRADO DE EVENTOS POR ORGANIZACIÓN")
    print("=" * 60)
    
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
                
                # Verificar que la organización es la esperada
                if user_info.get('organization') != org['expected_org']:
                    print(f"⚠️  Organización inesperada: esperaba {org['expected_org']}, obtuvo {user_info.get('organization')}")
                
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
        
        # 2. Obtener eventos propios
        print(f"\n📅 EVENTOS PROPIOS:")
        try:
            events_response = requests.get(f"{API_BASE}/events", headers=headers)
            
            if events_response.status_code == 200:
                events_result = events_response.json()
                events = events_result.get('events', [])
                
                print(f"  📊 Total eventos propios: {len(events)}")
                for event in events:
                    print(f"    📝 ID {event.get('id')}: {event.get('name')} - {event.get('organization')}")
                    
                    # Verificar que todos los eventos son de la organización correcta
                    if event.get('organization') != org['expected_org']:
                        print(f"    ⚠️  PROBLEMA: Evento de organización incorrecta!")
                
            else:
                print(f"  ❌ Error obteniendo eventos: {events_response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error obteniendo eventos: {e}")
        
        # 3. Verificar eventos en la base de datos
        print(f"\n🗄️  VERIFICACIÓN EN BASE DE DATOS:")
        try:
            # Llamar directamente a la base de datos para verificar
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), 'user-service', 'src'))
            
            from database_mysql import get_db_connection
            
            db = get_db_connection()
            conn = db.connect()
            cursor = conn.cursor(dictionary=True)
            
            # Contar eventos por organización
            cursor.execute("""
                SELECT organizacion, COUNT(*) as total
                FROM eventos 
                GROUP BY organizacion
                ORDER BY organizacion
            """)
            
            org_counts = cursor.fetchall()
            
            print(f"  📊 EVENTOS POR ORGANIZACIÓN EN BD:")
            for count in org_counts:
                print(f"    🏢 {count['organizacion']}: {count['total']} eventos")
            
            # Obtener eventos específicos de esta organización
            cursor.execute("""
                SELECT id, nombre, organizacion, fecha_evento
                FROM eventos 
                WHERE organizacion = %s
                ORDER BY fecha_evento DESC
            """, (org['expected_org'],))
            
            org_events = cursor.fetchall()
            
            print(f"  📋 EVENTOS DE {org['expected_org'].upper()}:")
            for event in org_events:
                print(f"    📝 ID {event['id']}: {event['nombre']} ({event['fecha_evento']})")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"  ❌ Error verificando BD: {e}")
    
    print(f"\n🎉 TESTING DE FILTRADO COMPLETADO")

if __name__ == "__main__":
    test_event_filtering()