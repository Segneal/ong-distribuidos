#!/usr/bin/env python3
"""
Verificar resultado de automatización
"""
import requests

def verify_result():
    """Verificar resultado"""
    print("🔍 VERIFICANDO RESULTADO DE AUTOMATIZACIÓN")
    print("=" * 50)
    
    # Login esperanza-social
    login_data = {"usernameOrEmail": "admin_esperanza", "password": "admin123"}
    response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Error login: {response.text}")
        return
    
    token = response.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Verificar transferencias
    print("\n📥 VERIFICANDO TRANSFERENCIAS RECIBIDAS...")
    response = requests.get(
        "http://localhost:3001/api/messaging/transfer-history?limit=3",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        transfers = data.get('transfers', [])
        print(f"Transferencias: {len(transfers)}")
        
        if transfers:
            latest = transfers[0]
            print(f"Última transferencia:")
            print(f"  - ID: {latest.get('id')}")
            print(f"  - Tipo: {latest.get('tipo')}")
            print(f"  - De: {latest.get('source_organization')}")
            print(f"  - Request ID: {latest.get('request_id')}")
            print(f"  - Notas: {latest.get('notas')}")
            
            if 'automático' in latest.get('notas', ''):
                print("✅ ¡TRANSFERENCIA PROCESADA AUTOMÁTICAMENTE!")
            else:
                print("⚠️  Transferencia no automática")
    
    # Verificar notificaciones
    print("\n🔔 VERIFICANDO NOTIFICACIONES...")
    response = requests.get("http://localhost:3001/api/notifications", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        notifications = data.get('notifications', [])
        
        recent_notifications = [n for n in notifications if not n.get('leida')]
        print(f"Notificaciones no leídas: {len(recent_notifications)}")
        
        if recent_notifications:
            latest_notif = recent_notifications[0]
            print(f"Última notificación:")
            print(f"  - Título: {latest_notif.get('titulo')}")
            print(f"  - Tipo: {latest_notif.get('tipo')}")
            
            if latest_notif.get('tipo') == 'transferencia_recibida':
                print("✅ ¡NOTIFICACIÓN AUTOMÁTICA CREADA!")

if __name__ == "__main__":
    verify_result()