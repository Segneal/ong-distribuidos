#!/usr/bin/env python3
"""
Test para verificar que las correcciones de la UI de adhesiones funcionen
"""
import requests
import json

def test_api_endpoints():
    """Test de los endpoints de la API"""
    print("=== TESTING API ENDPOINTS ===")
    
    base_url = "http://localhost:5000"
    
    # Login como admin
    print("1. Logging in as admin...")
    login_response = requests.post(f"{base_url}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful")
    
    # Test get events
    print("\n2. Testing get events...")
    events_response = requests.get(f"{base_url}/api/events", headers=headers)
    
    if events_response.status_code == 200:
        events_data = events_response.json()
        events = events_data.get("events", [])
        print(f"✅ Events loaded: {len(events)} events")
        
        if events:
            event = events[0]
            print(f"   Sample event: {event.get('name', 'No name')}")
            print(f"   Event date: {event.get('eventDate', event.get('date', 'No date'))}")
            
            # Test get event adhesions
            print(f"\n3. Testing event adhesions for event {event.get('id')}...")
            adhesions_response = requests.post(
                f"{base_url}/messaging/event-adhesions",
                headers=headers,
                json={"eventId": event.get('id')}
            )
            
            if adhesions_response.status_code == 200:
                adhesions_data = adhesions_response.json()
                adhesions = adhesions_data.get("adhesions", [])
                print(f"✅ Event adhesions loaded: {len(adhesions)} adhesions")
                
                if adhesions:
                    adhesion = adhesions[0]
                    print(f"   Sample adhesion:")
                    print(f"     Volunteer: {adhesion.get('volunteer_name', 'No name')} {adhesion.get('volunteer_surname', '')}")
                    print(f"     Status: {adhesion.get('status', 'No status')}")
                    print(f"     Date: {adhesion.get('adhesion_date', 'No date')}")
                    print(f"     External: {adhesion.get('external_volunteer', False)}")
                else:
                    print("   No adhesions found (this is normal if no test data)")
                    
            else:
                print(f"❌ Event adhesions failed: {adhesions_response.status_code}")
                print(f"   Response: {adhesions_response.text}")
                return False
        else:
            print("   No events found")
    else:
        print(f"❌ Events failed: {events_response.status_code}")
        return False
    
    # Test volunteer adhesions
    print("\n4. Testing volunteer adhesions...")
    volunteer_adhesions_response = requests.post(
        f"{base_url}/messaging/volunteer-adhesions",
        headers=headers,
        json={}
    )
    
    if volunteer_adhesions_response.status_code == 200:
        volunteer_data = volunteer_adhesions_response.json()
        volunteer_adhesions = volunteer_data.get("adhesions", [])
        print(f"✅ Volunteer adhesions loaded: {len(volunteer_adhesions)} adhesions")
    else:
        print(f"❌ Volunteer adhesions failed: {volunteer_adhesions_response.status_code}")
        return False
    
    return True

def show_ui_testing_instructions():
    """Mostrar instrucciones para probar la UI"""
    print("\n" + "="*60)
    print("🖥️  INSTRUCCIONES PARA PROBAR LA UI CORREGIDA")
    print("="*60)
    
    print("\n1. INICIAR EL FRONTEND:")
    print("   cd frontend")
    print("   npm start")
    print("   Abrir http://localhost:3000")
    
    print("\n2. INICIAR SESIÓN:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    
    print("\n3. NAVEGAR A GESTIÓN DE ADHESIONES:")
    print("   Menú lateral → 'Gestión Adhesiones'")
    
    print("\n4. VERIFICAR CORRECCIONES:")
    print("   ✅ No debería aparecer 'No tiene permisos'")
    print("   ✅ Las fechas deberían mostrarse correctamente (no 'Invalid Date')")
    print("   ✅ Los eventos deberían cargarse sin error 500")
    print("   ✅ Las adhesiones deberían mostrarse con información completa")
    
    print("\n5. FUNCIONALIDADES A PROBAR:")
    print("   🔸 Seleccionar un evento en la barra lateral")
    print("   🔸 Ver las estadísticas de adhesiones")
    print("   🔸 Ver la lista de adhesiones con información completa")
    print("   🔸 Cambiar a la pestaña 'Mis Adhesiones'")
    
    print("\n6. DATOS ESPERADOS:")
    print("   📊 Eventos con fechas formateadas correctamente")
    print("   📊 Adhesiones con nombres, emails y organizaciones")
    print("   📊 Estados de adhesiones (PENDIENTE, CONFIRMADA, etc.)")
    print("   📊 Badges para voluntarios externos vs internos")

def show_fixes_applied():
    """Mostrar las correcciones aplicadas"""
    print("\n" + "="*60)
    print("🔧 CORRECCIONES APLICADAS")
    print("="*60)
    
    print("\n1. CONSULTA SQL CORREGIDA:")
    print("   ❌ ANTES: u.name, u.lastName")
    print("   ✅ DESPUÉS: u.nombre, u.apellido")
    print("   + Agregado: u.telefono")
    
    print("\n2. MAPEO DE DATOS MEJORADO:")
    print("   ✅ Manejo de volunteer_data JSON")
    print("   ✅ Fallbacks para datos faltantes")
    print("   ✅ Detección de voluntarios externos")
    print("   ✅ Campos adicionales (teléfono, organización)")
    
    print("\n3. FORMATEO DE FECHAS ROBUSTO:")
    print("   ✅ Validación de fechas nulas")
    print("   ✅ Manejo de fechas inválidas")
    print("   ✅ Compatibilidad con eventDate y date")
    print("   ✅ Mensajes de error descriptivos")
    
    print("\n4. PERMISOS CORREGIDOS:")
    print("   ✅ user?.role en lugar de user?.rol")
    print("   ✅ Rol VOCAL agregado a permisos")
    print("   ✅ Rutas protegidas actualizadas")

def main():
    """Función principal"""
    print("🔧 TESTING ADHESION UI FIXES")
    print("="*50)
    
    try:
        # Test API endpoints
        api_success = test_api_endpoints()
        
        # Mostrar correcciones
        show_fixes_applied()
        
        # Mostrar instrucciones
        show_ui_testing_instructions()
        
        if api_success:
            print("\n✅ API TESTS PASSED - UI should work correctly now!")
        else:
            print("\n❌ Some API tests failed - check server logs")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server")
        print("Make sure API Gateway is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()