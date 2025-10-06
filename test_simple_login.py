#!/usr/bin/env python3
"""
Test simple de login
"""
import requests
import json

def test_login():
    """Test simple de login"""
    
    print("🔐 PROBANDO LOGIN...")
    
    login_data = {
        "usernameOrEmail": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(
            "http://localhost:3001/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        
        if login_response.status_code == 200:
            data = login_response.json()
            print(f"✅ Login exitoso!")
            print(f"Token: {data.get('token', 'N/A')[:20]}...")
            print(f"User: {data.get('user', {})}")
        else:
            print(f"❌ Login falló")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al API Gateway en puerto 3001")
        print("¿Está corriendo el API Gateway?")
    except requests.exceptions.Timeout:
        print("❌ Timeout conectando al API Gateway")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()