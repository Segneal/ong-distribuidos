#!/usr/bin/env python3
"""
Crear transferencia de test para probar automatización
"""
import requests
import time

def create_test_transfer():
    """Crear transferencia de test"""
    print("🧪 CREANDO TRANSFERENCIA DE TEST")
    print("=" * 40)
    
    # Login
    login_data = {"usernameOrEmail": "admin", "password": "admin123"}
    response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Error login: {response.text}")
        return
    
    token = response.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Crear transferencia directa en DB usando el script existente
    import mysql.connector
    import json
    from datetime import datetime
    
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root',
        'database': 'ong_management'
    }
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Crear transferencia ENVIADA
        request_id = f"test-auto-{int(time.time())}"
        donations = json.dumps([{
            "category": "ALIMENTOS",
            "quantity": "1",
            "description": "Test automatización",
            "inventoryId": 12,
            "inventory_id": 12,
            "parsed_quantity": 1
        }])
        
        cursor.execute("""
            INSERT INTO transferencias_donaciones 
            (tipo, organizacion_contraparte, solicitud_id, donaciones, estado, fecha_transferencia, usuario_registro, notas, organizacion_propietaria)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            'ENVIADA',
            'esperanza-social',
            request_id,
            donations,
            'COMPLETADA',
            datetime.now(),
            1,  # admin user id
            'Test para automatización',
            'empuje-comunitario'
        ))
        
        transfer_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Transferencia ENVIADA creada: ID {transfer_id}")
        print(f"   Request ID: {request_id}")
        
        # Ahora probar el endpoint automático
        print("\n🤖 PROBANDO PROCESAMIENTO AUTOMÁTICO...")
        response = requests.post("http://localhost:3001/api/messaging/process-pending-transfers")
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('processed', 0) > 0:
                print("✅ ¡PROCESAMIENTO AUTOMÁTICO EXITOSO!")
            else:
                print("⚠️  No se procesaron transferencias")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_test_transfer()