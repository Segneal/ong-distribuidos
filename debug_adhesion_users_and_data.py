#!/usr/bin/env python3
"""
Debug de usuarios y datos de adhesiones
"""
import mysql.connector
import json

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def check_users_and_organizations():
    """Verificar usuarios y organizaciones"""
    print("👥 VERIFICANDO USUARIOS Y ORGANIZACIONES")
    print("=" * 50)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Usuarios por organización
        cursor.execute("""
            SELECT organizacion, COUNT(*) as total, 
                   GROUP_CONCAT(CONCAT(username, ' (', rol, ')') SEPARATOR ', ') as usuarios
            FROM usuarios 
            GROUP BY organizacion
            ORDER BY organizacion
        """)
        
        orgs = cursor.fetchall()
        print("Organizaciones y usuarios:")
        for org in orgs:
            print(f"  {org['organizacion']}: {org['total']} usuarios")
            print(f"    {org['usuarios']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def check_current_adhesions():
    """Verificar adhesiones actuales"""
    print("\n📋 VERIFICANDO ADHESIONES ACTUALES")
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
                u.username,
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
            print(f"    Voluntario: {adhesion['username']} ({adhesion['voluntario_org']})")
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
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_approval_with_correct_user():
    """Test aprobación con usuario correcto"""
    print("\n✅ TESTING APROBACIÓN CON USUARIO CORRECTO")
    print("=" * 50)
    
    import requests
    
    # Primero verificar qué organización es dueña del evento 27
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT organizacion_origen 
            FROM eventos_red 
            WHERE evento_id = 27
        """)
        
        result = cursor.fetchone()
        if result:
            org_owner = result['organizacion_origen']
            print(f"Evento 27 pertenece a: {org_owner}")
            
            # Buscar usuario admin de esa organización
            cursor.execute("""
                SELECT username, rol
                FROM usuarios 
                WHERE organizacion = %s AND rol IN ('PRESIDENTE', 'COORDINADOR')
                LIMIT 1
            """, (org_owner,))
            
            admin_user = cursor.fetchone()
            if admin_user:
                print(f"Usuario admin encontrado: {admin_user['username']} ({admin_user['rol']})")
                
                # Intentar login
                if org_owner == 'fundacion-esperanza':
                    login_data = {"usernameOrEmail": "admin_fundacion", "password": "admin123"}
                elif org_owner == 'empuje-comunitario':
                    login_data = {"usernameOrEmail": "admin", "password": "admin123"}
                else:
                    login_data = {"usernameOrEmail": admin_user['username'], "password": "admin123"}
                
                response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
                print(f"Login status: {response.status_code}")
                
                if response.status_code == 200:
                    token = response.json().get('token')
                    headers = {'Authorization': f'Bearer {token}'}
                    
                    # Obtener adhesiones para el evento
                    response = requests.post(
                        "http://localhost:3001/api/messaging/event-adhesions",
                        json={"eventId": 27},
                        headers=headers
                    )
                    
                    print(f"Event adhesions status: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        adhesions = data.get('adhesions', [])
                        print(f"Adhesiones encontradas: {len(adhesions)}")
                        
                        for adhesion in adhesions:
                            print(f"  - ID: {adhesion.get('id')}, Estado: {adhesion.get('status')}")
                            print(f"    Voluntario: {adhesion.get('volunteer_name')} {adhesion.get('volunteer_surname')}")
                    else:
                        print(f"Error: {response.text}")
                else:
                    print(f"Error login: {response.text}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔍 DEBUG COMPLETO DE USUARIOS Y ADHESIONES")
    print("=" * 60)
    
    check_users_and_organizations()
    check_current_adhesions()
    test_approval_with_correct_user()