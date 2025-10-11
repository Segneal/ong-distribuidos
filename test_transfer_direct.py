#!/usr/bin/env python3
"""
Script para probar la transferencia directamente contra el messaging-service
"""
import requests
import json

def test_transfer_direct():
    """Prueba la transferencia directamente contra el messaging-service"""
    
    # Configuración
    MESSAGING_URL = "http://localhost:50054"
    
    try:
        print("=== PROBANDO TRANSFERENCIA DIRECTA ===\n")
        
        # Datos de transferencia de prueba
        transfer_data = {
            "targetOrganization": "empuje-comunitario",
            "requestId": "req-empuje-comunitario-0645517b",
            "donations": [
                {
                    "category": "JUGUETES",
                    "description": "Juguetes navideños",
                    "quantity": "1",
                    "inventoryId": 26
                }
            ],
            "userId": 17
        }
        
        print("1. Datos de transferencia:")
        print(json.dumps(transfer_data, indent=2))
        
        # Realizar transferencia
        print("\n2. Realizando transferencia...")
        transfer_response = requests.post(
            f"{MESSAGING_URL}/api/transferDonations",
            json=transfer_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {transfer_response.status_code}")
        print(f"Response: {transfer_response.text}")
        
        if transfer_response.status_code == 200:
            print("✅ Transferencia exitosa!")
        else:
            print(f"❌ Error en transferencia: {transfer_response.status_code}")
            
            # Intentar parsear el error
            try:
                error_data = transfer_response.json()
                print(f"Error detail: {error_data}")
            except:
                print("No se pudo parsear el error JSON")
        
        return transfer_response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está corriendo el messaging-service?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    if test_transfer_direct():
        print("\n🎉 Prueba directa de transferencia completada!")
    else:
        print("\n❌ Prueba directa de transferencia falló")