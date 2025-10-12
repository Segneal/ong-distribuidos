#!/usr/bin/env python3
"""
Test real del flujo de adhesiones
Simula el comportamiento real donde cada organización tiene su propia instancia del servicio
"""
import os
import sys
import json
import time
import subprocess
import threading
from datetime import datetime

# Add messaging service to path
sys.path.append('messaging-service/src')

def test_real_adhesion_flow():
    """Test real adhesion flow with proper organization separation"""
    print("=== TESTING REAL ADHESION FLOW ===")
    
    # Set up Kafka connection
    os.environ['KAFKA_BROKERS'] = 'localhost:9092'
    
    # Step 1: Send adhesion from empuje-comunitario to esperanza-viva
    print("\n1. Sending adhesion from empuje-comunitario to esperanza-viva...")
    
    os.environ['ORGANIZATION_ID'] = 'empuje-comunitario'
    
    from messaging.config import settings, Topics
    from messaging.producers.base_producer import BaseProducer
    
    print(f"Sender: {settings.organization_id}")
    
    producer = BaseProducer()
    
    test_volunteer_data = {
        "volunteer_id": 123,
        "name": "Juan",
        "surname": "Pérez",
        "email": "juan.perez@empuje.org",
        "phone": "123456789"
    }
    
    success = producer.publish_event_adhesion(
        target_org="esperanza-viva",
        event_id="test-event-001",
        volunteer_data=test_volunteer_data
    )
    
    print(f"Message sent: {success}")
    
    if not success:
        print("❌ Failed to send message")
        return False
    
    # Step 2: Manually consume and process the message as esperanza-viva would
    print("\n2. Processing message as esperanza-viva...")
    
    try:
        from kafka import KafkaConsumer
        
        topic = Topics.get_adhesion_topic("esperanza-viva")
        print(f"Consuming from topic: {topic}")
        
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=['localhost:9092'],
            group_id='test-esperanza-consumer',
            auto_offset_reset='earliest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
            consumer_timeout_ms=10000
        )
        
        message_found = False
        
        for message in consumer:
            if message.value and message.value.get('data', {}).get('type') == 'event_adhesion':
                print("✅ Adhesion message received!")
                
                message_data = message.value.get('data', {})
                volunteer = message_data.get('volunteer', {})
                
                print(f"Event ID: {message_data.get('event_id')}")
                print(f"Volunteer: {volunteer.get('name')} {volunteer.get('surname')}")
                print(f"Email: {volunteer.get('email')}")
                print(f"From Organization: {volunteer.get('organization_id')}")
                
                # Now process this message as esperanza-viva would
                print("\n3. Processing adhesion with AdhesionService...")
                
                # Change environment to esperanza-viva for processing
                original_org = os.environ.get('ORGANIZATION_ID')
                os.environ['ORGANIZATION_ID'] = 'esperanza-viva'
                
                # Import fresh modules with new organization
                import importlib
                import messaging.config
                importlib.reload(messaging.config)
                
                from messaging.services.adhesion_service import AdhesionService
                
                print(f"Processing as: {messaging.config.settings.organization_id}")
                
                adhesion_service = AdhesionService()
                
                # Process the incoming adhesion
                success = adhesion_service.process_incoming_adhesion(message_data)
                
                if success:
                    print("✅ Adhesion processed successfully!")
                    
                    # Check if notification was created
                    print("\n4. Checking notifications...")
                    
                    from messaging.services.notification_service import NotificationService
                    notification_service = NotificationService()
                    
                    # This would normally be called by the adhesion service
                    volunteer_name = f"{volunteer.get('name', '')} {volunteer.get('surname', '')}".strip()
                    volunteer_email = volunteer.get('email', '')
                    volunteer_org = volunteer.get('organization_id', '')
                    event_id = message_data.get('event_id', '')
                    
                    notification_service.notify_new_event_adhesion(
                        event_id, volunteer_name, volunteer_email, volunteer_org
                    )
                    
                    print("✅ Notification sent!")
                    
                else:
                    print("❌ Failed to process adhesion")
                
                # Restore original organization
                os.environ['ORGANIZATION_ID'] = original_org
                
                message_found = True
                break
        
        consumer.close()
        
        if not message_found:
            print("❌ No adhesion message found")
            return False
        
        print("\n✅ Complete adhesion flow test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Error in adhesion flow test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_notification_system():
    """Test the notification system separately"""
    print("\n=== TESTING NOTIFICATION SYSTEM ===")
    
    os.environ['ORGANIZATION_ID'] = 'esperanza-viva'
    os.environ['KAFKA_BROKERS'] = 'localhost:9092'
    
    try:
        from messaging.services.notification_service import NotificationService
        
        notification_service = NotificationService()
        
        # Test creating a notification
        notification_service.notify_new_event_adhesion(
            event_id="test-event-001",
            volunteer_name="Juan Pérez",
            volunteer_email="juan.perez@empuje.org",
            volunteer_org="empuje-comunitario"
        )
        
        print("✅ Notification created successfully!")
        
        # Check if notification was stored
        from messaging.database.connection import get_database_connection
        
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM notificaciones 
                WHERE tipo = 'nueva_adhesion_evento' 
                ORDER BY fecha_creacion DESC 
                LIMIT 1
            """)
            
            notification = cursor.fetchone()
            
            if notification:
                print("✅ Notification found in database!")
                print(f"Notification ID: {notification[0]}")
                print(f"Type: {notification[2]}")
                print(f"Message: {notification[3]}")
            else:
                print("❌ Notification not found in database")
        
    except Exception as e:
        print(f"❌ Error testing notification system: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("Starting real adhesion flow test...")
    
    # Test 1: Complete adhesion flow
    success = test_real_adhesion_flow()
    
    # Test 2: Notification system
    test_notification_system()
    
    if success:
        print("\n🎉 Real adhesion flow test PASSED!")
    else:
        print("\n❌ Real adhesion flow test FAILED!")

if __name__ == "__main__":
    main()