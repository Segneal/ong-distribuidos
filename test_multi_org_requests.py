#!/usr/bin/env python3
"""
Script para probar solicitudes con múltiples organizaciones
"""
import requests
import json

def test_multi_org_requests():
    """Prueba solicitudes con diferentes organizaciones"""
    
    # Configuración
    API_BASE = "http://localhost:3001/api"
    
    # Credenciales de diferentes organizaciones
    users = [
        {
            "name": "admin (empuje-comunitario)",
            "credentials": {"usernameOrEmail": "admin", "password": "admin123"},
            "expected_org": "empuje-comunitario"
        },
        {
            "name": "esperanza_admin (fundacion-esperanza)",
            "credentials": {"usernameOrEmail": "esperanza_admin", "password": "password123"},
            "expected_org": "fundacion-esperanza"
        }
    ]
    
    try:
        print("=== PROBANDO SOLICITUDES MULTI-ORGANIZACIÓN ===\n")
        
        for user in users:
            print(f"--- Probando con {user['name']} ---")
            
            # 1. Login
            login_response = requests.post(f"{API_BASE}/auth/login", json=user["credentials"])
            
            if login_response.status_code != 200:
                print(f"❌ Error en login: {login_response.status_code}")
                print(f"Response: {login_response.text}")
                continue
            
            login_result = login_response.json()
            token = login_result.get('token')
            user_info = login_result.get('user', {})
            
            print(f"✅ Login exitoso")
            print(f"   Usuario: {user_info.get('username')}")
            print(f"   Organización: {user_info.get('organization')}")
            
            # Verificar que la organización sea la esperada
            if user_info.get('organization') != user['expected_org']:
                print(f"⚠ Organización inesperada: esperaba {user['expected_org']}, obtuvo {user_info.get('organization')}")
            
            # Headers con token
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # 2. Crear solicitud
            new_request_data = {
                "donations": [
                    {"category": "ROPA", "description": f"Ropa de {user['expected_org']}"},
                    {"category": "ALIMENTOS", "description": f"Alimentos de {user['expected_org']}"}
                ],
                "notes": f"Solicitud de prueba de {user['expected_org']}"
            }
            
            create_response = requests.post(
                f"{API_BASE}/messaging/create-donation-request", 
                headers=headers,
                json=new_request_data
            )
            
            if create_response.status_code == 200:
                create_data = create_response.json()
                print(f"✅ Solicitud creada: {create_data.get('request_id')}")
            else:
                print(f"❌ Error creando solicitud: {create_response.status_code}")
                print(f"Response: {create_response.text}")
            
            # 3. Ver solicitudes activas
            active_response = requests.post(f"{API_BASE}/messaging/active-requests", headers=headers)
            
            if active_response.status_code == 200:
                active_data = active_response.json()
                print(f"✅ Solicitudes activas propias: {len(active_data.get('requests', []))}")
            else:
                print(f"❌ Error obteniendo solicitudes activas: {active_response.status_code}")
            
            print()
        
        # 4. Verificar en base de datos
        print("--- Verificando en base de datos ---")
        import mysql.connector
        
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management',
            port=3306
        )
        cursor = conn.cursor()
        
        # Solicitudes por organización
        cursor.execute("""
            SELECT 
                organization_id,
                COUNT(*) as count
            FROM solicitudes_donaciones 
            WHERE estado = 'ACTIVA'
            GROUP BY organization_id
        """)
        
        org_counts = cursor.fetchall()
        print("Solicitudes activas por organización (solicitudes_donaciones):")
        for org, count in org_counts:
            print(f"  - {org}: {count} solicitudes")
        
        # Solicitudes externas por organización
        cursor.execute("""
            SELECT 
                organizacion_solicitante,
                COUNT(*) as count
            FROM solicitudes_externas 
            WHERE activa = 1
            GROUP BY organizacion_solicitante
        """)
        
        ext_counts = cursor.fetchall()
        print("\nSolicitudes activas por organización (solicitudes_externas):")
        for org, count in ext_counts:
            print(f"  - {org}: {count} solicitudes")
        
        conn.close()
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está corriendo el API Gateway en el puerto 3001?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    if test_multi_org_requests():
        print("\n🎉 Pruebas multi-organización completadas!")
    else:
        print("\n❌ Algunas pruebas fallaron")