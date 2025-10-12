#!/usr/bin/env python3
"""
Test para verificar que los permisos de adhesiones funcionen correctamente
"""
import requests
import json

def test_login_and_permissions():
    """Test login y verificación de permisos"""
    print("=== TESTING ADHESION PERMISSIONS ===")
    
    base_url = "http://localhost:5000"
    
    # Test diferentes usuarios
    test_users = [
        {
            "username": "admin",
            "password": "admin123",
            "expected_role": "PRESIDENTE",
            "should_access": True
        },
        {
            "username": "coordinador",
            "password": "coord123",
            "expected_role": "COORDINADOR", 
            "should_access": True
        },
        {
            "username": "vocal",
            "password": "vocal123",
            "expected_role": "VOCAL",
            "should_access": True
        },
        {
            "username": "voluntario",
            "password": "vol123",
            "expected_role": "VOLUNTARIO",
            "should_access": True
        }
    ]
    
    for user_data in test_users:
        print(f"\n--- Testing user: {user_data['username']} ---")
        
        # Login
        login_response = requests.post(f"{base_url}/auth/login", json={
            "username": user_data["username"],
            "password": user_data["password"]
        })
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data.get("token")
            user_info = login_data.get("user", {})
            
            print(f"✅ Login successful")
            print(f"   Role: {user_info.get('role', 'Unknown')}")
            print(f"   Expected: {user_data['expected_role']}")
            
            # Verificar rol
            if user_info.get('role') == user_data['expected_role']:
                print(f"✅ Role matches expected")
            else:
                print(f"❌ Role mismatch!")
            
            # Test acceso a adhesiones
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test get volunteer adhesions
            adhesions_response = requests.post(
                f"{base_url}/messaging/volunteer-adhesions",
                headers=headers,
                json={}
            )
            
            if adhesions_response.status_code == 200:
                print(f"✅ Can access volunteer adhesions")
            else:
                print(f"❌ Cannot access volunteer adhesions: {adhesions_response.status_code}")
            
            # Test get event adhesions (solo para roles administrativos)
            if user_data['expected_role'] in ['PRESIDENTE', 'COORDINADOR', 'VOCAL']:
                event_adhesions_response = requests.post(
                    f"{base_url}/messaging/event-adhesions",
                    headers=headers,
                    json={"eventId": "test-event"}
                )
                
                if event_adhesions_response.status_code in [200, 400]:  # 400 es OK si no existe el evento
                    print(f"✅ Can access event adhesions management")
                else:
                    print(f"❌ Cannot access event adhesions: {event_adhesions_response.status_code}")
            else:
                print(f"ℹ️  Volunteer role - event management not expected")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            if login_response.status_code == 401:
                print(f"   Credentials may be incorrect")
            else:
                print(f"   Response: {login_response.text}")

def show_permission_matrix():
    """Mostrar matriz de permisos para adhesiones"""
    print("\n" + "="*60)
    print("📋 MATRIZ DE PERMISOS - GESTIÓN DE ADHESIONES")
    print("="*60)
    
    permissions = {
        "PRESIDENTE": {
            "Gestionar Adhesiones": "✅ SÍ",
            "Ver Mis Adhesiones": "✅ SÍ", 
            "Aprobar/Rechazar": "✅ SÍ",
            "Ver Estadísticas": "✅ SÍ"
        },
        "COORDINADOR": {
            "Gestionar Adhesiones": "✅ SÍ",
            "Ver Mis Adhesiones": "✅ SÍ",
            "Aprobar/Rechazar": "✅ SÍ", 
            "Ver Estadísticas": "✅ SÍ"
        },
        "VOCAL": {
            "Gestionar Adhesiones": "✅ SÍ",
            "Ver Mis Adhesiones": "✅ SÍ",
            "Aprobar/Rechazar": "✅ SÍ",
            "Ver Estadísticas": "✅ SÍ"
        },
        "VOLUNTARIO": {
            "Gestionar Adhesiones": "❌ NO",
            "Ver Mis Adhesiones": "✅ SÍ",
            "Aprobar/Rechazar": "❌ NO",
            "Ver Estadísticas": "❌ NO"
        }
    }
    
    # Header
    print(f"{'ROL':<12} {'GESTIONAR':<12} {'MIS ADHESIONES':<15} {'APROBAR':<10} {'ESTADÍSTICAS':<12}")
    print("-" * 60)
    
    for role, perms in permissions.items():
        print(f"{role:<12} {perms['Gestionar Adhesiones']:<12} {perms['Ver Mis Adhesiones']:<15} {perms['Aprobar/Rechazar']:<10} {perms['Ver Estadísticas']:<12}")
    
    print("\n📝 NOTAS:")
    print("• PRESIDENTE/COORDINADOR/VOCAL: Acceso completo a gestión")
    print("• VOLUNTARIO: Solo puede ver sus propias adhesiones")
    print("• Todos los roles pueden adherirse a eventos externos")
    print("• Las aprobaciones requieren permisos administrativos")

def main():
    """Función principal"""
    print("🔐 TESTING ADHESION PERMISSIONS")
    print("="*50)
    
    try:
        # Test permisos
        test_login_and_permissions()
        
        # Mostrar matriz
        show_permission_matrix()
        
        print("\n" + "="*50)
        print("✅ PERMISSION TESTING COMPLETED")
        print("="*50)
        
        print("\n🔧 TROUBLESHOOTING:")
        print("Si hay problemas de permisos:")
        print("1. Verificar que el usuario tenga el rol correcto en la BD")
        print("2. Verificar que el token JWT contenga el rol")
        print("3. Verificar que AuthContext.jsx use 'role' (no 'rol')")
        print("4. Verificar que AdhesionManagement.jsx use 'user?.role'")
        print("5. Verificar que App.js incluya todos los roles necesarios")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor")
        print("Asegúrate de que el API Gateway esté corriendo en http://localhost:5000")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()