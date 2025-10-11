#!/usr/bin/env python3
"""
Script para probar las rutas de messaging directamente
"""
import requests
import json

def test_messaging_routes():
    """Prueba las rutas de messaging directamente"""
    
    # Configuración
    API_BASE = "http://localhost:3001/api"
    
    try:
        print("=== PROBANDO RUTAS DE MESSAGING DIRECTAMENTE ===\n")
        
        # Crear un token falso para las pruebas (solo para verificar que las rutas respondan)
        # En producción esto no funcionaría, pero nos ayuda a probar la lógica de las rutas
        fake_headers = {
            "Content-Type": "application/json"
        }
        
        # 1. Probar solicitudes activas (sin token, debería dar 401)
        print("1. Probando solicitudes activas (sin token)...")
        active_response = requests.post(f"{API_BASE}/messaging/active-requests", headers=fake_headers)
        print(f"Status: {active_response.status_code}")
        print(f"Response: {active_response.text[:200]}...")
        
        # 2. Probar solicitudes externas (sin token, debería dar 401)
        print("\n2. Probando solicitudes externas (sin token)...")
        external_response = requests.post(f"{API_BASE}/messaging/external-requests", headers=fake_headers)
        print(f"Status: {external_response.status_code}")
        print(f"Response: {external_response.text[:200]}...")
        
        # 3. Verificar que las rutas existen (no deberían dar 404)
        if active_response.status_code == 401 and external_response.status_code == 401:
            print("\n✅ Las rutas existen y requieren autenticación (401), esto es correcto")
            return True
        elif active_response.status_code == 404 or external_response.status_code == 404:
            print("\n❌ Algunas rutas no existen (404)")
            return False
        else:
            print(f"\n⚠ Respuestas inesperadas: {active_response.status_code}, {external_response.status_code}")
            return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está corriendo el API Gateway en el puerto 3001?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    if test_messaging_routes():
        print("\n🎉 Las rutas de messaging están configuradas correctamente!")
    else:
        print("\n❌ Hay problemas con las rutas de messaging")