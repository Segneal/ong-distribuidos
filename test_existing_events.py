#!/usr/bin/env python3
"""
Test con eventos existentes
"""
import requests
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ong_management'
}

def get_token(org='empuje-comunitario'):
    """Obtener token"""
    if org == 'empuje-comunitario':
        login_data = {"usernameOrEmail": "admin", "password": "admin123"}
    else:
        login_data = {"usernameOrEmail": "admin_esperanza", "password": "admin123"}
    
    response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json().get('token'), response.json().get('user')
    return None, None

def check_existing_events():
    """Verificar eventos existentes"""
    print("📅 VERIFICANDO EVENTOS EXISTENTES")
    print("=" * 40)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Eventos de empuje-comunitario
        cursor.execute("""
            SELECT id, nombre, descripcion, fecha_evento, expuesto_red 
            FROM eventos 
            WHERE organizacion = 'empuje-comunitario'
            ORDER BY fecha_evento DESC
            LIMIT 5
        """)
        
        eventos_empuje = cursor.fetchall()
        print(f"Eventos de empuje-comunitario: {len(eventos_empuje)}")
        
        for evento in eventos_empuje:
            print(f"  - ID: {evento['id']}, Nombre: {evento['nombre']}, Expuesto: {evento['expuesto_red']}")
        
        # Eventos en la red
        cursor.execute("""
            SELECT evento_id, nombre, organizacion_origen, activo
            FROM eventos_red 
            WHERE activo = true
            ORDER BY fecha_publicacion DESC
            LIMIT 5
        """)
        
        eventos_red = cursor.fetchall()
        print(f"\nEventos en la red: {len(eventos_red)}")
        
        for evento in eventos_red:
            print(f"  - ID: {evento['evento_id']}, Nombre: {evento['nombre']}, Org: {evento['organizacion_origen']}")
        
        cursor.close()
        conn.close()
        
        return eventos_empuje, eventos_red
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return [], []

def test_adhesion_to_existing_event():
    """Test adhesión a evento existente"""
    print("\n👤 TESTING ADHESIÓN A EVENTO EXISTENTE")
    print("=" * 50)
    
    # Obtener eventos en la red
    _, eventos_red = check_existing_events()
    
    if not eventos_red:
        print("❌ No hay eventos en la red para test")
        return
    
    # Usar el primer evento
    evento = eventos_red[0]
    event_id = evento['evento_id']
    
    print(f"Usando evento: {evento['nombre']} (ID: {event_id})")
    
    # Login esperanza-social
    token_esperanza, user_esperanza = get_token('esperanza-social')
    headers = {'Authorization': f'Bearer {token_esperanza}'}
    
    # Crear adhesión
    adhesion_data = {
        "eventId": event_id,
        "targetOrganization": evento['organizacion_origen'],
        "volunteerData": {
            "nombre": "Test Volunteer Complete",
            "email": "test.complete@example.com",
            "telefono": "987654321",
            "experiencia": "Experiencia completa de test"
        }
    }
    
    response = requests.post(
        "http://localhost:3001/api/messaging/create-event-adhesion",
        json=adhesion_data,
        headers=headers
    )
    
    print(f"Status adhesión: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Adhesión creada exitosamente")
        
        # Verificar adhesiones para el evento
        token_org, _ = get_token(evento['organizacion_origen'])
        headers_org = {'Authorization': f'Bearer {token_org}'}
        
        response = requests.post(
            "http://localhost:3001/api/messaging/event-adhesions",
            json={"eventId": event_id},
            headers=headers_org
        )
        
        print(f"\nVerificando adhesiones - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            adhesions = data.get('adhesions', [])
            print(f"Adhesiones totales: {len(adhesions)}")
            
            pending = [a for a in adhesions if a.get('status') == 'PENDIENTE']
            print(f"Adhesiones pendientes: {len(pending)}")
            
            if pending:
                print("✅ Sistema de adhesiones funcionando")
                return True
            else:
                print("⚠️  No hay adhesiones pendientes")
        else:
            print(f"❌ Error verificando adhesiones: {response.text}")
    else:
        print("❌ Error creando adhesión")
    
    return False

if __name__ == "__main__":
    print("🔍 TEST CON EVENTOS EXISTENTES")
    print("=" * 50)
    
    check_existing_events()
    test_adhesion_to_existing_event()