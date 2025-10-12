#!/usr/bin/env python3
"""
Test del flujo real de transferencias
"""
import requests
import mysql.connector
import time

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

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

def check_transfers_before():
    """Verificar transferencias antes"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM transferencias_donaciones WHERE organizacion_propietaria = 'empuje-comunitario'")
    empuje_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM transferencias_donaciones WHERE organizacion_propietaria = 'esperanza-social'")
    esperanza_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    print(f"ANTES - Empuje: {empuje_count}, Esperanza: {esperanza_count}")
    return empuje_count, esperanza_count

def make_transfer():
    """Hacer transferencia real"""
    token = get_token('empuje-comunitario')
    headers = {'Authorization': f'Bearer {token}'}
    
    transfer_data = {
        "targetOrganization": "esperanza-social",
        "requestId": f"real-test-{int(time.time())}",
        "donations": [
            {
                "inventoryId": 13,
                "quantity": "1",
                "category": "ALIMENTOS",
                "description": "Prueba de donación multi-org"
            }
        ],
        "userId": 11
    }
    
    response = requests.post(
        "http://localhost:50054/api/transferDonations",
        json=transfer_data,
        headers=headers
    )
    
    print(f"Transfer Status: {response.status_code}")
    print(f"Transfer Response: {response.text}")
    
    return response.status_code == 200

def check_transfers_after():
    """Verificar transferencias después"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM transferencias_donaciones WHERE organizacion_propietaria = 'empuje-comunitario'")
    empuje_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM transferencias_donaciones WHERE organizacion_propietaria = 'esperanza-social'")
    esperanza_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    print(f"DESPUÉS - Empuje: {empuje_count}, Esperanza: {esperanza_count}")
    return empuje_count, esperanza_count

def check_notifications():
    """Verificar notificaciones"""
    # Esperanza
    token = get_token('esperanza-social')
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get("http://localhost:3001/api/notifications", headers=headers)
    if response.status_code == 200:
        notifications = response.json().get('notifications', [])
        print(f"Notificaciones Esperanza: {len(notifications)}")
        for notif in notifications[:2]:
            print(f"  - {notif.get('titulo')}")

def main():
    print("🧪 TEST FLUJO REAL DE TRANSFERENCIAS")
    print("=" * 50)
    
    # 1. Estado inicial
    empuje_before, esperanza_before = check_transfers_before()
    
    # 2. Hacer transferencia
    if make_transfer():
        print("✅ Transferencia enviada")
        
        # 3. Esperar procesamiento
        print("⏳ Esperando 10 segundos...")
        time.sleep(10)
        
        # 4. Verificar resultados
        empuje_after, esperanza_after = check_transfers_after()
        
        print(f"\nCambios:")
        print(f"Empuje: {empuje_before} -> {empuje_after} (diff: {empuje_after - empuje_before})")
        print(f"Esperanza: {esperanza_before} -> {esperanza_after} (diff: {esperanza_after - esperanza_before})")
        
        if empuje_after > empuje_before and esperanza_after > esperanza_before:
            print("✅ Consumer funcionando - ambas transferencias creadas")
        elif empuje_after > empuje_before:
            print("❌ Consumer NO funcionando - solo transferencia ENVIADA")
        else:
            print("❌ Error - no se creó ninguna transferencia")
        
        # 5. Verificar notificaciones
        check_notifications()
    else:
        print("❌ Error en transferencia")

if __name__ == "__main__":
    main()