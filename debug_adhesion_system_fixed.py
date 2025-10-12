#!/usr/bin/env python3
"""
Debug del sistema de adhesiones - versión corregida
"""
import mysql.connector
import requests
import json

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def check_current_adhesions():
    """Verificar adhesiones actuales"""
    print("📋 VERIFICANDO ADHESIONES ACTUALES")
    print("=" * 40)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Adhesiones con detalles
        cursor.execute("""
            SELECT 
                aee.id,
                aee.evento_externo_id,
                aee.voluntario_id,
                aee.estado,
                aee.fecha_adhesion,
                u.nombre_usuario,
                u.nombre,
                u.apellido,
                u.organizacion as voluntario_org,
                er.nombre as evento_nombre,
                er.organizacion_origen as evento_org
            FROM adhesiones_eventos_externos aee
            LEFT JOIN usuarios u ON aee.voluntario_id = u.id
            LEFT JOIN eventos_red er ON aee.evento_externo_id = er.evento_id
            ORDER BY aee.fecha_adhesion DESC
            LIMIT 10
        """)
        
        adhesions = cursor.fetchall()
        print(f"Adhesiones recientes ({len(adhesions)}):")
        
        for adhesion in adhesions:
            print(f"  ID: {adhesion['id']}")
            print(f"    Evento: {adhesion['evento_nombre']} (ID: {adhesion['evento_externo_id']})")
            print(f"    Voluntario: {adhesion['nombre']} {adhesion['apellido']} ({adhesion['voluntario_org']})")
            print(f"    Estado: {adhesion['estado']}")
            print(f"    Fecha: {adhesion['fecha_adhesion']}")
            print(f"    Org del evento: {adhesion['evento_org']}")
            print()
        
        # Estadísticas por estado
        cursor.execute("""
            SELECT estado, COUNT(*) as total
            FROM adhesiones_eventos_externos
            GROUP BY estado
        """)
        
        stats = cursor.fetchall()
        print("Estadísticas por estado:")
        for stat in stats:
            print(f"  {stat['estado']}: {stat['total']}")
        
        cursor.close()
        conn.close()
        
        return adhesions
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def find_admin_user_for_org(org):
    """Encontrar usuario admin para organización"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, nombre_usuario, nombre, apellido, rol
            FROM usuarios 
            WHERE organizacion = %s AND rol IN ('PRESIDENTE', 'COORDINADOR')
            LIMIT 1
        """, (org,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return user
        
    except Exception as e:
        print(f"❌ Error buscando admin: {e}")
        return None

def test_adhesion_approval_flow():
    """Test completo del flujo de aprobación"""
    print("\n✅ TESTING FLUJO DE APROBACIÓN COMPLETO")
    print("=" * 50)
    
    # 1. Obtener adhesiones pendientes
    adhesions = check_current_adhesions()
    
    pending_adhesions = [a for a in adhesions if a['estado'] == 'PENDIENTE']
    
    if not pending_adhesions:
        print("⚠️  No hay adhesiones pendientes para test")
        return
    
    # 2. Tomar la primera adhesión pendiente
    adhesion = pending_adhesions[0]
    event_org = adhesion['evento_org']
    
    print(f"Testing con adhesión ID: {adhesion['id']}")
    print(f"Evento: {adhesion['evento_nombre']}")
    print(f"Organización del evento: {event_org}")
    
    # 3. Encontrar usuario admin de la organización del evento
    admin_user = find_admin_user_for_org(event_org)
    
    if not admin_user:
        print(f"❌ No se encontró usuario admin para {event_org}")
        return
    
    print(f"Usuario admin: {admin_user['nombre']} {admin_user['apellido']} ({admin_user['rol']})")
    
    # 4. Intentar login con diferentes credenciales
    login_attempts = []
    
    if event_org == 'empuje-comunitario':
        login_attempts = [
            {"usernameOrEmail": "admin", "password": "admin123"},
            {"usernameOrEmail": admin_user['nombre_usuario'], "password": "admin123"}
        ]
    elif event_org == 'fundacion-esperanza':
        login_attempts = [
            {"usernameOrEmail": "admin_fundacion", "password": "admin123"},
            {"usernameOrEmail": admin_user['nombre_usuario'], "password": "admin123"}
        ]
    else:
        login_attempts = [
            {"usernameOrEmail": admin_user['nombre_usuario'], "password": "admin123"}
        ]
    
    token = None
    for login_data in login_attempts:
        response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
        print(f"Login attempt {login_data['usernameOrEmail']}: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get('token')
            print(f"✅ Login exitoso")
            break
        else:
            print(f"❌ Error: {response.text}")
    
    if not token:
        print("❌ No se pudo hacer login")
        return
    
    # 5. Obtener adhesiones para el evento
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.post(
        "http://localhost:3001/api/messaging/event-adhesions",
        json={"eventId": adhesion['evento_externo_id']},
        headers=headers
    )
    
    print(f"\\nEvent adhesions API - Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        api_adhesions = data.get('adhesions', [])
        print(f"Adhesiones desde API: {len(api_adhesions)}")
        
        for api_adhesion in api_adhesions:
            print(f"  - ID: {api_adhesion.get('id')}, Estado: {api_adhesion.get('status')}")
            print(f"    Voluntario: {api_adhesion.get('volunteer_name')} {api_adhesion.get('volunteer_surname')}")
        
        # 6. Buscar endpoints de aprobación
        print("\\n🔍 Buscando endpoints de aprobación...")
        
        if api_adhesions:
            test_adhesion = api_adhesions[0]
            
            endpoints_to_test = [
                ("/api/messaging/approve-adhesion", {"adhesionId": test_adhesion.get('id'), "action": "approve"}),
                ("/api/messaging/update-adhesion-status", {"adhesionId": test_adhesion.get('id'), "status": "CONFIRMADA"}),
                ("/api/events/approve-adhesion", {"adhesionId": test_adhesion.get('id'), "approved": True}),
                ("/api/adhesions/approve", {"id": test_adhesion.get('id'), "status": "CONFIRMADA"})
            ]
            
            for endpoint, data in endpoints_to_test:
                response = requests.post(
                    f"http://localhost:3001{endpoint}",
                    json=data,
                    headers=headers
                )
                
                print(f"  {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"    ✅ Funciona: {response.text}")
                elif response.status_code == 404:
                    print(f"    ❌ No existe")
                else:
                    print(f"    ⚠️  Error: {response.text}")
    else:
        print(f"❌ Error obteniendo adhesiones: {response.text}")

if __name__ == "__main__":
    print("🔧 DEBUG SISTEMA DE ADHESIONES - VERSIÓN CORREGIDA")
    print("=" * 60)
    
    test_adhesion_approval_flow()