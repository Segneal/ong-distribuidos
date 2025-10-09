#!/usr/bin/env python3
"""
Script para iniciar el consumer de solicitudes de inscripción
"""
import sys
import os
import logging

# Agregar el path del messaging service
sys.path.append(os.path.join(os.path.dirname(__file__), 'messaging-service', 'src'))

def start_consumer():
    """Iniciar el consumer de solicitudes de inscripción"""
    
    print("🚀 INICIANDO CONSUMER DE SOLICITUDES DE INSCRIPCIÓN")
    print("=" * 55)
    
    try:
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Importar y iniciar el consumer
        from messaging.consumers.inscription_request_consumer import start_inscription_consumer
        
        print("✅ Consumer configurado correctamente")
        print("🔄 Esperando mensajes de Kafka...")
        print("   Topics: inscription-requests, inscription-responses")
        print("   Presiona Ctrl+C para detener")
        print("-" * 55)
        
        # Iniciar el consumer
        start_inscription_consumer()
        
    except KeyboardInterrupt:
        print("\n🛑 Consumer detenido por usuario")
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("   Asegúrate de que el messaging service esté configurado correctamente")
    except Exception as e:
        print(f"❌ Error iniciando consumer: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_consumer()