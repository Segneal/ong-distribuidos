#!/usr/bin/env python3
"""
Test directo de transferencia sin solicitud previa
"""
import requests
import json
import mysql.connector
import time

# Configuración
MESSAGING_BASE = "http://localhost:50054/api"
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def get_valid_token():
    """Obtener token válido para empuje-comunitario"""
    login_data = {
        "usernameOrEmail": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data.get('token')
        else:
            print(f"Error obteniendo token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error en login: {e}")
        return None

def test_direct_transfer():
    """Test directo de transferencia"""
    print("=== TEST DIRECTO DE TRANSFERENCIA ===")
    
    token = get_valid_token()
    if not token:
        print("❌ No se pudo obtener token")
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    transfer_data = {
        "targetOrganization": "esperanza-social",
        "requestId": "direct-test-" + str(int(time.time())),
        "donations": [
            {
                "inventoryId": 12,
                "quantity": "1",
                "category": "ALIMENTOS",
                "description": "Prueba de donación multi-org"
            }
        ],
        "userId": 11
    }
    
    try:
        response = requests.post(
            f"{MESSAGING_BASE}/transferDonations",
            json=transfer_data,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Transferencia exitosa")
            return True
        else:
            print("❌ Error en transferencia")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def check_transfers_after():
    """Verificar transferencias después del test"""
    print("\n=== VERIFICANDO TRANSFERENCIAS DESPUÉS ===")
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Últimas 3 transferencias
        cursor.execute("""
            SELECT * FROM transferencias_donaciones 
            ORDER BY fecha_transferencia DESC 
            LIMIT 3
        """)
        
        transfers = cursor.fetchall()
        
        for transfer in transfers:
            print(f"ID: {transfer['id']}")
            print(f"Tipo: {transfer['tipo']}")
            print(f"Contraparte: {transfer['organizacion_contraparte']}")
            print(f"Propietaria: {transfer['organizacion_propietaria']}")
            print(f"Fecha: {transfer['fecha_transferencia']}")
            print("-" * 30)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Función principal"""
    print("🧪 TEST DIRECTO DE TRANSFERENCIA")
    print("=" * 40)
    
    # 1. Realizar transferencia
    if test_direct_transfer():
        # 2. Esperar procesamiento
        print("\n⏳ Esperando 10 segundos para procesamiento...")
        time.sleep(10)
        
        # 3. Verificar resultados
        check_transfers_after()
    
    print("\n🏁 TEST COMPLETADO")

if __name__ == "__main__":
    main()