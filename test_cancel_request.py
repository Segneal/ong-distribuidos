#!/usr/bin/env python3
"""
Script para probar la cancelación de solicitudes
"""
import requests
import json
import mysql.connector

def test_cancel_request():
    """Prueba la cancelación de solicitudes"""
    
    # Configuración
    API_BASE = "http://localhost:3001/api"
    
    # Credenciales de prueba
    login_data = {
        "usernameOrEmail": "admin",
        "password": "admin123"
    }
    
    try:
        print("=== PROBANDO CANCELACIÓN DE SOLICITUDES ===\n")
        
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
        
        # 2. Obtener solicitudes activas
        print("\n2. Obteniendo solicitudes activas...")
        active_response = requests.post(f"{API_BASE}/messaging/active-requests", headers=headers)
        
        if active_response.status_code != 200:
            print(f"❌ Error obteniendo solicitudes: {active_response.status_code}")
            return False
        
        active_data = active_response.json()
        requests_list = active_data.get('requests', [])
        
        print(f"✅ Solicitudes activas encontradas: {len(requests_list)}")
        
        if not requests_list:
            print("⚠ No hay solicitudes activas para cancelar")
            
            # Crear una solicitud para probar
            print("\n3. Creando solicitud para probar cancelación...")
            new_request_data = {
                "donations": [
                    {"category": "ROPA", "description": "Ropa para cancelar"},
                ],
                "notes": "Solicitud para probar cancelación"
            }
            
            create_response = requests.post(
                f"{API_BASE}/messaging/create-donation-request", 
                headers=headers,
                json=new_request_data
            )
            
            if create_response.status_code == 200:
                create_data = create_response.json()
                request_id = create_data.get('request_id')
                print(f"✅ Solicitud creada: {request_id}")
            else:
                print(f"❌ Error creando solicitud: {create_response.status_code}")
                return False
        else:
            # Usar la primera solicitud activa
            request_id = requests_list[0]['request_id']
            print(f"✅ Usando solicitud existente: {request_id}")
        
        # 3. Cancelar la solicitud
        print(f"\n4. Cancelando solicitud {request_id}...")
        cancel_data = {
            "requestId": request_id
        }
        
        cancel_response = requests.post(
            f"{API_BASE}/messaging/cancel-donation-request",
            headers=headers,
            json=cancel_data
        )
        
        print(f"Status de cancelación: {cancel_response.status_code}")
        print(f"Response: {cancel_response.text}")
        
        if cancel_response.status_code == 200:
            print("✅ Solicitud cancelada exitosamente")
        else:
            print(f"❌ Error cancelando solicitud: {cancel_response.status_code}")
            return False
        
        # 4. Verificar en base de datos
        print("\n5. Verificando en base de datos...")
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor()
        
        # Verificar en solicitudes_donaciones
        cursor.execute("""
            SELECT solicitud_id, estado 
            FROM solicitudes_donaciones 
            WHERE solicitud_id = %s
        """, (request_id,))
        
        result = cursor.fetchone()
        if result:
            print(f"✅ En solicitudes_donaciones: {result[0]} - Estado: {result[1]}")
        else:
            print("⚠ No encontrada en solicitudes_donaciones")
        
        # Verificar en solicitudes_externas
        cursor.execute("""
            SELECT solicitud_id, activa 
            FROM solicitudes_externas 
            WHERE solicitud_id = %s
        """, (request_id,))
        
        result = cursor.fetchone()
        if result:
            print(f"✅ En solicitudes_externas: {result[0]} - Activa: {result[1]}")
        else:
            print("⚠ No encontrada en solicitudes_externas")
        
        conn.close()
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está corriendo el API Gateway?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    if test_cancel_request():
        print("\n🎉 Prueba de cancelación completada!")
    else:
        print("\n❌ Prueba de cancelación falló")