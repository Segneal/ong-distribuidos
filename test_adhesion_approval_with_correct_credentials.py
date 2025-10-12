#!/usr/bin/env python3
"""
Test de aprobación de adhesiones con credenciales correctas
"""
import requests
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def test_fundacion_login():
    """Test login fundacion-esperanza"""
    print("🔑 TESTING LOGIN FUNDACION-ESPERANZA")
    print("=" * 40)
    
    # Intentar con usuarios conocidos
    login_attempts = [
        {"usernameOrEmail": "esperanza_admin", "password": "admin123"},
        {"usernameOrEmail": "esperanza_coord", "password": "admin123"},
        {"usernameOrEmail": "maria@esperanza.org", "password": "admin123"},
        {"usernameOrEmail": "carlos@esperanza.org", "password": "admin123"}
    ]
    
    for attempt in login_attempts:
        response = requests.post("http://localhost:3001/api/auth/login", json=attempt)
        
        print(f"Login {attempt['usernameOrEmail']}: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json().get('user', {})
            print(f"✅ Login exitoso!")
            print(f"   Usuario: {user_data.get('username')}")
            print(f"   Organización: {user_data.get('organization')}")
            print(f"   Rol: {user_data.get('role')}")
            return response.json().get('token'), user_data
        else:
            print(f"   Error: {response.text}")
    
    return None, None

def test_adhesion_approval_complete():
    """Test completo de aprobación de adhesiones"""
    print("\\n✅ TESTING APROBACIÓN COMPLETA DE ADHESIONES")
    print("=" * 50)
    
    # 1. Login fundacion-esperanza
    token, user = test_fundacion_login()
    
    if not token:
        print("❌ No se pudo hacer login a fundacion-esperanza")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. Obtener adhesiones para evento de fundacion-esperanza
    # Evento 27 pertenece a fundacion-esperanza
    response = requests.post(
        "http://localhost:3001/api/messaging/event-adhesions",
        json={"eventId": 27},
        headers=headers
    )
    
    print(f"\\nEvent adhesions API - Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        adhesions = data.get('adhesions', [])
        print(f"Adhesiones encontradas: {len(adhesions)}")
        
        for adhesion in adhesions:
            print(f"  - ID: {adhesion.get('id')}")
            print(f"    Estado: {adhesion.get('status')}")
            print(f"    Voluntario: {adhesion.get('volunteer_name')} {adhesion.get('volunteer_surname')}")
            print(f"    Email: {adhesion.get('volunteer_email')}")
        
        # 3. Buscar adhesiones pendientes
        pending = [a for a in adhesions if a.get('status') == 'PENDIENTE']
        print(f"\\nAdhesiones pendientes: {len(pending)}")
        
        if pending:
            # 4. Intentar aprobar la primera adhesión pendiente
            adhesion_to_approve = pending[0]
            print(f"\\nIntentando aprobar adhesión ID: {adhesion_to_approve.get('id')}")
            
            # Probar diferentes endpoints de aprobación
            approval_endpoints = [
                {
                    "url": "/api/messaging/approve-adhesion",
                    "data": {
                        "adhesionId": adhesion_to_approve.get('id'),
                        "action": "approve"
                    }
                },
                {
                    "url": "/api/messaging/update-adhesion-status", 
                    "data": {
                        "adhesionId": adhesion_to_approve.get('id'),
                        "status": "CONFIRMADA"
                    }
                },
                {
                    "url": "/api/events/approve-adhesion",
                    "data": {
                        "adhesionId": adhesion_to_approve.get('id'),
                        "approved": True
                    }
                }
            ]
            
            approval_success = False
            
            for endpoint in approval_endpoints:
                response = requests.post(
                    f"http://localhost:3001{endpoint['url']}",
                    json=endpoint['data'],
                    headers=headers
                )
                
                print(f"  {endpoint['url']}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"    ✅ Aprobación exitosa: {response.text}")
                    approval_success = True
                    break
                elif response.status_code == 404:
                    print(f"    ❌ Endpoint no existe")
                else:
                    print(f"    ⚠️  Error: {response.text}")
            
            if not approval_success:
                print("\\n❌ NINGÚN ENDPOINT DE APROBACIÓN FUNCIONA")
                print("🔧 Esto indica que falta implementar el endpoint de aprobación")
                
                # 5. Aprobar directamente en la base de datos como workaround
                print("\\n💾 Aprobando directamente en base de datos...")
                
                try:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        UPDATE adhesiones_eventos_externos 
                        SET estado = 'CONFIRMADA', fecha_aprobacion = NOW()
                        WHERE id = %s
                    """, (adhesion_to_approve.get('id'),))
                    
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    print(f"✅ Adhesión {adhesion_to_approve.get('id')} aprobada directamente en DB")
                    
                    # Verificar el cambio
                    response = requests.post(
                        "http://localhost:3001/api/messaging/event-adhesions",
                        json={"eventId": 27},
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        updated_adhesions = response.json().get('adhesions', [])
                        updated_adhesion = next((a for a in updated_adhesions if a.get('id') == adhesion_to_approve.get('id')), None)
                        
                        if updated_adhesion and updated_adhesion.get('status') == 'CONFIRMADA':
                            print("✅ Cambio confirmado en API")
                        else:
                            print("⚠️  Cambio no reflejado en API")
                    
                except Exception as e:
                    print(f"❌ Error actualizando DB: {e}")
            else:
                print("\\n✅ SISTEMA DE APROBACIÓN FUNCIONANDO")
        else:
            print("⚠️  No hay adhesiones pendientes para aprobar")
    else:
        print(f"❌ Error obteniendo adhesiones: {response.text}")

if __name__ == "__main__":
    print("🔧 TEST COMPLETO DE APROBACIÓN CON CREDENCIALES CORRECTAS")
    print("=" * 60)
    
    test_adhesion_approval_complete()