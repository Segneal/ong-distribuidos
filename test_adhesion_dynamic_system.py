#!/usr/bin/env python3
"""
Test del sistema dinámico de adhesiones
Verifica que las organizaciones puedan enviar y recibir adhesiones dinámicamente
"""
import os
import sys
import json
import time
import threading
from datetime import datetime

# Add messaging service to path
sys.path.append('messaging-service/src')

def test_dynamic_adhesion_system():
    """Test the dynamic adhesion system between multiple organizations"""
    print("=== TESTING DYNAMIC ADHESION SYSTEM ===")
    
    # Set up Kafka connection
    os.environ['KAFKA_BROKERS'] = 'localhost:9092'
    
    # Test organizations
    organizations = ['empuje-comunitario', 'esperanza-viva', 'manos-solidarias']
    
    print(f"Testing with organizations: {organizations}")
    
    # Step 1: Test message sending from each organization to others
    print("\n1. Testing message sending between organizations...")
    
    for sender_org in organizations:
        for receiver_org in organizations:
            if sender_org != receiver_org:
                print(f"\n  Testing: {sender_org} -> {receiver_org}")
                
                # Set sender organization
                os.environ['ORGANIZATION_ID'] = sender_org
                
                from messaging.config import Settings, Topics
                from messaging.producers.base_producer import BaseProducer
                
                # Reload settings
                sender_settings = Settings()
                producer = BaseProducer()
                
                # Create test volunteer data
                test_volunteer_data = {
                    "volunteer_id": 123,
                    "name": "Test",
                    "surname": "Volunteer",
                    "email": f"test@{sender_org}.org",
                    "phone": "123456789"
                }
                
                # Send adhesion message
                success = producer.publish_event_adhesion(
                    target_org=receiver_org,
                    event_id=f"test-event-{receiver_org}",
                    volunteer_data=test_volunteer_data
                )
                
                print(f"    Message sent: {success}")
                
                if success:
                    # Verify message in receiver's topic
                    receiver_topic = Topics.get_adhesion_topic(receiver_org)
                    print(f"    Target topic: {receiver_topic}")
                    
                    # Quick check if message exists
                    try:
                        from kafka import KafkaConsumer
                        
                        consumer = KafkaConsumer(
                            receiver_topic,
                            bootstrap_servers=['localhost:9092'],
                            group_id=f'test-{receiver_org}-consumer',
                            auto_offset_reset='latest',
                            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
                            consumer_timeout_ms=2000
                        )
                        
                        message_found = False
                        for message in consumer:
                            if message.value and message.value.get('data', {}).get('type') == 'event_adhesion':
                                message_found = True
                                break
                        
                        consumer.close()
                        print(f"    Message received: {message_found}")
                        
                    except Exception as e:
                        print(f"    Error checking message: {e}")
    
    # Step 2: Test OrganizationConsumer for each organization
    print("\n2. Testing OrganizationConsumer for each organization...")
    
    for org in organizations:
        print(f"\n  Testing consumer for {org}...")
        
        # Set organization
        os.environ['ORGANIZATION_ID'] = org
        
        from messaging.config import Settings
        from messaging.consumers.base_consumer import OrganizationConsumer
        
        # Reload settings
        org_settings = Settings()
        
        # Create consumer
        consumer = OrganizationConsumer()
        print(f"    Consumer topics: {consumer.topics}")
        
        # Verify topics include adhesion topic
        expected_adhesion_topic = f"adhesion-evento-{org}"
        adhesion_topic_found = any(expected_adhesion_topic in topic for topic in consumer.topics)
        print(f"    Adhesion topic configured: {adhesion_topic_found}")
        
        # Test handler registration
        has_adhesion_handler = "event_adhesion" in consumer._message_handlers
        print(f"    Adhesion handler registered: {has_adhesion_handler}")
    
    # Step 3: Test end-to-end flow
    print("\n3. Testing end-to-end adhesion flow...")
    
    # Start consumer for esperanza-viva
    os.environ['ORGANIZATION_ID'] = 'esperanza-viva'
    
    from messaging.config import Settings
    from messaging.consumers.base_consumer import OrganizationConsumer
    
    esperanza_settings = Settings()
    esperanza_consumer = OrganizationConsumer()
    
    print(f"Starting consumer for {esperanza_settings.organization_id}")
    print(f"Consumer topics: {esperanza_consumer.topics}")
    
    # Start consumer in background
    consumer_thread = threading.Thread(target=esperanza_consumer.start)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    time.sleep(2)  # Let consumer start
    
    # Send message from empuje-comunitario
    os.environ['ORGANIZATION_ID'] = 'empuje-comunitario'
    
    from messaging.config import Settings
    from messaging.producers.base_producer import BaseProducer
    
    empuje_settings = Settings()
    producer = BaseProducer()
    
    test_volunteer_data = {
        "volunteer_id": 999,
        "name": "End-to-End",
        "surname": "Test",
        "email": "e2e@empuje.org",
        "phone": "999999999"
    }
    
    print(f"Sending adhesion from {empuje_settings.organization_id} to esperanza-viva...")
    
    success = producer.publish_event_adhesion(
        target_org="esperanza-viva",
        event_id="e2e-test-event",
        volunteer_data=test_volunteer_data
    )
    
    print(f"Message sent: {success}")
    
    # Wait for processing
    print("Waiting for message processing...")
    time.sleep(5)
    
    # Stop consumer
    esperanza_consumer.stop()
    
    print("End-to-end test completed")
    
    print("\n✅ Dynamic adhesion system test completed!")

def list_all_topics():
    """List all topics in Kafka"""
    print("\n=== LISTING ALL KAFKA TOPICS ===")
    
    try:
        from kafka.admin import KafkaAdminClient
        
        admin_client = KafkaAdminClient(
            bootstrap_servers=['localhost:9092'],
            client_id='topic_lister'
        )
        
        # List topics
        metadata = admin_client.list_topics()
        topics = list(metadata.topics.keys())
        
        print(f"Total topics: {len(topics)}")
        
        # Filter adhesion topics
        adhesion_topics = [t for t in topics if 'adhesion-evento' in t]
        print(f"Adhesion topics: {adhesion_topics}")
        
        # Filter transfer topics
        transfer_topics = [t for t in topics if 'transferencia-donaciones' in t]
        print(f"Transfer topics: {transfer_topics}")
        
        admin_client.close()
        
    except Exception as e:
        print(f"Error listing topics: {e}")

def main():
    """Main test function"""
    print("Starting dynamic adhesion system test...")
    
    # List topics first
    list_all_topics()
    
    # Test dynamic system
    test_dynamic_adhesion_system()
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()