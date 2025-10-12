#!/usr/bin/env python3
"""
Verificar a qué usuario se envió la notificación
"""
import requests

def verify_notification_user():
    """Verificar notificaciones de ambos usuarios admin"""
    print("🔍 VERIFICANDO NOTIFICACIONES DE AMBOS ADMINS")
    print("=" * 50)
    
    # Test con esperanza_admin (María González - ID 17)
    print("\\n👤 USUARIO: esperanza_admin (María González)")
    login_data = {"usernameOrEmail": "esperanza_admin", "password": "admin123"}
    response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        user_data = response.json().get('user')
        token = response.json().get('token')
        
        print(f"Login exitoso - ID: {user_data.get('id')}")
        
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get("http://localhost:3001/api/notifications", headers=headers)
        
        if response.status_code == 200:
            notifications = response.json().get('notifications', [])
            print(f"Notificaciones: {len(notifications)}")
            
            adhesion_notifs = [n for n in notifications if 'adhesion' in n.get('tipo', '')]
            print(f"Notificaciones de adhesión: {len(adhesion_notifs)}")
            
            for notif in adhesion_notifs[:3]:
                print(f"  - {notif.get('titulo')}")
        else:
            print(f"Error: {response.text}")
    else:
        print(f"Error login: {response.text}")
    
    # Test con esperanza_coord (Carlos Ruiz - ID 18)
    print("\\n👤 USUARIO: esperanza_coord (Carlos Ruiz)")
    login_data = {"usernameOrEmail": "esperanza_coord", "password": "admin123"}
    response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        user_data = response.json().get('user')
        token = response.json().get('token')
        
        print(f"Login exitoso - ID: {user_data.get('id')}")
        
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get("http://localhost:3001/api/notifications", headers=headers)
        
        if response.status_code == 200:
            notifications = response.json().get('notifications', [])
            print(f"Notificaciones: {len(notifications)}")
            
            adhesion_notifs = [n for n in notifications if 'adhesion' in n.get('tipo', '')]
            print(f"Notificaciones de adhesión: {len(adhesion_notifs)}")
            
            for notif in adhesion_notifs[:3]:
                print(f"  - {notif.get('titulo')}")
                print(f"    Fecha: {notif.get('fecha_creacion')}")
        else:
            print(f"Error: {response.text}")
    else:
        print(f"Error login: {response.text}")

if __name__ == "__main__":
    verify_notification_user()