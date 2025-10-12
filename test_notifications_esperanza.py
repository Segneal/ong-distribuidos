#!/usr/bin/env python3
"""
Test de notificaciones para esperanza
"""
import requests

def test_notifications():
    """Test de notificaciones"""
    # Login como esperanza
    login_data = {"usernameOrEmail": "admin_esperanza", "password": "admin123"}
    
    try:
        response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get('token')
            headers = {'Authorization': f'Bearer {token}'}
            
            # Test notificaciones
            response = requests.get(
                "http://localhost:3001/api/notifications",
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('notifications', [])
                print(f"✅ Notificaciones: {len(notifications)}")
                
                for i, notif in enumerate(notifications[:5]):
                    print(f"{i+1}. {notif.get('titulo')}")
                    print(f"   Fecha: {notif.get('fecha_creacion')}")
                    print(f"   Leída: {'Sí' if notif.get('leida') else 'No'}")
            else:
                print(f"Error: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🔔 TEST DE NOTIFICACIONES ESPERANZA")
    print("=" * 40)
    
    test_notifications()