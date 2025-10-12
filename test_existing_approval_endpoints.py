#!/usr/bin/env python3
"""
Test de los endpoints de aprobación existentes
"""
import requests

def test_approval_endpoints():
    """Test de endpoints de aprobación"""
    print("✅ TESTING ENDPOINTS DE APROBACIÓN EXISTENTES")
    print("=" * 50)
    
    # Login fundacion-esperanza
    login_data = {"usernameOrEmail": "esperanza_admin", "password": "admin123"}
    response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Error login: {response.text}")
        return
    
    token = response.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Obtener adhesiones pendientes
    response = requests.post(
        "http://localhost:3001/api/messaging/event-adhesions",
        json={"eventId": 27},
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Error obteniendo adhesiones: {response.text}")
        return
    
    adhesions = response.json().get('adhesions', [])
    pending = [a for a in adhesions if a.get('status') == 'PENDIENTE']
    
    print(f"Adhesiones pendientes: {len(pending)}")
    
    if not pending:
        print("⚠️  No hay adhesiones pendientes para test")
        return
    
    # Probar aprobación
    adhesion_to_approve = pending[0]
    print(f"\\nProbando aprobación de adhesión ID: {adhesion_to_approve.get('id')}")
    
    # Test endpoint de aprobación
    approval_data = {"adhesionId": adhesion_to_approve.get('id')}
    
    response = requests.post(
        "http://localhost:3001/api/messaging/approve-event-adhesion",
        json=approval_data,
        headers=headers
    )
    
    print(f"Approve endpoint - Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ ¡ENDPOINT DE APROBACIÓN FUNCIONA!")
        
        # Verificar que el estado cambió
        response = requests.post(
            "http://localhost:3001/api/messaging/event-adhesions",
            json={"eventId": 27},
            headers=headers
        )
        
        if response.status_code == 200:
            updated_adhesions = response.json().get('adhesions', [])
            updated_adhesion = next((a for a in updated_adhesions if a.get('id') == adhesion_to_approve.get('id')), None)
            
            if updated_adhesion and updated_adhesion.get('status') == 'CONFIRMADA':
                print("✅ Estado actualizado correctamente")
            else:
                print(f"⚠️  Estado no actualizado: {updated_adhesion.get('status') if updated_adhesion else 'No encontrado'}")
    else:
        print("❌ Error en endpoint de aprobación")
        
        # Si hay error, probar rechazo con otra adhesión
        if len(pending) > 1:
            print("\\nProbando rechazo con otra adhesión...")
            
            adhesion_to_reject = pending[1]
            rejection_data = {
                "adhesionId": adhesion_to_reject.get('id'),
                "reason": "Test de rechazo"
            }
            
            response = requests.post(
                "http://localhost:3001/api/messaging/reject-event-adhesion",
                json=rejection_data,
                headers=headers
            )
            
            print(f"Reject endpoint - Status: {response.status_code}")
            print(f"Response: {response.text}")

if __name__ == "__main__":
    print("🔧 TEST DE ENDPOINTS DE APROBACIÓN EXISTENTES")
    print("=" * 60)
    
    test_approval_endpoints()