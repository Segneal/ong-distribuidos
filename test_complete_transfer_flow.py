#!/usr/bin/env python3
"""
Test completo del flujo de transferencias y notificaciones
"""
import requests
import json
import mysql.connector
from datetime import datetime
import time

# Configuración
API_BASE = "http://localhost:3001/api"
MESSAGING_BASE = "http://localhost:50054/api"
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def get_db_connection():
    """Obtener conexión a la base de datos"""
    return mysql.connector.connect(**DB_CONFIG)

def get_valid_token(organization='empuje-comunitario'):
    """Obtener un token válido para pruebas"""
    if organization == 'empuje-comunitario':
        # Token para admin de Empuje Comunitario
        login_data = {
            "usernameOrEmail": "admin",
            "password": "admin123"
        }
    else:
        # Token para admin de Esperanza Social
        login_data = {
            "usernameOrEmail": "admin_esperanza",
            "password": "admin123"
        }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            return data.get('token')
        else:
            print(f"Error obteniendo token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error en login: {e}")
        return None

def create_test_request():
    """Crear una solicitud de donación de prueba"""
    print("\n=== CREANDO SOLICITUD DE DONACIÓN ===")
    
    token = get_valid_token('esperanza-social')
    if not token:
        print("❌ No se pudo obtener token para Esperanza")
        return None
    
    headers = {'Authorization': f'Bearer {token}'}
    
    request_data = {
        "donations": [
            {
                "categoria": "ALIMENTOS",
                "descripcion": "Arroz integral 1kg",
                "cantidad": 20
            },
            {
                "categoria": "ROPA", 
                "descripcion": "Camisetas talle L",
                "cantidad": 15
            }
        ],
        "userId": 26,  # admin_esperanza
        "userOrganization": "esperanza-social",
        "notes": "Solicitud de prueba para testing"
    }
    
    try:
        response = requests.post(
            f"{MESSAGING_BASE}/createDonationRequest",
            json=request_data,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            request_id = data.get('request_id')
            print(f"✅ Solicitud creada: {request_id}")
            return request_id
        else:
            print("❌ Error creando solicitud")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def transfer_donations_to_request(request_id):
    """Transferir donaciones a la solicitud"""
    print(f"\n=== TRANSFIRIENDO DONACIONES A SOLICITUD {request_id} ===")
    
    token = get_valid_token('empuje-comunitario')
    if not token:
        print("❌ No se pudo obtener token para Empuje Comunitario")
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    transfer_data = {
        "targetOrganization": "esperanza-social",
        "requestId": request_id,
        "donations": [
            {
                "inventoryId": 12,  # Prueba de donación multi-org
                "quantity": "5",
                "category": "ALIMENTOS",
                "description": "Prueba de donación multi-org"
            },
            {
                "inventoryId": 4,  # Camisetas talle M
                "quantity": "8",
                "category": "ROPA", 
                "description": "Camisetas talle M"
            }
        ],
        "userId": 11  # admin de empuje-comunitario
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
            data = response.json()
            transfer_id = data.get('transfer_id')
            print(f"✅ Transferencia realizada: {transfer_id}")
            return True
        else:
            print("❌ Error en transferencia")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def check_transfer_history():
    """Verificar historial de transferencias"""
    print("\n=== VERIFICANDO HISTORIAL DE TRANSFERENCIAS ===")
    
    # Verificar para Empuje Comunitario (enviadas)
    token_empuje = get_valid_token('empuje-comunitario')
    if token_empuje:
        headers = {'Authorization': f'Bearer {token_empuje}'}
        
        try:
            response = requests.post(
                f"{MESSAGING_BASE}/getTransferHistory",
                json={"organizationId": "empuje-comunitario", "limit": 10},
                headers=headers
            )
            
            print(f"Empuje Comunitario - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                transfers = data.get('transfers', [])
                print(f"Transferencias de Empuje Comunitario: {len(transfers)}")
                
                for transfer in transfers:
                    print(f"  - Tipo: {transfer.get('tipo')}")
                    print(f"    Contraparte: {transfer.get('organizacion_contraparte')}")
                    print(f"    Fecha: {transfer.get('fecha_transferencia')}")
                    print(f"    Donaciones: {len(transfer.get('donations', []))}")
            
        except Exception as e:
            print(f"Error verificando Empuje Comunitario: {e}")
    
    # Verificar para Esperanza Social (recibidas)
    token_esperanza = get_valid_token('esperanza-social')
    if token_esperanza:
        headers = {'Authorization': f'Bearer {token_esperanza}'}
        
        try:
            response = requests.post(
                f"{MESSAGING_BASE}/getTransferHistory",
                json={"organizationId": "esperanza-social", "limit": 10},
                headers=headers
            )
            
            print(f"Esperanza Social - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                transfers = data.get('transfers', [])
                print(f"Transferencias de Esperanza Social: {len(transfers)}")
                
                for transfer in transfers:
                    print(f"  - Tipo: {transfer.get('tipo')}")
                    print(f"    Contraparte: {transfer.get('organizacion_contraparte')}")
                    print(f"    Fecha: {transfer.get('fecha_transferencia')}")
                    print(f"    Donaciones: {len(transfer.get('donations', []))}")
            
        except Exception as e:
            print(f"Error verificando Esperanza Social: {e}")

def check_notifications():
    """Verificar notificaciones"""
    print("\n=== VERIFICANDO NOTIFICACIONES ===")
    
    # Verificar notificaciones para admin de Esperanza
    token = get_valid_token('esperanza-social')
    if not token:
        print("❌ No se pudo obtener token para verificar notificaciones")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(
            f"{API_BASE}/notifications",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            notifications = data.get('notifications', [])
            print(f"✅ Notificaciones encontradas: {len(notifications)}")
            
            for notif in notifications:
                print(f"  - Tipo: {notif.get('tipo')}")
                print(f"    Título: {notif.get('titulo')}")
                print(f"    Mensaje: {notif.get('mensaje')[:100]}...")
                print(f"    Fecha: {notif.get('fecha_creacion')}")
                print(f"    Leída: {notif.get('leida')}")
        else:
            print("❌ Error obteniendo notificaciones")
            
    except Exception as e:
        print(f"Error: {e}")

def check_database_state():
    """Verificar estado de la base de datos"""
    print("\n=== VERIFICANDO ESTADO DE BASE DE DATOS ===")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar transferencias
        cursor.execute("""
            SELECT COUNT(*) as total, tipo, organizacion_propietaria
            FROM transferencias_donaciones 
            GROUP BY tipo, organizacion_propietaria
        """)
        
        transfers = cursor.fetchall()
        print("Transferencias por tipo y organización:")
        for transfer in transfers:
            print(f"  - {transfer['tipo']} ({transfer['organizacion_propietaria']}): {transfer['total']}")
        
        # Verificar notificaciones
        cursor.execute("""
            SELECT COUNT(*) as total, tipo, leida
            FROM notificaciones 
            GROUP BY tipo, leida
        """)
        
        notifications = cursor.fetchall()
        print("\nNotificaciones por tipo y estado:")
        for notif in notifications:
            estado = "Leída" if notif['leida'] else "No leída"
            print(f"  - {notif['tipo']} ({estado}): {notif['total']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error verificando base de datos: {e}")

def main():
    """Función principal"""
    print("🧪 TEST COMPLETO DE FLUJO DE TRANSFERENCIAS")
    print("=" * 60)
    
    # 1. Verificar estado inicial
    check_database_state()
    
    # 2. Crear solicitud de donación
    request_id = create_test_request()
    if not request_id:
        print("❌ No se pudo crear la solicitud. Abortando test.")
        return
    
    # 3. Esperar un momento para que se procese
    print("\n⏳ Esperando 3 segundos...")
    time.sleep(3)
    
    # 4. Transferir donaciones
    if not transfer_donations_to_request(request_id):
        print("❌ No se pudo realizar la transferencia. Continuando con verificaciones...")
    
    # 5. Esperar para que se procese la transferencia
    print("\n⏳ Esperando 5 segundos para que se procese la transferencia...")
    time.sleep(5)
    
    # 6. Verificar resultados
    check_transfer_history()
    check_notifications()
    check_database_state()
    
    print("\n🏁 TEST COMPLETADO")

if __name__ == "__main__":
    main()