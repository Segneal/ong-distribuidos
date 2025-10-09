#!/usr/bin/env python3
"""
Script para probar el RequestService directamente
"""
import sys
import os
from pathlib import Path

def test_request_service_direct():
    """Probar el RequestService directamente"""
    
    print("🧪 TESTING REQUEST SERVICE DIRECTAMENTE")
    print("=" * 45)
    
    # Configurar variables de entorno desde .env.local
    env_file = Path(__file__).parent / 'messaging-service' / '.env.local'
    
    if env_file.exists():
        print(f"📄 Cargando configuración desde: {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    # Agregar paths necesarios
    sys.path.append(os.path.join(os.path.dirname(__file__), 'messaging-service', 'src'))
    
    try:
        # Importar el servicio
        from messaging.services.request_service import RequestService
        print("✅ RequestService importado correctamente")
        
        # Crear instancia del servicio
        request_service = RequestService()
        print("✅ RequestService instanciado correctamente")
        
        # Probar con datos en español
        donations_spanish = [
            {
                "categoria": "ALIMENTOS",
                "descripcion": "Arroz y fideos",
                "cantidad": 50
            },
            {
                "categoria": "ROPA", 
                "descripcion": "Abrigos de invierno",
                "cantidad": 20
            }
        ]
        
        print(f"\n📋 PROBANDO CON DATOS EN ESPAÑOL:")
        print(f"   Donaciones: {donations_spanish}")
        
        success, message, request_id = request_service.create_donation_request(
            donations=donations_spanish,
            user_id=1,
            notes="Prueba directa del servicio"
        )
        
        if success:
            print(f"✅ Solicitud creada exitosamente")
            print(f"   Request ID: {request_id}")
            print(f"   Mensaje: {message}")
        else:
            print(f"❌ Error creando solicitud: {message}")
        
        # Probar con datos en inglés
        donations_english = [
            {
                "category": "FOOD",
                "description": "Rice and pasta",
                "quantity": 50
            }
        ]
        
        print(f"\n📋 PROBANDO CON DATOS EN INGLÉS:")
        print(f"   Donaciones: {donations_english}")
        
        success2, message2, request_id2 = request_service.create_donation_request(
            donations=donations_english,
            user_id=1,
            notes="Prueba directa con formato inglés"
        )
        
        if success2:
            print(f"✅ Solicitud creada exitosamente")
            print(f"   Request ID: {request_id2}")
            print(f"   Mensaje: {message2}")
        else:
            print(f"❌ Error creando solicitud: {message2}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_request_service_direct()