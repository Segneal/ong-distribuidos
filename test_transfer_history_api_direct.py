#!/usr/bin/env python3
"""
Test directo del API de historial de transferencias para verificar filtrado por organización
"""

import requests
import json
import sys

def test_transfer_history_filtering():
    print("🔍 TESTING TRANSFER HISTORY API FILTERING")
    print("=" * 60)
    
    # URLs del API
    login_url = "http://localhost:3001/api/auth/login"
    transfer_history_url = "http://localhost:3001/api/messaging/transfer-history"
    
    # Credenciales de prueba
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
    
    for user in users:
        print(f"\n--- Testing user: {user['name']} ---")
        
        try:
            # 1. Login
            login_response = requests.post(login_url, json=user["credentials"])
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                continue
                
            login_data = login_response.json()
            token = login_data.get("token")
            
            if not token:
                print("❌ No token received")
                continue
                
            print(f"✅ Login successful")
            print(f"   Organization: {login_data.get('user', {}).get('organization', 'N/A')}")
            
            # 2. Get transfer history
            headers = {"Authorization": f"Bearer {token}"}
            history_response = requests.post(transfer_history_url, headers=headers)
            
            if history_response.status_code != 200:
                print(f"❌ Transfer history failed: {history_response.status_code}")
                print(f"   Response: {history_response.text}")
                continue
                
            history_data = history_response.json()
            transfers = history_data.get("transfers", [])
            
            print(f"✅ Transfer history retrieved")
            print(f"   Total transfers: {len(transfers)}")
            
            # 3. Verificar que todas las transferencias pertenecen a la organización correcta
            if transfers:
                print("   📋 Transfers found:")
                for i, transfer in enumerate(transfers[:5]):  # Mostrar solo las primeras 5
                    org_prop = transfer.get("organizacion_propietaria", "N/A")
                    tipo = transfer.get("tipo", "N/A")
                    contraparte = transfer.get("organizacion_contraparte", "N/A")
                    fecha = transfer.get("fecha_transferencia", "N/A")
                    
                    print(f"   {i+1}. {tipo} - {contraparte} - {fecha}")
                    print(f"      Propietaria: {org_prop}")
                    
                    # Verificar filtrado
                    if org_prop != user["expected_org"]:
                        print(f"   ❌ ERROR: Transfer belongs to {org_prop}, expected {user['expected_org']}")
                    else:
                        print(f"   ✅ Correct organization filter")
                        
                if len(transfers) > 5:
                    print(f"   ... and {len(transfers) - 5} more transfers")
            else:
                print("   📭 No transfers found")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error - API Gateway not running on localhost:3001")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print("✅ Test completed - check results above")
    print("🔄 If seeing wrong organization transfers:")
    print("   1. API Gateway may need restart to load new code")
    print("   2. Check if messaging.js has the correct WHERE clause")
    print("   3. Verify database has organizacion_propietaria field")

if __name__ == "__main__":
    test_transfer_history_filtering()