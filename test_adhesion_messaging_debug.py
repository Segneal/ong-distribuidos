#!/usr/bin/env python3
"""
Script para debuggear el sistema de mensajería de adhesiones
Verifica que los mensajes se envíen y reciban correctamente
"""
import os
import sys
import json
import time
import threading
from datetime import datetime

# Add messaging service to path
sys.path.append('messaging-service/src')

from messaging.config import settings, Topics
from messaging.kafka.connection import kafka_manager
from messaging.producers.base_producer import BaseProducer
from messaging.consumers.adhesion_consumer import AdhesionConsumer

def test_adhesion_messaging():
    """Test complete adhesion messaging flow"""
    print("=== DEBUGGING ADHESION MESSAGING ===")
    print(f"Organization ID: {settings.organization_id}")
    print(f"Kafka Brokers: {settings.kafka_bootstrap_servers}")
    
    # Test 1: Check Kafka connection
    print("\n1. Testing Kafka connection...")
    health = kafka_manager.health_check()
    print(f"Kafka Health: {health}")
    
    if health['status'] != 'healthy':
        print("❌ Kafka connection failed!")
        return False
    
    # Test 2: Create topics
    print("\n2. Creating topics...")
    esperanza_topic = Topics.get_adhesion_topic("esperanza-viva")
    empuje_topic = Topics.get_adhesion_topic("empuje-comunitario")
    
    topics_to_create = [esperanza_topic, empuje_topic]
    kafka_manager.create_topics_if_not_exist(topics_to_create)
    print(f"Topics created: {topics_to_create}")
    
    # Test 3: Test producer
    print("\n3. Testing producer...")
    producer = BaseProducer()
    
    # Create test adhesion message
    test_volunteer_data = {
        "volunteer_id": 123,
        "name": "Juan",
        "surname": "Pérez",
        "email": "juan.perez@empuje.org",
        "phone": "123456789"
    }
    
    # Send message from empuje-comunitario to esperanza-viva
    success = producer.publish_event_adhesion(
        target_org="esperanza-viva",
        event_id="test-event-001",
        volunteer_data=test_volunteer_data
    )
    
    print(f"Message sent: {success}")
    
    if not success:
        print("❌ Failed to send adhesion message!")
        return False
    
    # Test 4: Test consumer
    print("\n4. Testing consumer...")
    
    # Create consumer for esperanza-viva
    os.environ['ORGANIZATION_ID'] = 'esperanza-viva'
    
    # Reload settings with new organization
    from messaging.config import Settings
    esperanza_settings = Settings()
    print(f"Consumer organization: {esperanza_settings.organization_id}")
    
    # Create consumer
    consumer = AdhesionConsumer()
    print(f"Consumer topic: {consumer.topic}")
    print(f"Consumer group: {consumer.get_consumer_group()}")
    
    # Start consumer in thread
    consumer_thread = threading.Thread(target=consumer.start)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    print("Consumer started, waiting for messages...")
    time.sleep(10)  # Wait for message processing
    
    # Stop consumer
    consumer.stop()
    
    print("\n5. Checking message consumption...")
    # We should check logs or database to see if message was processed
    
    return True

def test_topic_listing():
    """List all topics to verify they exist"""
    print("\n=== LISTING KAFKA TOPICS ===")
    
    try:
        from kafka.admin import KafkaAdminClient
        from kafka.admin.config_resource import ConfigResource, ConfigResourceType
        
        admin_client = KafkaAdminClient(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            client_id='topic_lister'
        )
        
        # List topics
        metadata = admin_client.list_topics()
        print(f"Available topics: {list(metadata.topics.keys())}")
        
        # Check specific adhesion topics
        esperanza_topic = Topics.get_adhesion_topic("esperanza-viva")
        empuje_topic = Topics.get_adhesion_topic("empuje-comunitario")
        
        print(f"Esperanza topic: {esperanza_topic} - {'EXISTS' if esperanza_topic in metadata.topics else 'MISSING'}")
        print(f"Empuje topic: {empuje_topic} - {'EXISTS' if empuje_topic in metadata.topics else 'MISSING'}")
        
        admin_client.close()
        
    except Exception as e:
        print(f"Error listing topics: {e}")

def test_manual_consumer():
    """Manually consume messages from adhesion topic"""
    print("\n=== MANUAL CONSUMER TEST ===")
    
    try:
        from kafka import KafkaConsumer
        
        # Test consuming from esperanza-viva topic
        topic = Topics.get_adhesion_topic("esperanza-viva")
        print(f"Consuming from topic: {topic}")
        
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id='debug-consumer',
            auto_offset_reset='earliest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
            consumer_timeout_ms=5000  # 5 second timeout
        )
        
        print("Waiting for messages...")
        message_count = 0
        
        for message in consumer:
            message_count += 1
            print(f"Message {message_count}:")
            print(f"  Topic: {message.topic}")
            print(f"  Partition: {message.partition}")
            print(f"  Offset: {message.offset}")
            print(f"  Key: {message.key}")
            print(f"  Value: {json.dumps(message.value, indent=2)}")
            print("-" * 50)
            
            if message_count >= 10:  # Limit to 10 messages
                break
        
        if message_count == 0:
            print("No messages found in topic")
        
        consumer.close()
        
    except Exception as e:
        print(f"Error in manual consumer: {e}")

def main():
    """Main test function"""
    print("Starting adhesion messaging debug...")
    
    # Test 1: Topic listing
    test_topic_listing()
    
    # Test 2: Manual consumer
    test_manual_consumer()
    
    # Test 3: Full messaging test
    test_adhesion_messaging()
    
    print("\nDebug complete!")

if __name__ == "__main__":
    main()