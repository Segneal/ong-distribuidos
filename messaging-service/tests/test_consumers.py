"""
Unit tests for message consumers
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
import threading
import time
from kafka.errors import KafkaError, CommitFailedError

from messaging.consumers.base_consumer import BaseConsumer, NetworkConsumer, OrganizationConsumer
# MockKafkaMessage and MockTopicPartition will be defined locally


class MockKafkaMessage:
    """Mock Kafka message for testing consumers"""
    
    def __init__(self, value, topic="test-topic", partition=0, offset=0):
        self.value = value
        self.topic = topic
        self.partition = partition
        self.offset = offset


class MockTopicPartition:
    """Mock Kafka TopicPartition for testing"""
    
    def __init__(self, topic, partition):
        self.topic = topic
        self.partition = partition


class TestBaseConsumer:
    """Test cases for BaseConsumer"""
    
    def test_init(self, mock_settings):
        """Test BaseConsumer initialization"""
        topics = ["test-topic-1", "test-topic-2"]
        consumer = ConcreteConsumer(topics)
        
        assert consumer.topics == topics
        assert consumer.organization_id == mock_settings.organization_id
        assert consumer._consumer is None
        assert consumer._running is False
        assert consumer._thread is None
        assert consumer._message_handlers == {}
        assert consumer._error_handlers == {}
    
    def test_register_message_handler(self):
        """Test registering message handlers"""
        consumer = ConcreteConsumer(["test-topic"])
        
        def test_handler(message):
            pass
        
        consumer.register_message_handler("test_type", test_handler)
        
        assert "test_type" in consumer._message_handlers
        assert consumer._message_handlers["test_type"] == test_handler
    
    def test_register_error_handler(self):
        """Test registering error handlers"""
        consumer = ConcreteConsumer(["test-topic"])
        
        def test_error_handler(error, message):
            pass
        
        consumer.register_error_handler("TestError", test_error_handler)
        
        assert "TestError" in consumer._error_handlers
        assert consumer._error_handlers["TestError"] == test_error_handler
    
    def test_validate_message_envelope_success(self):
        """Test successful message envelope validation"""
        consumer = ConcreteConsumer(["test-topic"])
        
        message = {
            "message_id": "msg-123",
            "message_type": "test_type",
            "organization_id": "test-org",
            "timestamp": "2024-01-15T10:30:00Z",
            "data": {"test": "data"}
        }
        
        assert consumer._validate_message_envelope(message) is True
    
    def test_validate_message_envelope_missing_field(self):
        """Test message envelope validation with missing field"""
        consumer = ConcreteConsumer(["test-topic"])
        
        message = {
            "message_id": "msg-123",
            "message_type": "test_type",
            # Missing organization_id, timestamp, data
        }
        
        assert consumer._validate_message_envelope(message) is False
    
    def test_should_process_message_external(self, mock_settings):
        """Test message processing decision for external messages"""
        consumer = ConcreteConsumer(["test-topic"])
        
        message = {
            "organization_id": "other-org"
        }
        
        assert consumer._should_process_message(message) is True
    
    def test_should_process_message_own(self, mock_settings):
        """Test message processing decision for own messages"""
        consumer = ConcreteConsumer(["test-topic"])
        
        message = {
            "organization_id": mock_settings.organization_id
        }
        
        assert consumer._should_process_message(message) is False
    
    @patch('messaging.consumers.base_consumer.logger')
    def test_process_message_success(self, mock_logger, mock_settings):
        """Test successful message processing"""
        consumer = ConcreteConsumer(["test-topic"])
        
        # Register a test handler
        handler_mock = Mock()
        consumer.register_message_handler("test_type", handler_mock)
        
        message = {
            "message_id": "msg-123",
            "message_type": "test_type",
            "organization_id": "other-org",
            "timestamp": "2024-01-15T10:30:00Z",
            "data": {"test": "data"}
        }
        
        consumer._process_message(message)
        
        # Verify handler was called with message data
        handler_mock.assert_called_once_with({"test": "data"})
    
    @patch('messaging.consumers.base_consumer.logger')
    def test_process_message_invalid_envelope(self, mock_logger):
        """Test message processing with invalid envelope"""
        consumer = ConcreteConsumer(["test-topic"])
        
        message = {
            "message_id": "msg-123"
            # Missing required fields
        }
        
        consumer._process_message(message)
        
        # Verify error was logged
        mock_logger.error.assert_called()
    
    @patch('messaging.consumers.base_consumer.logger')
    def test_process_message_own_message(self, mock_logger, mock_settings):
        """Test message processing for own messages (should be skipped)"""
        consumer = ConcreteConsumer(["test-topic"])
        
        handler_mock = Mock()
        consumer.register_message_handler("test_type", handler_mock)
        
        message = {
            "message_id": "msg-123",
            "message_type": "test_type",
            "organization_id": mock_settings.organization_id,
            "timestamp": "2024-01-15T10:30:00Z",
            "data": {"test": "data"}
        }
        
        consumer._process_message(message)
        
        # Verify handler was not called
        handler_mock.assert_not_called()
    
    @patch('messaging.consumers.base_consumer.logger')
    def test_process_message_unknown_type(self, mock_logger, mock_settings):
        """Test message processing with unknown message type"""
        consumer = ConcreteConsumer(["test-topic"])
        
        message = {
            "message_id": "msg-123",
            "message_type": "unknown_type",
            "organization_id": "other-org",
            "timestamp": "2024-01-15T10:30:00Z",
            "data": {"test": "data"}
        }
        
        consumer._process_message(message)
        
        # Verify warning was logged
        mock_logger.warning.assert_called()
    
    @patch('messaging.consumers.base_consumer.logger')
    def test_process_message_handler_error(self, mock_logger, mock_settings):
        """Test message processing with handler error"""
        consumer = ConcreteConsumer(["test-topic"])
        
        # Register a handler that raises an exception
        def failing_handler(message_data):
            raise ValueError("Handler error")
        
        consumer.register_message_handler("test_type", failing_handler)
        
        message = {
            "message_id": "msg-123",
            "message_type": "test_type",
            "organization_id": "other-org",
            "timestamp": "2024-01-15T10:30:00Z",
            "data": {"test": "data"}
        }
        
        consumer._process_message(message)
        
        # Verify error was logged
        mock_logger.error.assert_called()
    
    @patch('messaging.consumers.base_consumer.logger')
    def test_handle_processing_error_with_handler(self, mock_logger):
        """Test error handling with registered error handler"""
        consumer = ConcreteConsumer(["test-topic"])
        
        error_handler_mock = Mock()
        consumer.register_error_handler("ValueError", error_handler_mock)
        
        error = ValueError("Test error")
        message = {"test": "message"}
        
        consumer._handle_processing_error(error, message)
        
        # Verify error handler was called
        error_handler_mock.assert_called_once_with(error, message)
    
    @patch('messaging.consumers.base_consumer.logger')
    def test_handle_processing_error_without_handler(self, mock_logger):
        """Test error handling without registered error handler"""
        consumer = ConcreteConsumer(["test-topic"])
        
        error = ValueError("Test error")
        message = {"test": "message"}
        
        consumer._handle_processing_error(error, message)
        
        # Verify error was logged
        mock_logger.error.assert_called()
    
    @patch('messaging.consumers.base_consumer.logger')
    def test_handle_processing_error_handler_fails(self, mock_logger):
        """Test error handling when error handler itself fails"""
        consumer = ConcreteConsumer(["test-topic"])
        
        def failing_error_handler(error, message):
            raise RuntimeError("Error handler failed")
        
        consumer.register_error_handler("ValueError", failing_error_handler)
        
        error = ValueError("Test error")
        message = {"test": "message"}
        
        consumer._handle_processing_error(error, message)
        
        # Verify both errors were logged
        assert mock_logger.error.call_count >= 1
    
    def test_is_running_false(self):
        """Test is_running when consumer is not running"""
        consumer = ConcreteConsumer(["test-topic"])
        assert consumer.is_running() is False
    
    def test_is_running_true(self):
        """Test is_running when consumer is running"""
        consumer = ConcreteConsumer(["test-topic"])
        consumer._running = True
        assert consumer.is_running() is True
    
    @patch('messaging.consumers.base_consumer.logger')
    def test_start_already_running(self, mock_logger):
        """Test starting consumer when already running"""
        consumer = ConcreteConsumer(["test-topic"])
        consumer._running = True
        
        consumer.start()
        
        mock_logger.warning.assert_called()
    
    @patch('messaging.consumers.base_consumer.logger')
    def test_stop_not_running(self, mock_logger):
        """Test stopping consumer when not running"""
        consumer = ConcreteConsumer(["test-topic"])
        
        consumer.stop()
        
        mock_logger.warning.assert_called()
    
    def test_setup_handlers_abstract(self):
        """Test that setup_handlers is abstract"""
        consumer = ConcreteConsumer(["test-topic"])
        
        with pytest.raises(TypeError):
            # This should fail because setup_handlers is abstract
            consumer.setup_handlers()


class ConcreteConsumer(BaseConsumer):
    """Concrete implementation of BaseConsumer for testing"""
    
    def setup_handlers(self):
        """Concrete implementation of setup_handlers"""
        pass


class TestConcreteConsumer:
    """Test cases for concrete consumer implementation"""
    
    @patch('threading.Thread')
    @patch('messaging.consumers.base_consumer.logger')
    def test_start_success(self, mock_logger, mock_thread):
        """Test successful consumer start"""
        consumer = ConcreteConsumer(["test-topic"])
        
        consumer.start()
        
        assert consumer._running is True
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    @patch('messaging.consumers.base_consumer.logger')
    def test_stop_success(self, mock_logger):
        """Test successful consumer stop"""
        consumer = ConcreteConsumer(["test-topic"])
        
        # Mock running thread
        mock_thread = Mock()
        mock_thread.is_alive.return_value = False
        consumer._thread = mock_thread
        consumer._running = True
        
        consumer.stop()
        
        assert consumer._running is False
        mock_thread.join.assert_called_once_with(timeout=10)


class TestNetworkConsumer:
    """Test cases for NetworkConsumer"""
    
    @patch('messaging.config.Topics')
    def test_init(self, mock_topics, mock_settings):
        """Test NetworkConsumer initialization"""
        mock_topics.DONATION_REQUESTS = "donation-requests"
        mock_topics.DONATION_OFFERS = "donation-offers"
        mock_topics.REQUEST_CANCELLATIONS = "request-cancellations"
        mock_topics.SOLIDARITY_EVENTS = "solidarity-events"
        mock_topics.EVENT_CANCELLATIONS = "event-cancellations"
        
        consumer = NetworkConsumer()
        
        expected_topics = [
            "donation-requests",
            "donation-offers", 
            "request-cancellations",
            "solidarity-events",
            "event-cancellations"
        ]
        
        assert consumer.topics == expected_topics
        assert consumer.organization_id == mock_settings.organization_id
    
    def test_setup_handlers(self):
        """Test NetworkConsumer handler setup"""
        with patch('messaging.config.Topics'):
            consumer = NetworkConsumer()
            
            # Verify handlers are registered
            assert "donation_request" in consumer._message_handlers
            assert "donation_offer" in consumer._message_handlers
            assert "request_cancellation" in consumer._message_handlers
            assert "solidarity_event" in consumer._message_handlers
            assert "event_cancellation" in consumer._message_handlers
    
    @patch('messaging.consumers.donation_consumer.DonationRequestConsumer')
    @patch('messaging.consumers.base_consumer.logger')
    def test_handle_donation_request(self, mock_logger, mock_donation_consumer_class):
        """Test handling donation request"""
        with patch('messaging.config.Topics'):
            consumer = NetworkConsumer()
            
            message_data = {
                "organization_id": "other-org",
                "request_id": "REQ-001",
                "donations": [],
                "timestamp": "2024-01-15T10:30:00Z"
            }
            
            consumer._handle_donation_request(message_data)
            
            # Verify DonationRequestConsumer was created and used
            mock_donation_consumer_class.assert_called_once()
            mock_consumer_instance = mock_donation_consumer_class.return_value
            mock_consumer_instance.process_message.assert_called_once()
    
    @patch('messaging.services.offer_service.OfferService')
    @patch('messaging.consumers.base_consumer.logger')
    def test_handle_donation_offer(self, mock_logger, mock_offer_service_class):
        """Test handling donation offer"""
        with patch('messaging.config.Topics'):
            consumer = NetworkConsumer()
            
            message_data = {
                "offer_id": "OFFER-001",
                "donor_organization": "other-org",
                "donations": [],
                "timestamp": "2024-01-15T10:30:00Z"
            }
            
            # Mock successful processing
            mock_offer_service = mock_offer_service_class.return_value
            mock_offer_service.process_external_offer.return_value = True
            
            consumer._handle_donation_offer(message_data)
            
            # Verify OfferService was used
            mock_offer_service_class.assert_called_once()
            mock_offer_service.process_external_offer.assert_called_once_with(message_data)
    
    @patch('messaging.services.offer_service.OfferService')
    @patch('messaging.consumers.base_consumer.logger')
    def test_handle_donation_offer_error(self, mock_logger, mock_offer_service_class):
        """Test handling donation offer with error"""
        with patch('messaging.config.Topics'):
            consumer = NetworkConsumer()
            
            message_data = {
                "offer_id": "OFFER-001",
                "donor_organization": "other-org",
                "donations": [],
                "timestamp": "2024-01-15T10:30:00Z"
            }
            
            # Mock service error
            mock_offer_service = mock_offer_service_class.return_value
            mock_offer_service.process_external_offer.side_effect = Exception("Service error")
            
            consumer._handle_donation_offer(message_data)
            
            # Verify error was logged
            mock_logger.error.assert_called()
    
    @patch('messaging.services.event_service.EventService')
    @patch('messaging.consumers.base_consumer.logger')
    def test_handle_solidarity_event(self, mock_logger, mock_event_service_class):
        """Test handling solidarity event"""
        with patch('messaging.config.Topics'):
            consumer = NetworkConsumer()
            
            message_data = {
                "organization_id": "other-org",
                "event_id": "EVENT-001",
                "name": "Test Event",
                "timestamp": "2024-01-15T10:30:00Z"
            }
            
            # Mock successful processing
            mock_event_service = mock_event_service_class.return_value
            mock_event_service.process_external_event.return_value = True
            
            consumer._handle_solidarity_event(message_data)
            
            # Verify EventService was used
            mock_event_service_class.assert_called_once()
            mock_event_service.process_external_event.assert_called_once_with(message_data)
    
    @patch('messaging.services.event_service.EventService')
    @patch('messaging.consumers.base_consumer.logger')
    def test_handle_event_cancellation(self, mock_logger, mock_event_service_class):
        """Test handling event cancellation"""
        with patch('messaging.config.Topics'):
            consumer = NetworkConsumer()
            
            message_data = {
                "organization_id": "other-org",
                "event_id": "EVENT-001",
                "timestamp": "2024-01-15T10:30:00Z"
            }
            
            # Mock successful processing
            mock_event_service = mock_event_service_class.return_value
            mock_event_service.process_event_cancellation.return_value = True
            
            consumer._handle_event_cancellation(message_data)
            
            # Verify EventService was used
            mock_event_service_class.assert_called_once()
            mock_event_service.process_event_cancellation.assert_called_once_with(message_data)


class TestOrganizationConsumer:
    """Test cases for OrganizationConsumer"""
    
    @patch('messaging.config.Topics')
    def test_init(self, mock_topics, mock_settings):
        """Test OrganizationConsumer initialization"""
        mock_topics.get_transfer_topic.return_value = f"transfer-{mock_settings.organization_id}"
        mock_topics.get_adhesion_topic.return_value = f"adhesion-{mock_settings.organization_id}"
        
        consumer = OrganizationConsumer()
        
        expected_topics = [
            f"transfer-{mock_settings.organization_id}",
            f"adhesion-{mock_settings.organization_id}"
        ]
        
        assert consumer.topics == expected_topics
        assert consumer.organization_id == mock_settings.organization_id
    
    def test_setup_handlers(self):
        """Test OrganizationConsumer handler setup"""
        with patch('messaging.config.Topics'):
            consumer = OrganizationConsumer()
            
            # Verify handlers are registered
            assert "donation_transfer" in consumer._message_handlers
            assert "event_adhesion" in consumer._message_handlers
    
    @patch('messaging.consumers.transfer_consumer.DonationTransferConsumer')
    @patch('messaging.consumers.base_consumer.logger')
    def test_handle_donation_transfer(self, mock_logger, mock_transfer_consumer_class):
        """Test handling donation transfer"""
        with patch('messaging.config.Topics'):
            consumer = OrganizationConsumer()
            
            message_data = {
                "request_id": "REQ-001",
                "donor_organization": "other-org",
                "donations": [],
                "timestamp": "2024-01-15T10:30:00Z"
            }
            
            consumer._handle_donation_transfer(message_data)
            
            # Verify DonationTransferConsumer was created and used
            mock_transfer_consumer_class.assert_called_once()
            mock_consumer_instance = mock_transfer_consumer_class.return_value
            mock_consumer_instance.process_message.assert_called_once()
    
    @patch('messaging.services.adhesion_service.AdhesionService')
    @patch('messaging.consumers.base_consumer.logger')
    def test_handle_event_adhesion(self, mock_logger, mock_adhesion_service_class):
        """Test handling event adhesion"""
        with patch('messaging.config.Topics'):
            consumer = OrganizationConsumer()
            
            message_data = {
                "event_id": "EVENT-001",
                "volunteer": {
                    "organization_id": "other-org",
                    "volunteer_id": "VOL-001",
                    "name": "Juan"
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
            
            # Mock successful processing
            mock_adhesion_service = mock_adhesion_service_class.return_value
            mock_adhesion_service.process_incoming_adhesion.return_value = True
            
            consumer._handle_event_adhesion(message_data)
            
            # Verify AdhesionService was used
            mock_adhesion_service_class.assert_called_once()
            mock_adhesion_service.process_incoming_adhesion.assert_called_once_with(message_data)
    
    @patch('messaging.services.adhesion_service.AdhesionService')
    @patch('messaging.consumers.base_consumer.logger')
    def test_handle_event_adhesion_error(self, mock_logger, mock_adhesion_service_class):
        """Test handling event adhesion with error"""
        with patch('messaging.config.Topics'):
            consumer = OrganizationConsumer()
            
            message_data = {
                "event_id": "EVENT-001",
                "volunteer": {
                    "organization_id": "other-org",
                    "volunteer_id": "VOL-001",
                    "name": "Juan"
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
            
            # Mock service error
            mock_adhesion_service = mock_adhesion_service_class.return_value
            mock_adhesion_service.process_incoming_adhesion.side_effect = Exception("Service error")
            
            consumer._handle_event_adhesion(message_data)
            
            # Verify error was logged
            mock_logger.error.assert_called()