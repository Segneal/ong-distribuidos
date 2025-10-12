#!/usr/bin/env python3
"""
Test específico para la API de volunteer-adhesions
"""
import requests
import json

def test_volunteer_adhesions_api():
    """Test de la API volunteer-adhesions"""
    print("=== TESTING VOLUNTEER ADHESIONS API ===")
    
    base_url = "http://localhost:5000"
    
    # Test con usuario esperanza_admin (María - ID 17)
    print("\n1. Testing with esperanza_admin (María - ID 17)...")
    
    login_response = requests.post(f"{base_url}/auth/login", json={
        "username": "esperanza_admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json().get("token")
        user_info = login_response.json().get("user", {})
        
        print(f"✅ Login successful")
        print(f"   User ID: {user_info.get('id')}")
        print(f"   Username: {user_info.get('username')}")
        print(f"   Name: {user_info.get('firstName')} {user_info.get('lastName')}")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test volunteer adhesions
        adhesions_response = requests.post(
            f"{base_url}/messaging/volunteer-adhesions",
            headers=headers,
            json={}
        )
        
        if adhesions_response.status_code == 200:
            data = adhesions_response.json()
            adhesions = data.get("adhesions", [])
            
            print(f"✅ API call successful")
            print(f"   Found {len(adhesions)} adhesions")
            
            for i, adhesion in enumerate(adhesions, 1):
                print(f"\n   Adhesion {i}:")
                print(f"     ID: {adhesion.get('id')}")
                print(f"     Event: {adhesion.get('event_name')}")
                print(f"     Status: {adhesion.get('status')}")
                print(f"     Organization: {adhesion.get('organization_id')}")
                print(f"     Event Date: {adhesion.get('event_date')}")
                print(f"     Adhesion Date: {adhesion.get('adhesion_date')}")
                
                # Verificar si hay adhesiones confirmadas
                if adhesion.get('status') == 'CONFIRMADA':
                    print(f"     ✅ FOUND CONFIRMED ADHESION!")
                elif adhesion.get('status') == 'PENDIENTE':
                    print(f"     ⏳ Pending adhesion")
                else:
                    print(f"     ❓ Status: {adhesion.get('status')}")
        else:
            print(f"❌ API call failed: {adhesions_response.status_code}")
            print(f"   Response: {adhesions_response.text}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
    
    # Test con admin (Juan - ID 11)
    print("\n2. Testing with admin (Juan - ID 11)...")
    
    login_response = requests.post(f"{base_url}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json().get("token")
        user_info = login_response.json().get("user", {})
        
        print(f"✅ Login successful")
        print(f"   User ID: {user_info.get('id')}")
        print(f"   Username: {user_info.get('username')}")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test volunteer adhesions
        adhesions_response = requests.post(
            f"{base_url}/messaging/volunteer-adhesions",
            headers=headers,
            json={}
        )
        
        if adhesions_response.status_code == 200:
            data = adhesions_response.json()
            adhesions = data.get("adhesions", [])
            
            print(f"✅ API call successful")
            print(f"   Found {len(adhesions)} adhesions")
            
            for i, adhesion in enumerate(adhesions, 1):
                print(f"\n   Adhesion {i}:")
                print(f"     ID: {adhesion.get('id')}")
                print(f"     Event: {adhesion.get('event_name')}")
                print(f"     Status: {adhesion.get('status')}")
                print(f"     Organization: {adhesion.get('organization_id')}")
        else:
            print(f"❌ API call failed: {adhesions_response.status_code}")
    else:
        print(f"❌ Login failed: {login_response.status_code}")

def show_expected_results():
    """Mostrar los resultados esperados basados en la BD"""
    print("\n" + "="*60)
    print("📊 RESULTADOS ESPERADOS BASADOS EN LA BASE DE DATOS")
    print("="*60)
    
    print("\n🔍 ADHESIONES EN LA BASE DE DATOS:")
    print("   ID 25: Usuario 17 (María) - Estado CONFIRMADA ✅")
    print("   ID 29: Usuario 11 (Juan) - Estado PENDIENTE ⏳")
    print("   ID 26: Usuario 11 (Juan) - Estado PENDIENTE ⏳")
    
    print("\n📋 RESULTADOS ESPERADOS:")
    print("   esperanza_admin (María - ID 17):")
    print("     - Debería ver 1+ adhesiones")
    print("     - Al menos 1 debería estar CONFIRMADA")
    print("     - UI debería mostrar 'Aprobada' no 'Pendiente'")
    
    print("   admin (Juan - ID 11):")
    print("     - Debería ver 2+ adhesiones")
    print("     - Ambas deberían estar PENDIENTE")
    print("     - UI debería mostrar 'Pendiente de Aprobación'")
    
    print("\n🔧 SI LA API DEVUELVE DATOS CORRECTOS PERO LA UI NO:")
    print("   1. Verificar que el frontend esté refrescando los datos")
    print("   2. Verificar el mapeo de estados en VolunteerAdhesions.jsx")
    print("   3. Verificar la consola del navegador por errores")
    print("   4. Verificar que no haya caché en el navegador")

def main():
    """Función principal"""
    print("🔍 TESTING VOLUNTEER ADHESIONS API")
    print("="*50)
    
    try:
        test_volunteer_adhesions_api()
        show_expected_results()
        
        print("\n" + "="*50)
        print("✅ TEST COMPLETED")
        print("="*50)
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server")
        print("Make sure API Gateway is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()