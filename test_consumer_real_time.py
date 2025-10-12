#!/usr/bin/env python3
"""
Test del consumer en tiempo real
"""
import sys
import time
import threading
sys.path.append('messaging-service/src')

from messaging.consumers.base_consumer import OrganizationConsumer
from messaging.producers.base_producer import BaseProducer

def test_consumer_listening():
    """Test si el consumer está escuchando"""
    print("=== TESTING CONSUMER EN TIEMPO REAL ===")
    
    try:
        # Crear consumer
        consumer = OrganizationConsumer()
        
        print(f"Consumer topics: {consumer.topics}")
        print(f"Consumer running: {consumer.is_running()}")
        
        # Iniciar consumer en thread separado
        def start_consumer():
            print("Iniciando consumer...")
            consumer.start()
        
        consumer_thread = threading.Thread(target=start_consumer)
        consumer_thread.daemon = True
        consumer_thread.start()
        
        # Esperar un poco
        time.sleep(2)
        
        print(f"Consumer running after start: {consumer.is_running()}")
        
        # Enviar mensaje de prueba
        producer = BaseProducer()
        
        test_data = {
            "transfer_id": "consumer-test-123",
            "request_id": "req-test-123", 
            "source_organization": "empuje-comunitario",
            "target_organization": "esperanza-social",
            "donations": [{"test": "consumer data"}],
            "timestamp": "2025-10-12T15:00:00",
            "user_id": 1
        }
        
        print("Enviando mensaje de prueba...")
        success = producer.publish_donation_transfer("esperanza-social", test_data)
        print(f"Mensaje enviado: {success}")
        
        # Esperar procesamiento
        print("Esperando 10 segundos para procesamiento...")
        time.sleep(10)
        
        # Verificar si se procesó
        import mysql.connector
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='ong_management'
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM transferencias_donaciones 
            WHERE solicitud_id = 'req-test-123' AND tipo = 'RECIBIDA'
        """)
        
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        if count > 0:
            print("✅ Consumer procesó el mensaje correctamente")
        else:
            print("❌ Consumer NO procesó el mensaje")
        
        # Detener consumer
        consumer.stop()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_consumer_listening()