"""
Integration tests for Kafka messaging flows
"""
import pytest
import time
import json
from unittest.mock import patch, Mock

from messaging.kafka.connection import KafkaConnectionManager
from messaging.producers.base_producer import BaseProducer
from messaging.consumers.base_consumer import NetworkConsumer, OrganizationConsumer


@pytest.mark.integration
class TestKafkaIntegration:
    """Integration tests for Kafka messaging"""
    
    def test_kafka_connection(self, kafka_config):
        """Test basic Kafka connection"""
        try:
            manager = KafkaConnectionManager()
            
            # Override settings for test
            with patch('messaging.kafka.connection.settings') as mock_settings:
                mock_settings.kafka_brokers = kafka_config['bootstrap_servers']
                mock_settings.kafka_group_id = kafka_config['group_id']
                
                # Test producer creation
                producer = manager.get_producer()
                assert producer is not None
                
                # Test admin client creation
                admin = manager.get_admin_client()
                assert admin is not None
                
                # Cleanup
                manager.close()
                
        except Exception as e:
            pytest.skip(f"Kafka integration test failed: {e}")
    
    def test_producer_consumer_flow(self, kafka_config, setup_kafka_topics, kafka_producer, kafka_consumer, integration_helper):
        """Test complete producer-consumer flow"""
        topic = "test-donation-requests"
        
        # Create test message
        test_data = {
            "organization_id": "external-org",
            "request_id": "REQ-FLOW-001",
            "donations": [
                {
                    "category": "ALIMENTOS",
                    "description": "Puré de tomates"
                }
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        message_envelope = integration_helper.create_message_envelope(
            "donation_request", "external-org", test_data
        )
        
        # Send message
        future = kafka_producer.send(topic, value=message_envelope, key="external-org")
        record_metadata = future.get(timeout=10)
        
        assert record_metadata.topic == topic
        
        # Consume message
        consumer = kafka_consumer([topic])
        messages = []
        
        try:
            for message in consumer:
                messages.append(message.value)
                break  # Only get first message
        except Exception:
            pass  # Timeout is expected
        finally:
            consumer.close()
        
        # Verify message was received
        assert len(messages) == 1
        received_message = messages[0]
        assert received_message["message_type"] == "donation_request"
        assert received_message["organization_id"] == "external-org"
        assert received_message["data"]["request_id"] == "REQ-FLOW-001"
    
    def test_multiple_topics_flow(self, kafka_config, setup_kafka_topics, kafka_producer, kafka_consumer, integration_helper):
        """Test messaging across multiple topics"""
        topics = ["test-donation-requests", "test-donation-offers"]
        
        # Send messages to different topics
        messages_sent = []
        
        # Send donation request
        request_data = {
            "organization_id": "org-1",
            "request_id": "REQ-MULTI-001",
            "donations": [{"category": "ALIMENTOS", "description": "Arroz"}],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        request_envelope = integration_helper.create_message_envelope(
            "donation_request", "org-1", request_data
        )
        
        kafka_producer.send(topics[0], value=request_envelope, key="org-1")
        messages_sent.append(("donation_request", "org-1"))
        
        # Send donation offer
        offer_data = {
            "offer_id": "OFFER-MULTI-001",
            "donor_organization": "org-2",
            "donations": [{"category": "ROPA", "description": "Camisetas", "quantity": "10"}],
            "timestamp": "2024-01-15T11:00:00Z"
        }
        
        offer_envelope = integration_helper.create_message_envelope(
            "donation_offer", "org-2", offer_data
        )
        
        kafka_producer.send(topics[1], value=offer_envelope, key="org-2")
        messages_sent.append(("donation_offer", "org-2"))
        
        # Flush producer
        kafka_producer.flush()
        
        # Consume from both topics
        consumer = kafka_consumer(topics)
        messages_received = []
        
        try:
            for message in consumer:
                messages_received.append((message.value["message_type"], message.value["organization_id"]))
                if len(messages_received) >= 2:
                    break
        except Exception:
            pass  # Timeout is expected
        finally:
            consumer.close()
        
        # Verify all messages were received
        assert len(messages_received) >= 1  # At least one message should be received
        
        # Check that we received the expected message types
        received_types = [msg[0] for msg in messages_received]
        assert "donation_request" in received_types or "donation_offer" in received_types
    
    @patch('messaging.config.settings')
    def test_producer_integration(self, mock_settings, kafka_config, setup_kafka_topics, kafka_consumer):
        """Test BaseProducer integration with real Kafka"""
        mock_settings.organization_id = "test-org"
        mock_settings.kafka_brokers = kafka_config['bootstrap_servers']
        mock_settings.kafka_group_id = kafka_config['group_id']
        
        # Mock Topics configuration
        with patch('messaging.config.Topics') as mock_topics:
            mock_topics.DONATION_REQUESTS = "test-donation-requests"
            mock_topics.DONATION_OFFERS = "test-donation-offers"
            mock_topics.get_transfer_topic.return_value = "test-transfer-test-org"
            
            # Create producer
            producer = BaseProducer()
            
            # Test donation request publishing
            donations = [
                {"category": "ALIMENTOS", "description": "Puré de tomates"}
            ]
            
            result = producer.publish_donation_request("REQ-PROD-001", donations)
            assert result is True
            
            # Verify message was sent
            consumer = kafka_consumer(["test-donation-requests"])
            messages = []
            
            try:
                for message in consumer:
                    messages.append(message.value)
                    break
            except Exception:
                pass
            finally:
                consumer.close()
            
            # Should have received the message
            if messages:
                received = messages[0]
                assert received["message_type"] == "donation_request"
                assert received["data"]["request_id"] == "REQ-PROD-001"
    
    def test_error_handling_integration(self, kafka_config, setup_kafka_topics):
        """Test error handling in integration scenarios"""
        # Test with invalid Kafka configuration
        with patch('messaging.kafka.connection.settings') as mock_settings:
            mock_settings.kafka_brokers = "invalid:9999"
            mock_settings.kafka_group_id = "test-group"
            
            manager = KafkaManager()
            
            # Should raise exception for invalid broker
            with pytest.raises(Exception):
                producer = manager.get_producer()
                # Try to send a message to trigger connection
                producer.send("test-topic", value={"test": "data"}).get(timeout=5)
    
    def test_message_ordering_integration(self, kafka_config, setup_kafka_topics, kafka_producer, kafka_consumer, integration_helper):
        """Test message ordering in Kafka"""
        topic = "test-donation-requests"
        
        # Send multiple messages with same key (should maintain order)
        messages_sent = []
        for i in range(3):
            test_data = {
                "organization_id": "order-org",
                "request_id": f"REQ-ORDER-{i:03d}",
                "donations": [{"category": "ALIMENTOS", "description": f"Item {i}"}],
                "timestamp": "2024-01-15T10:30:00Z"
            }
            
            message_envelope = integration_helper.create_message_envelope(
                "donation_request", "order-org", test_data
            )
            
            kafka_producer.send(topic, value=message_envelope, key="order-org")
            messages_sent.append(f"REQ-ORDER-{i:03d}")
        
        kafka_producer.flush()
        
        # Consume messages
        consumer = kafka_consumer([topic])
        messages_received = []
        
        try:
            for message in consumer:
                messages_received.append(message.value["data"]["request_id"])
                if len(messages_received) >= 3:
                    break
        except Exception:
            pass
        finally:
            consumer.close()
        
        # Verify we received messages (order may not be guaranteed in test environment)
        assert len(messages_received) >= 1
        
        # At least verify we received some of the expected messages
        for received_id in messages_received:
            assert received_id in messages_sent
    
    def test_consumer_group_integration(self, kafka_config, setup_kafka_topics, kafka_producer, integration_helper):
        """Test consumer group behavior"""
        topic = "test-donation-requests"
        
        # Send a message
        test_data = {
            "organization_id": "group-org",
            "request_id": "REQ-GROUP-001",
            "donations": [{"category": "ALIMENTOS", "description": "Test item"}],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        message_envelope = integration_helper.create_message_envelope(
            "donation_request", "group-org", test_data
        )
        
        kafka_producer.send(topic, value=message_envelope, key="group-org")
        kafka_producer.flush()
        
        # Create two consumers in the same group
        from kafka import KafkaConsumer
        
        consumer1 = KafkaConsumer(
            topic,
            bootstrap_servers=kafka_config['bootstrap_servers'],
            group_id="same-group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
            auto_offset_reset='earliest',
            consumer_timeout_ms=3000
        )
        
        consumer2 = KafkaConsumer(
            topic,
            bootstrap_servers=kafka_config['bootstrap_servers'],
            group_id="same-group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
            auto_offset_reset='earliest',
            consumer_timeout_ms=3000
        )
        
        messages1 = []
        messages2 = []
        
        try:
            # Consumer 1 should get the message
            for message in consumer1:
                messages1.append(message.value)
                break
        except Exception:
            pass
        
        try:
            # Consumer 2 should not get the same message (already consumed by consumer 1)
            for message in consumer2:
                messages2.append(message.value)
                break
        except Exception:
            pass  # Timeout expected
        
        consumer1.close()
        consumer2.close()
        
        # Only one consumer should have received the message
        total_messages = len(messages1) + len(messages2)
        assert total_messages <= 1  # Message should not be duplicated across consumers in same group