#!/usr/bin/env python3
"""
Test del sistema automatizado de transferencias
"""
import requests
import time

def get_token(org='empuje-comunitario'):
    """Obtener token"""
    if org == 'empuje-comunitario':
        login_data = {"usernameOrEmail": "admin", "password": "admin123"}
    else:
        login_data = {"usernameOrEmail": "admin_esperanza", "password": "admin123"}
    
    response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json().get('token')
    return None

def test_automated_transfer():
    """Test del sistema automatizado"""
    print("🚀 TESTING SISTEMA AUTOMATIZADO DE TRANSFERENCIAS")
    print("=" * 60)
    
    # 1. Login como empuje-comunitario
    token_empuje = get_token('empuje-comunitario')
    if not token_empuje:
        print("❌ Error obteniendo token de empuje-comunitario")
        return
    
    # 2. Hacer transferencia
    print("\n📤 ENVIANDO TRANSFERENCIA...")
    transfer_data = {
        "targetOrganization": "esperanza-social",
        "requestId": f"auto-test-{int(time.time())}",
        "donations": [
            {
                "category": "ALIMENTOS",
                "quantity": "2",
                "description": "Test automatizado",
                "inventoryId": 12,
                "inventory_id": 12,
                "parsed_quantity": 2
            }
        ],
        "notes": "Transferencia de test automatizado"
    }
    
    headers = {'Authorization': f'Bearer {token_empuje}'} 
    response = requests.post(
        "http://localhost:3001/api/messaging/transfer-donations",
        json=transfer_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        print("❌ Error en transferencia")
        return
    
    print("✅ Transferencia enviada exitosamente")
    
    # 3. Esperar un momento para el procesamiento automático
    print("\n⏳ Esperando procesamiento automático...")
    time.sleep(2)
    
    # 4. Verificar desde esperanza-social
    print("\n📥 VERIFICANDO RECEPCIÓN EN ESPERANZA-SOCIAL...")
    token_esperanza = get_token('esperanza-social')
    if not token_esperanza:
        print("❌ Error obteniendo token de esperanza-social")
        return
    
    headers = {'Authorization': f'Bearer {token_esperanza}'}
    response = requests.get(
        "http://localhost:3001/api/messaging/transfer-history?limit=3",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        transfers = data.get('transfers', [])
        print(f"Transferencias encontradas: {len(transfers)}")
        
        if transfers:
            latest = transfers[0]
            print(f"Última transferencia:")
            print(f"  - ID: {latest.get('id')}")
            print(f"  - Tipo: {latest.get('tipo')}")
            print(f"  - De: {latest.get('source_organization')}")
            print(f"  - Estado: {latest.get('estado')}")
            
            if latest.get('tipo') == 'RECIBIDA':
                print("✅ ¡TRANSFERENCIA RECIBIDA AUTOMÁTICAMENTE!")
            else:
                print("⚠️  Transferencia no procesada automáticamente")
        else:
            print("❌ No se encontraron transferencias")
    else:
        print(f"❌ Error verificando transferencias: {response.text}")
    
    # 5. Verificar notificaciones
    print("\n🔔 VERIFICANDO NOTIFICACIONES...")
    response = requests.get(
        "http://localhost:3001/api/notifications",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        notifications = data.get('notifications', [])
        print(f"Notificaciones: {len(notifications)}")
        
        recent_transfer_notifications = [
            n for n in notifications 
            if n.get('tipo') == 'transferencia_recibida' and not n.get('leida')
        ]
        
        if recent_transfer_notifications:
            print("✅ ¡NOTIFICACIÓN DE TRANSFERENCIA CREADA!")
            latest_notif = recent_transfer_notifications[0]
            print(f"  - Título: {latest_notif.get('titulo')}")
            print(f"  - Tipo: {latest_notif.get('tipo')}")
        else:
            print("⚠️  No se encontraron notificaciones de transferencia")
    else:
        print(f"❌ Error verificando notificaciones: {response.text}")

if __name__ == "__main__":
    test_automated_transfer()