#!/usr/bin/env python3
"""
Script para probar la cancelación de solicitudes con Fundación Esperanza
"""
import requests
import json
import mysql.connector

def test_cancel_esperanza():
    """Prueba la cancelación de solicitudes con Fundación Esperanza"""
    
    # Configuración
    API_BASE = "http://localhost:3001/api"
    
    # Credenciales de Fundación Esperanza
    login_data = {
        "usernameOrEmail": "esperanza_admin",
        "password": "password123"
    }
    
    try:
        print("=== PROBANDO CANCELACIÓN CON FUNDACIÓN ESPERANZA ===\n")
        
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
        
        # 2. Crear una solicitud para probar
        print("\n2. Creando solicitud para probar cancelación...")
        new_request_data = {
            "donations": [
                {"category": "ALIMENTOS", "description": "Alimentos para cancelar"},
            ],
            "notes": "Solicitud de Esperanza para probar cancelación"
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
            print(f"Response: {create_response.text}")
            return False
        
        # 3. Verificar que aparece en solicitudes activas
        print("\n3. Verificando solicitudes activas...")
        active_response = requests.post(f"{API_BASE}/messaging/active-requests", headers=headers)
        
        if active_response.status_code == 200:
            active_data = active_response.json()
            requests_list = active_data.get('requests', [])
            print(f"✅ Solicitudes activas: {len(requests_list)}")
            
            # Buscar nuestra solicitud
            found = any(req['request_id'] == request_id for req in requests_list)
            if found:
                print(f"✅ Solicitud {request_id} encontrada en lista activa")
            else:
                print(f"⚠ Solicitud {request_id} no encontrada en lista activa")
        
        # 4. Cancelar la solicitud
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
        
        # 5. Verificar en base de datos
        print("\n5. Verificando en base de datos...")
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor()
        
        # Verificar en solicitudes_externas
        cursor.execute("""
            SELECT solicitud_id, organizacion_solicitante, activa 
            FROM solicitudes_externas 
            WHERE solicitud_id = %s
        """, (request_id,))
        
        result = cursor.fetchone()
        if result:
            print(f"✅ En solicitudes_externas: {result[0]} - Org: {result[1]} - Activa: {result[2]}")
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
    if test_cancel_esperanza():
        print("\n🎉 Prueba de cancelación con Esperanza completada!")
    else:
        print("\n❌ Prueba de cancelación con Esperanza falló")