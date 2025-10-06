#!/usr/bin/env python3
"""
Script para verificar la configuración del messaging service
"""
import requests
import json

def check_messaging_config():
    """Verificar la configuración del messaging service"""
    
    print("🔍 VERIFICANDO CONFIGURACIÓN DEL MESSAGING SERVICE")
    print("=" * 55)
    
    try:
        # Verificar que el servicio esté corriendo
        health_response = requests.get("http://localhost:50054/health")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Messaging service está corriendo")
            print(f"   Status: {health_data.get('status')}")
        else:
            print(f"❌ Messaging service no responde correctamente: {health_response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error conectando al messaging service: {e}")
        print(f"   ¿Está corriendo en puerto 50054?")
        return
    
    # Probar crear una solicitud simple para ver el error específico
    print(f"\n🧪 PROBANDO CREACIÓN DE SOLICITUD SIMPLE:")
    
    test_data = {
        "donations": [
            {
                "categoria": "ALIMENTOS",
                "descripcion": "Test",
                "cantidad": 1
            }
        ],
        "userId": 1,
        "notes": "Test de configuración"
    }
    
    try:
        response = requests.post("http://localhost:50054/api/createDonationRequest", json=test_data)
        
        print(f"📨 Respuesta del messaging service:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Solicitud creada exitosamente")
            print(f"   Request ID: {result.get('request_id')}")
        else:
            try:
                error_data = response.json()
                print(f"❌ Error: {error_data}")
                
                # Analizar el tipo de error
                error_detail = error_data.get('detail', '')
                if 'Access denied' in error_detail:
                    print(f"\n🔐 PROBLEMA DE CREDENCIALES DETECTADO:")
                    print(f"   El messaging service está usando credenciales incorrectas")
                    print(f"   Error: {error_detail}")
                    print(f"\n💡 SOLUCIÓN:")
                    print(f"   1. Detener el messaging service actual (Ctrl+C)")
                    print(f"   2. Reiniciar con: python start_messaging_local.py")
                elif 'cursor' in error_detail:
                    print(f"\n🔧 PROBLEMA DE CONTEXT MANAGER:")
                    print(f"   El código no está actualizado")
                else:
                    print(f"\n❓ OTRO ERROR:")
                    print(f"   {error_detail}")
                    
            except:
                print(f"   Error Text: {response.text}")
                
    except Exception as e:
        print(f"❌ Error probando messaging service: {e}")
    
    print(f"\n🎯 RECOMENDACIÓN:")
    print(f"   El messaging service necesita reiniciarse con la configuración local correcta")
    print(f"   Comando: python start_messaging_local.py")

if __name__ == "__main__":
    check_messaging_config()