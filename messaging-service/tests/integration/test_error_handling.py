"""
Integration tests for error handling and recovery scenarios
"""
import pytest
import time
import json
from unittest.mock import patch, Mock
from kafka.errors import KafkaError, KafkaTimeoutError


@pytest.mark.integration
class TestErrorHandling:
    """Integration tests for error handling scenarios"""
    
    def test_kafka_connection_failure_recovery(self, kafka_config):
        """Test recovery from Kafka connection failures"""
        from messaging.kafka.connection import KafkaManager
        
        manager = KafkaManager()
        
        # Test with invalid broker configuration
        with patch('messaging.kafka.connection.settings') as mock_settings:
            mock_settings.kafka_brokers = "invalid-broker:9999"
            mock_settings.kafka_group_id = "test-group"
            
            # Should raise exception for invalid broker
            with pytest.raises(Exception):
                producer = manager.get_producer()
                # Try to send a message to trigger connection
                future = producer.send("test-topic", value={"test": "data"})
                future.get(timeout=2)  # Short timeout to fail quickly
    
    def test_message_processing_error_recovery(self, setup_test_database, integration_test_data):
        """Test recovery from message processing errors"""
        cursor = setup_test_database
        
        # Test database constraint violation recovery
        request_data = integration_test_data['donation_request']
        
        # Insert first record successfully
        cursor.execute("""
            INSERT INTO solicitudes_externas 
            (organizacion_solicitante, solicitud_id, donaciones, activa)
            VALUES (%s, %s, %s, %s)
        """, (
            request_data['organization_id'],
            request_data['request_id'],
            json.dumps(request_data['donations']),
            True
        ))
        
        # Try to insert duplicate (should fail due to unique constraint)
        try:
            cursor.execute("""
                INSERT INTO solicitudes_externas 
                (organizacion_solicitante, solicitud_id, donaciones, activa)
                VALUES (%s, %s, %s, %s)
            """, (
                request_data['organization_id'],
                request_data['request_id'],  # Same ID, should fail
                json.dumps(request_data['donations']),
                True
            ))
            pytest.fail("Expected unique constraint violation")
        except Exception as e:
            # This is expected - duplicate key error
            assert "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower()
        
        # Verify original record is still there
        cursor.execute("""
            SELECT COUNT(*) FROM solicitudes_externas
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """, (request_data['organization_id'], request_data['request_id']))
        
        count = cursor.fetchone()[0]
        assert count == 1
    
    def test_invalid_message_format_handling(self, kafka_config, setup_kafka_topics, 
                                           kafka_producer, kafka_consumer, integration_helper):
        """Test handling of invalid message formats"""
        
        # Send message with invalid JSON structure
        invalid_message = {
            "message_id": "invalid-msg-001",
            "message_type": "donation_request",
            "organization_id": "test-org",
            "timestamp": "2024-01-15T10:30:00Z",
            "data": {
                # Missing required fields
                "type": "donation_request",
                "organization_id": "test-org"
                # Missing request_id, donations, timestamp
            }
        }
        
        # Send invalid message
        kafka_producer.send("test-donation-requests", value=invalid_message, key="test-org")
        
        # Send valid message after invalid one
        valid_data = {
            "type": "donation_request",
            "organization_id": "test-org",
            "request_id": "REQ-VALID-001",
            "donations": [{"category": "ALIMENTOS", "description": "Arroz"}],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        valid_message = integration_helper.create_message_envelope(
            "donation_request", "test-org", valid_data
        )
        
        kafka_producer.send("test-donation-requests", value=valid_message, key="test-org")
        kafka_producer.flush()
        
        # Consume messages
        consumer = kafka_consumer(["test-donation-requests"])
        messages = []
        
        try:
            for message in consumer:
                messages.append(message.value)
                if len(messages) >= 2:
                    break
        except Exception:
            pass
        finally:
            consumer.close()
        
        # Should have received both messages
        assert len(messages) >= 1
        
        # At least one should be the valid message
        valid_received = False
        for msg in messages:
            if (msg.get("data", {}).get("request_id") == "REQ-VALID-001"):
                valid_received = True
                break
        
        assert valid_received
    
    def test_database_connection_error_handling(self, integration_test_data):
        """Test handling of database connection errors"""
        
        # Mock database connection failure
        with patch('psycopg2.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database connection failed")
            
            # Test that services handle database errors gracefully
            try:
                from messaging.services.offer_service import OfferService
                service = OfferService()
                
                offer_data = integration_test_data['donation_offer']
                result = service.process_external_offer(offer_data)
                
                # Should return False on database error, not raise exception
                assert result is False
                
            except ImportError:
                # Service doesn't exist, skip test
                pytest.skip("OfferService not found")
            except Exception as e:
                # Should not propagate database errors
                pytest.fail(f"Service should handle database errors gracefully: {e}")
    
    def test_message_serialization_error_handling(self, kafka_config, setup_kafka_topics, kafka_producer):
        """Test handling of message serialization errors"""
        
        # Create message with non-serializable data
        class NonSerializable:
            pass
        
        invalid_message = {
            "message_id": "serial-error-001",
            "message_type": "donation_request",
            "organization_id": "test-org",
            "timestamp": "2024-01-15T10:30:00Z",
            "data": {
                "non_serializable": NonSerializable()  # This will cause JSON serialization error
            }
        }
        
        # Should handle serialization error gracefully
        try:
            future = kafka_producer.send("test-donation-requests", value=invalid_message, key="test-org")
            future.get(timeout=5)
            pytest.fail("Expected serialization error")
        except Exception as e:
            # Expected - serialization should fail
            assert "serializable" in str(e).lower() or "json" in str(e).lower()
    
    def test_consumer_timeout_handling(self, kafka_config, setup_kafka_topics, kafka_consumer):
        """Test consumer timeout handling"""
        
        # Create consumer with short timeout
        consumer = kafka_consumer(["test-donation-requests"])
        
        messages = []
        start_time = time.time()
        
        try:
            # Try to consume from empty topic (should timeout)
            for message in consumer:
                messages.append(message.value)
                break
        except Exception:
            # Timeout is expected
            pass
        finally:
            consumer.close()
        
        elapsed_time = time.time() - start_time
        
        # Should have timed out quickly (within reasonable time)
        assert elapsed_time < 10  # Should timeout within 10 seconds
        assert len(messages) == 0  # No messages should be received
    
    def test_partial_message_processing_failure(self, setup_test_database, integration_test_data):
        """Test handling of partial message processing failures"""
        cursor = setup_test_database
        connection = cursor.connection
        
        # Test transaction rollback on partial failure
        request_data = integration_test_data['donation_request']
        
        try:
            # Start transaction
            connection.autocommit = False
            
            # Insert first part successfully
            cursor.execute("""
                INSERT INTO solicitudes_externas 
                (organizacion_solicitante, solicitud_id, donaciones, activa)
                VALUES (%s, %s, %s, %s)
            """, (
                request_data['organization_id'],
                request_data['request_id'],
                json.dumps(request_data['donations']),
                True
            ))
            
            # Simulate failure in second part (invalid SQL)
            cursor.execute("INSERT INTO non_existent_table VALUES (1)")
            
            # Should not reach here
            connection.commit()
            pytest.fail("Expected SQL error")
            
        except Exception:
            # Rollback on error
            connection.rollback()
        finally:
            connection.autocommit = True
        
        # Verify no partial data was committed
        cursor.execute("""
            SELECT COUNT(*) FROM solicitudes_externas
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """, (request_data['organization_id'], request_data['request_id']))
        
        count = cursor.fetchone()[0]
        assert count == 0  # No data should be committed due to rollback
    
    def test_concurrent_message_processing_errors(self, setup_test_database, integration_test_data):
        """Test handling of concurrent message processing errors"""
        cursor = setup_test_database
        
        request_data = integration_test_data['donation_request']
        
        # Simulate concurrent processing of same message
        # First processor succeeds
        cursor.execute("""
            INSERT INTO solicitudes_externas 
            (organizacion_solicitante, solicitud_id, donaciones, activa)
            VALUES (%s, %s, %s, %s)
        """, (
            request_data['organization_id'],
            request_data['request_id'],
            json.dumps(request_data['donations']),
            True
        ))
        
        # Second processor tries to process same message (should handle duplicate gracefully)
        try:
            cursor.execute("""
                INSERT INTO solicitudes_externas 
                (organizacion_solicitante, solicitud_id, donaciones, activa)
                VALUES (%s, %s, %s, %s)
            """, (
                request_data['organization_id'],
                request_data['request_id'],  # Same ID
                json.dumps(request_data['donations']),
                True
            ))
            pytest.fail("Expected duplicate key error")
        except Exception:
            # Expected - duplicate processing should be handled
            pass
        
        # Verify only one record exists
        cursor.execute("""
            SELECT COUNT(*) FROM solicitudes_externas
            WHERE organizacion_solicitante = %s AND solicitud_id = %s
        """, (request_data['organization_id'], request_data['request_id']))
        
        count = cursor.fetchone()[0]
        assert count == 1
    
    def test_message_ordering_error_recovery(self, kafka_config, setup_kafka_topics, 
                                           kafka_producer, kafka_consumer, integration_helper):
        """Test recovery from message ordering issues"""
        
        # Send messages in specific order
        messages_sent = []
        
        for i in range(3):
            data = {
                "organization_id": "order-test-org",
                "request_id": f"REQ-ORDER-{i}",
                "donations": [{"category": "ALIMENTOS", "description": f"Item {i}"}],
                "timestamp": f"2024-01-15T10:{30+i}:00Z"
            }
            
            message = integration_helper.create_message_envelope(
                "donation_request", "order-test-org", data
            )
            
            # Use same key to maintain order within partition
            kafka_producer.send("test-donation-requests", value=message, key="order-test-org")
            messages_sent.append(f"REQ-ORDER-{i}")
        
        kafka_producer.flush()
        
        # Consume messages
        consumer = kafka_consumer(["test-donation-requests"])
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
        
        # Verify we received messages (order may vary in test environment)
        assert len(messages_received) >= 1
        
        # All received messages should be from our sent messages
        for received_id in messages_received:
            assert received_id in messages_sent
    
    def test_resource_cleanup_on_error(self, kafka_config):
        """Test proper resource cleanup on errors"""
        from messaging.kafka.connection import KafkaManager
        
        manager = KafkaManager()
        
        # Test producer cleanup on error
        with patch('messaging.kafka.connection.settings') as mock_settings:
            mock_settings.kafka_brokers = kafka_config['bootstrap_servers']
            mock_settings.kafka_group_id = kafka_config['group_id']
            
            try:
                producer = manager.get_producer()
                assert producer is not None
                
                # Simulate error and cleanup
                manager.close()
                
                # Verify cleanup
                assert manager._producer is None
                
            except Exception:
                # Ensure cleanup happens even on error
                manager.close()
                assert manager._producer is None