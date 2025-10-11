#!/usr/bin/env python3
"""
Script para probar la transferencia de donaciones
"""
import requests
import json
import mysql.connector

def test_transfer_donations():
    """Prueba la transferencia de donaciones"""
    
    # Configuración
    API_BASE = "http://localhost:3001/api"
    
    # Credenciales de prueba (usuario que va a transferir)
    login_data = {
        "usernameOrEmail": "esperanza_admin",
        "password": "password123"
    }
    
    try:
        print("=== PROBANDO TRANSFERENCIA DE DONACIONES ===\n")
        
        # 1. Login
        print("1. Haciendo login...")
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            return False
        
        login_result = login_response.json()
        token = login_result.get('token')
        user_info = login_result.get('user', {})
        
        print(f"✅ Login exitoso - Organización: {user_info.get('organization')}")
        
        # Headers con token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 2. Verificar que hay solicitudes externas disponibles
        print("\n2. Verificando solicitudes externas...")
        external_response = requests.post(f"{API_BASE}/messaging/external-requests", headers=headers)
        
        if external_response.status_code != 200:
            print(f"❌ Error obteniendo solicitudes externas: {external_response.status_code}")
            return False
        
        external_data = external_response.json()
        external_requests = external_data.get('requests', [])
        
        print(f"✅ Solicitudes externas encontradas: {len(external_requests)}")
        
        if not external_requests:
            print("⚠ No hay solicitudes externas para transferir")
            return False
        
        # Usar la primera solicitud externa
        target_request = external_requests[0]
        print(f"✅ Usando solicitud: {target_request['request_id']} de {target_request['requesting_organization']}")
        
        # 3. Verificar inventario disponible
        print("\n3. Verificando inventario disponible...")
        inventory_response = requests.get(f"{API_BASE}/inventory", headers=headers)
        
        if inventory_response.status_code != 200:
            print(f"❌ Error obteniendo inventario: {inventory_response.status_code}")
            return False
        
        inventory_data = inventory_response.json()
        inventory_items = inventory_data.get('donations', [])
        
        print(f"✅ Items de inventario encontrados: {len(inventory_items)}")
        
        if not inventory_items:
            print("⚠ No hay items en el inventario para transferir")
            return False
        
        # Usar el primer item con cantidad > 0
        available_item = None
        for item in inventory_items:
            if item.get('quantity', 0) > 0:
                available_item = item
                break
        
        if not available_item:
            print("⚠ No hay items con cantidad disponible")
            return False
        
        print(f"✅ Usando item: {available_item['description']} (ID: {available_item['id']}, Cantidad: {available_item['quantity']})")
        
        # 4. Preparar datos de transferencia
        transfer_data = {
            "targetOrganization": target_request['requesting_organization'],
            "requestId": target_request['request_id'],
            "donations": [
                {
                    "category": available_item['category'],
                    "description": available_item['description'],
                    "quantity": "1",  # Transferir 1 unidad
                    "inventoryId": available_item['id']
                }
            ]
        }
        
        print(f"\n4. Datos de transferencia:")
        print(f"   Target: {transfer_data['targetOrganization']}")
        print(f"   Request: {transfer_data['requestId']}")
        print(f"   Donations: {len(transfer_data['donations'])} items")
        
        # 5. Realizar transferencia
        print("\n5. Realizando transferencia...")
        transfer_response = requests.post(
            f"{API_BASE}/messaging/transfer-donations",
            headers=headers,
            json=transfer_data
        )
        
        print(f"Status: {transfer_response.status_code}")
        print(f"Response: {transfer_response.text}")
        
        if transfer_response.status_code == 200:
            transfer_result = transfer_response.json()
            if transfer_result.get('success'):
                print("✅ Transferencia exitosa!")
                print(f"   Transfer ID: {transfer_result.get('transfer_id')}")
            else:
                print(f"❌ Error en transferencia: {transfer_result.get('error')}")
                return False
        else:
            print(f"❌ Error HTTP en transferencia: {transfer_response.status_code}")
            return False
        
        # 6. Verificar en base de datos
        print("\n6. Verificando en base de datos...")
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor()
        
        # Verificar transferencia registrada
        cursor.execute("""
            SELECT tipo, organizacion_contraparte, solicitud_id, estado
            FROM transferencias_donaciones 
            ORDER BY fecha_transferencia DESC 
            LIMIT 1
        """)
        
        transfer_record = cursor.fetchone()
        if transfer_record:
            print(f"✅ Transferencia registrada:")
            print(f"   Tipo: {transfer_record[0]}")
            print(f"   Organización: {transfer_record[1]}")
            print(f"   Solicitud: {transfer_record[2]}")
            print(f"   Estado: {transfer_record[3]}")
        else:
            print("⚠ No se encontró registro de transferencia")
        
        # Verificar inventario actualizado
        cursor.execute("""
            SELECT quantity FROM donaciones WHERE id = %s
        """, (available_item['id'],))
        
        updated_quantity = cursor.fetchone()
        if updated_quantity:
            new_quantity = updated_quantity[0]
            original_quantity = available_item['quantity']
            print(f"✅ Inventario actualizado:")
            print(f"   Cantidad original: {original_quantity}")
            print(f"   Cantidad actual: {new_quantity}")
            print(f"   Diferencia: {original_quantity - new_quantity}")
        
        conn.close()
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Están corriendo los servicios?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    if test_transfer_donations():
        print("\n🎉 Prueba de transferencia completada!")
    else:
        print("\n❌ Prueba de transferencia falló")