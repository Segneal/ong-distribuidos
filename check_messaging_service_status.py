#!/usr/bin/env python3
"""
Verificar el estado del messaging service
"""

import requests
import json

def check_messaging_service():
    print("🔍 CHECKING MESSAGING SERVICE STATUS")
    print("=" * 50)
    
    # URLs a probar
    urls = [
        "http://localhost:50054/health",
        "http://localhost:50054/api/health",
        "http://localhost:50054/",
        "http://localhost:50054/api/transferDonations"
    ]
    
    for url in urls:
        try:
            print(f"\n📡 Probando: {url}")
            response = requests.get(url, timeout=3)
            print(f"   ✅ Status: {response.status_code}")
            if response.text:
                print(f"   📄 Response: {response.text[:200]}...")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection refused - Service not running")
        except requests.exceptions.Timeout:
            print(f"   ⏳ Timeout - Service not responding")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Probar POST a transferDonations
    print(f"\n📤 Probando POST a transferDonations...")
    try:
        test_data = {
            "targetOrganization": "test",
            "requestId": "test",
            "donations": [],
            "userId": 1
        }
        response = requests.post("http://localhost:50054/api/transferDonations", 
                               json=test_data, timeout=3)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📄 Response: {response.text[:200]}...")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection refused - Service not running")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("📋 RESULTADO")
    print("=" * 50)
    print("Si todas las conexiones fallan:")
    print("1. 🔄 El messaging service NO está corriendo")
    print("2. 🚀 Inicia el messaging service:")
    print("   cd messaging-service")
    print("   python src/main.py")

if __name__ == "__main__":
    check_messaging_service()