#!/usr/bin/env python3
"""
Test completo del flujo de adhesiones entre organizaciones
"""
import os
import sys
import json
import time
import threading
from datetime import datetime

# Add messaging service to path
sys.path.append('messaging-service/src')

def test_adhesion_flow():
    """Test complete adhesion flow between organizations"""
    print("=== TESTING COMPLETE ADHESION FLOW ===")
    
    # Set environment for empuje-comunitario (sender)
    os.environ['KAFKA_BROKERS'] = 'localhost:9092'
    os.environ['ORGANIZATION_ID'] = 'empuje-comunitario'
    
    from messaging.config import settings, Topics
    from messaging.producers.base_producer import BaseProducer
    
    print(f"Sender Organization: {settings.organization_id}")
    
    # Step 1: Send adhesion message from empuje-comunitario to esperanza-viva
    print("\n1. Sending adhesion message...")
    
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
    
    # Step 2: Manually consume message as esperanza-viva
    print("\n2. Consuming message as esperanza-viva...")
    
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
            consumer_timeout_ms=10000  # 10 second timeout
        )
        
        print("Waiting for messages...")
        message_found = False
        
        for message in consumer:
            print(f"Received message:")
            print(f"  Topic: {message.topic}")
            print(f"  Partition: {message.partition}")
            print(f"  Offset: {message.offset}")
            print(f"  Value: {json.dumps(message.value, indent=2)}")
            
            # Process the message
            message_data = message.value.get('data', {})
            if message_data.get('type') == 'event_adhesion':
                print("✅ Event adhesion message received!")
                
                # Test processing
                volunteer = message_data.get('volunteer', {})
                print(f"Volunteer: {volunteer.get('name')} {volunteer.get('surname')}")
                print(f"Email: {volunteer.get('email')}")
                print(f"Organization: {volunteer.get('organization_id')}")
                print(f"Event ID: {message_data.get('event_id')}")
                
                message_found = True
                break
        
        consumer.close()
        
        if not message_found:
            print("❌ No adhesion message found")
            return False
        
        # Step 3: Test processing with AdhesionService
        print("\n3. Testing AdhesionService processing...")
        
        # Change organization to esperanza-viva for processing
        os.environ['ORGANIZATION_ID'] = 'esperanza-viva'
        
        # Reload settings
        from messaging.config import Settings
        esperanza_settings = Settings()
        print(f"Processor Organization: {esperanza_settings.organization_id}")
        
        from messaging.services.adhesion_service import AdhesionService
        
        adhesion_service = AdhesionService()
        
        # Process the message
        success = adhesion_service.process_incoming_adhesion(message_data)
        
        if success:
            print("✅ Adhesion processed successfully!")
        else:
            print("❌ Failed to process adhesion")
            return False
        
        print("\n✅ Complete adhesion flow test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Error in adhesion flow test: {e}")
        return False

def test_consumer_integration():
    """Test the actual consumer integration"""
    print("\n=== TESTING CONSUMER INTEGRATION ===")
    
    # Set environment for esperanza-viva (receiver)
    os.environ['ORGANIZATION_ID'] = 'esperanza-viva'
    os.environ['KAFKA_BROKERS'] = 'localhost:9092'
    
    from messaging.config import Settings
    esperanza_settings = Settings()
    
    from messaging.consumers.adhesion_consumer import AdhesionConsumer
    
    print(f"Consumer Organization: {esperanza_settings.organization_id}")
    
    # Create consumer
    consumer = AdhesionConsumer()
    print(f"Consumer topic: {consumer.topic}")
    
    # Start consumer in background
    consumer_thread = threading.Thread(target=consumer.start)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    print("Consumer started, waiting for processing...")
    time.sleep(5)
    
    # Send a test message from empuje-comunitario
    os.environ['ORGANIZATION_ID'] = 'empuje-comunitario'
    
    from messaging.config import Settings
    empuje_settings = Settings()
    from messaging.producers.base_producer import BaseProducer
    
    producer = BaseProducer()
    
    test_volunteer_data = {
        "volunteer_id": 456,
        "name": "María",
        "surname": "González",
        "email": "maria.gonzalez@empuje.org",
        "phone": "987654321"
    }
    
    print(f"Sending message from {empuje_settings.organization_id}...")
    
    success = producer.publish_event_adhesion(
        target_org="esperanza-viva",
        event_id="test-event-002",
        volunteer_data=test_volunteer_data
    )
    
    print(f"Message sent: {success}")
    
    # Wait for processing
    time.sleep(10)
    
    # Stop consumer
    consumer.stop()
    
    print("Consumer integration test completed")

def main():
    """Main test function"""
    print("Starting complete adhesion flow test...")
    
    # Test 1: Complete flow
    success1 = test_adhesion_flow()
    
    # Test 2: Consumer integration
    test_consumer_integration()
    
    if success1:
        print("\n🎉 All tests PASSED!")
    else:
        print("\n❌ Some tests FAILED!")

if __name__ == "__main__":
    main()