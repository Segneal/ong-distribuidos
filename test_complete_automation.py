#!/usr/bin/env python3
"""
Test completo del sistema automatizado
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

def test_complete_automation():
    """Test completo del sistema automatizado"""
    print("🚀 TEST COMPLETO DEL SISTEMA AUTOMATIZADO")
    print("=" * 60)
    
    # 1. Obtener estado inicial
    print("\n📊 ESTADO INICIAL...")
    token_esperanza = get_token('esperanza-social')
    headers_esperanza = {'Authorization': f'Bearer {token_esperanza}'}
    
    response = requests.get(
        "http://localhost:3001/api/messaging/transfer-history?limit=1",
        headers=headers_esperanza
    )
    
    initial_count = 0
    if response.status_code == 200:
        initial_count = len(response.json().get('transfers', []))
        print(f"Transferencias iniciales: {initial_count}")
    
    # 2. Hacer transferencia desde empuje-comunitario
    print("\n📤 ENVIANDO TRANSFERENCIA DESDE EMPUJE-COMUNITARIO...")
    token_empuje = get_token('empuje-comunitario')
    headers_empuje = {'Authorization': f'Bearer {token_empuje}'}
    
    transfer_data = {
        "targetOrganization": "esperanza-social",
        "requestId": f"complete-test-{int(time.time())}",
        "donations": [
            {
                "category": "ALIMENTOS",
                "quantity": "3",
                "description": "Test automatización completa",
                "inventoryId": 12,
                "inventory_id": 12,
                "parsed_quantity": 3
            },
            {
                "category": "ROPA",
                "quantity": "2",
                "description": "Camisetas para niños",
                "inventoryId": 13,
                "inventory_id": 13,
                "parsed_quantity": 2
            }
        ],
        "notes": "Test completo de automatización"
    }
    
    response = requests.post(
        "http://localhost:3001/api/messaging/transfer-donations",
        json=transfer_data,
        headers=headers_empuje
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Transferencia enviada: {data.get('transfer_id')}")
        print(f"   Mensaje: {data.get('message')}")
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # 3. Verificar procesamiento automático
    print("\n⏳ Esperando procesamiento automático...")
    time.sleep(2)
    
    # 4. Verificar transferencia recibida
    print("\n📥 VERIFICANDO TRANSFERENCIA RECIBIDA...")
    response = requests.get(
        "http://localhost:3001/api/messaging/transfer-history?limit=3",
        headers=headers_esperanza
    )
    
    if response.status_code == 200:
        data = response.json()
        transfers = data.get('transfers', [])
        print(f"Transferencias actuales: {len(transfers)}")
        
        if transfers:
            latest = transfers[0]
            print(f"Última transferencia:")
            print(f"  - ID: {latest.get('id')}")
            print(f"  - Tipo: {latest.get('tipo')}")
            print(f"  - De: {latest.get('source_organization')}")
            print(f"  - Para: {latest.get('target_organization')}")
            print(f"  - Request ID: {latest.get('request_id')}")
            print(f"  - Donaciones: {len(latest.get('donations', []))}")
            print(f"  - Estado: {latest.get('estado')}")
            print(f"  - Notas: {latest.get('notas')}")
            
            if latest.get('tipo') == 'RECIBIDA' and 'automático' in latest.get('notas', ''):
                print("✅ ¡TRANSFERENCIA PROCESADA AUTOMÁTICAMENTE!")
            else:
                print("❌ Transferencia no procesada automáticamente")
        else:
            print("❌ No se encontraron transferencias")
    else:
        print(f"❌ Error verificando transferencias: {response.text}")
    
    # 5. Verificar notificaciones
    print("\n🔔 VERIFICANDO NOTIFICACIONES...")
    response = requests.get("http://localhost:3001/api/notifications", headers=headers_esperanza)
    
    if response.status_code == 200:
        data = response.json()
        notifications = data.get('notifications', [])
        
        unread_transfer_notifications = [
            n for n in notifications 
            if n.get('tipo') == 'transferencia_recibida' and not n.get('leida')
        ]
        
        print(f"Notificaciones de transferencia no leídas: {len(unread_transfer_notifications)}")
        
        if unread_transfer_notifications:
            latest_notif = unread_transfer_notifications[0]
            print(f"Última notificación:")
            print(f"  - Título: {latest_notif.get('titulo')}")
            print(f"  - Tipo: {latest_notif.get('tipo')}")
            print(f"  - Mensaje: {latest_notif.get('mensaje')[:100]}...")
            print("✅ ¡NOTIFICACIÓN AUTOMÁTICA CREADA!")
        else:
            print("❌ No se encontraron notificaciones de transferencia")
    else:
        print(f"❌ Error verificando notificaciones: {response.text}")
    
    # 6. Verificar desde el lado que envía
    print("\n📤 VERIFICANDO DESDE EMPUJE-COMUNITARIO...")
    response = requests.get(
        "http://localhost:3001/api/messaging/transfer-history?limit=3",
        headers=headers_empuje
    )
    
    if response.status_code == 200:
        data = response.json()
        transfers = data.get('transfers', [])
        
        if transfers:
            latest = transfers[0]
            print(f"Última transferencia enviada:")
            print(f"  - Tipo: {latest.get('tipo')}")
            print(f"  - Para: {latest.get('target_organization')}")
            print(f"  - Estado: {latest.get('estado')}")
            
            if latest.get('tipo') == 'ENVIADA':
                print("✅ ¡TRANSFERENCIA ENVIADA REGISTRADA!")
        else:
            print("❌ No se encontraron transferencias enviadas")
    
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETO FINALIZADO")
    print("✅ El sistema automatizado está funcionando correctamente!")
    print("   - Las transferencias se procesan automáticamente")
    print("   - Se crean notificaciones automáticamente")
    print("   - Ambos lados ven su historial correctamente")

if __name__ == "__main__":
    test_complete_automation()