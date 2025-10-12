#!/usr/bin/env python3
"""
Test del formato correcto para crear eventos
"""
import requests
import time

def get_token():
    """Obtener token"""
    login_data = {"usernameOrEmail": "admin", "password": "admin123"}
    response = requests.post("http://localhost:3001/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json().get('token')
    return None

def test_event_formats():
    """Test diferentes formatos de evento"""
    print("📅 TESTING FORMATOS DE EVENTO")
    print("=" * 40)
    
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    # Formato 1: Con fecha separada
    event_data_1 = {
        "name": f"Test Event Format 1 {int(time.time())}",
        "description": "Test description",
        "date": "2025-12-25",
        "time": "10:00",
        "location": "Test Location",
        "maxParticipants": 10,
        "category": "SOCIAL"
    }
    
    print("Formato 1 (date + time separados):")
    response = requests.post(
        "http://localhost:3001/api/events",
        json=event_data_1,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Formato 2: Con fecha completa
    event_data_2 = {
        "name": f"Test Event Format 2 {int(time.time())}",
        "description": "Test description",
        "fecha_evento": "2025-12-25 10:00:00",
        "location": "Test Location",
        "maxParticipants": 10,
        "category": "SOCIAL"
    }
    
    print("\nFormato 2 (fecha_evento completa):")
    response = requests.post(
        "http://localhost:3001/api/events",
        json=event_data_2,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Formato 3: Campos mínimos
    event_data_3 = {
        "nombre": f"Test Event Format 3 {int(time.time())}",
        "descripcion": "Test description",
        "fecha_evento": "2025-12-25",
        "ubicacion": "Test Location"
    }
    
    print("\nFormato 3 (campos en español):")
    response = requests.post(
        "http://localhost:3001/api/events",
        json=event_data_3,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_event_formats()