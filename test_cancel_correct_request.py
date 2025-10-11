#!/usr/bin/env python3
"""
Script para probar la cancelación con la solicitud correcta de Fundación Esperanza
"""
import requests
import json
import mysql.connector

def test_cancel_correct_request():
    """Prueba la cancelación con la solicitud correcta"""
    
    # Configuración
    API_BASE = "http://localhost:3001/api"
    
    # Credenciales de Fundación Esperanza
    login_data = {
        "usernameOrEmail": "esperanza_admin",
        "password": "password123"
    }
    
    # ID de la solicitud correcta que encontramos
    correct_request_id = "req-esperanza-1760205347"
    
    try:
        print("=== PROBANDO CANCELACIÓN CON SOLICITUD CORRECTA ===\n")
        
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
        
        # 2. Verificar solicitudes activas
        print("\n2. Verificando solicitudes activas...")
        active_response = requests.post(f"{API_BASE}/messaging/active-requests", headers=headers)
        
        if active_response.status_code == 200:
            active_data = active_response.json()
            requests_list = active_data.get('requests', [])
            print(f"✅ Solicitudes activas: {len(requests_list)}")
            
            for req in requests_list:
                print(f"   - {req['request_id']}")
            
            # Verificar que nuestra solicitud esté en la lista
            found = any(req['request_id'] == correct_request_id for req in requests_list)
            if found:
                print(f"✅ Solicitud {correct_request_id} encontrada en lista activa")
            else:
                print(f"⚠ Solicitud {correct_request_id} no encontrada en lista activa")
                return False
        else:
            print(f"❌ Error obteniendo solicitudes activas: {active_response.status_code}")
            return False
        
        # 3. Cancelar la solicitud correcta
        print(f"\n3. Cancelando solicitud {correct_request_id}...")
        cancel_data = {
            "requestId": correct_request_id
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
        print("\n4. Verificando en base de datos...")
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
        """, (correct_request_id,))
        
        result = cursor.fetchone()
        if result:
            print(f"✅ En solicitudes_externas: {result[0]} - Org: {result[1]} - Activa: {result[2]}")
            if result[2] == 0:
                print("✅ Solicitud marcada como inactiva correctamente")
            else:
                print("⚠ Solicitud sigue activa")
        else:
            print("⚠ No encontrada en solicitudes_externas")
        
        # 5. Verificar que ya no aparece en solicitudes activas
        print("\n5. Verificando que ya no aparece en solicitudes activas...")
        active_response2 = requests.post(f"{API_BASE}/messaging/active-requests", headers=headers)
        
        if active_response2.status_code == 200:
            active_data2 = active_response2.json()
            requests_list2 = active_data2.get('requests', [])
            print(f"✅ Solicitudes activas después de cancelar: {len(requests_list2)}")
            
            found_after = any(req['request_id'] == correct_request_id for req in requests_list2)
            if not found_after:
                print(f"✅ Solicitud {correct_request_id} ya no aparece en lista activa")
            else:
                print(f"⚠ Solicitud {correct_request_id} todavía aparece en lista activa")
        
        conn.close()
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está corriendo el API Gateway?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    if test_cancel_correct_request():
        print("\n🎉 Prueba de cancelación con solicitud correcta completada!")
    else:
        print("\n❌ Prueba de cancelación con solicitud correcta falló")