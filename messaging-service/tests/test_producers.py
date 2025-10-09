"""
Unit tests for message producers
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import uuid

from messaging.producers.base_producer import BaseProducer



@pytest.fixture(autouse=True)
def mock_kafka_manager():
    """Mock kafka_manager for all producer tests"""
    with patch('messaging.producers.base_producer.kafka_manager') as mock_manager:
        mock_producer = Mock()
        mock_producer.send.return_value = Mock()
        mock_producer.send.return_value.get.return_value = Mock(
            topic="test-topic",
            partition=0,
            offset=123
        )
        mock_manager.get_producer.return_value = mock_producer
        yield mock_manager


class TestBaseProducer:
    """Test cases for BaseProducer"""
    
    def test_init(self, mock_settings):
        """Test BaseProducer initialization"""
        producer = BaseProducer()
        assert producer.organization_id == mock_settings.organization_id
    
    def test_create_message_envelope(self, mock_settings):
        """Test message envelope creation"""
        producer = BaseProducer()
        
        data = {"test": "data"}
        envelope = producer._create_message_envelope("test_type", data)
        
        assert "message_id" in envelope
        assert envelope["message_type"] == "test_type"
        assert envelope["organization_id"] == mock_settings.organization_id
        assert "timestamp" in envelope
        assert envelope["data"] == data
        
        # Verify message_id is a valid UUID
        uuid.UUID(envelope["message_id"])
    
    def test_validate_message_success(self):
        """Test successful message validation"""
        producer = BaseProducer()
        
        message = {
            "field1": "value1",
            "field2": "value2"
        }
        required_fields = ["field1", "field2"]
        
        assert producer._validate_message(message, required_fields) is True
    
    def test_validate_message_missing_field(self):
        """Test message validation with missing field"""
        producer = BaseProducer()
        
        message = {
            "field1": "value1"
        }
        required_fields = ["field1", "field2"]
        
        assert producer._validate_message(message, required_fields) is False
    
    @patch('messaging.producers.base_producer.logger')
    def test_publish_message_success(self, mock_logger, mock_kafka_manager, mock_settings):
        """Test successful message publishing"""
        producer = BaseProducer()
        
        message = {"type": "test", "data": "test_data"}
        result = producer._publish_message("test-topic", message, "test-key")
        
        assert result is True
        mock_kafka_manager.get_producer.assert_called_once()
        
        # Verify producer.send was called with correct parameters
        producer_mock = mock_kafka_manager.get_producer.return_value
        producer_mock.send.assert_called_once()
        
        call_args = producer_mock.send.call_args
        assert call_args[1]["topic"] == "test-topic"
        assert call_args[1]["key"] == "test-key"
        
        # Verify envelope structure
        envelope = call_args[1]["value"]
        assert envelope["message_type"] == "test"
        assert envelope["organization_id"] == mock_settings.organization_id
        assert envelope["data"] == message
    
    @patch('messaging.producers.base_producer.logger')
    def test_publish_message_kafka_error(self, mock_logger, mock_kafka_manager):
        """Test message publishing with Kafka error"""
        from kafka.errors import KafkaError
        
        producer = BaseProducer()
        
        # Mock Kafka error
        producer_mock = mock_kafka_manager.get_producer.return_value
        producer_mock.send.side_effect = KafkaError("Connection failed")
        
        message = {"type": "test", "data": "test_data"}
        result = producer._publish_message("test-topic", message)
        
        assert result is False
        mock_logger.error.assert_called()
    
    @patch('messaging.producers.base_producer.logger')
    def test_publish_message_unexpected_error(self, mock_logger, mock_kafka_manager):
        """Test message publishing with unexpected error"""
        producer = BaseProducer()
        
        # Mock unexpected error
        producer_mock = mock_kafka_manager.get_producer.return_value
        producer_mock.send.side_effect = Exception("Unexpected error")
        
        message = {"type": "test", "data": "test_data"}
        result = producer._publish_message("test-topic", message)
        
        assert result is False
        mock_logger.error.assert_called()
    
    @patch('messaging.config.Topics')
    def test_publish_donation_request(self, mock_topics, mock_kafka_manager, mock_settings):
        """Test publishing donation request"""
        mock_topics.DONATION_REQUESTS = "donation-requests"
        
        producer = BaseProducer()
        
        donations = [
            {"category": "ALIMENTOS", "description": "Puré de tomates"}
        ]
        
        result = producer.publish_donation_request("REQ-001", donations)
        
        assert result is True
        
        # Verify message structure
        producer_mock = mock_kafka_manager.get_producer.return_value
        call_args = producer_mock.send.call_args
        envelope = call_args[1]["value"]
        message_data = envelope["data"]
        
        assert message_data["type"] == "donation_request"
        assert message_data["request_id"] == "REQ-001"
        assert message_data["donations"] == donations
        assert message_data["organization_id"] == mock_settings.organization_id
    
    @patch('messaging.config.Topics')
    def test_publish_donation_transfer(self, mock_topics, mock_kafka_manager, mock_settings):
        """Test publishing donation transfer"""
        mock_topics.get_transfer_topic.return_value = "transfer-target-org"
        
        producer = BaseProducer()
        
        donations = [
            {"category": "ALIMENTOS", "description": "Puré de tomates", "quantity": "2kg"}
        ]
        
        result = producer.publish_donation_transfer("target-org", "REQ-001", donations)
        
        assert result is True
        
        # Verify topic selection
        mock_topics.get_transfer_topic.assert_called_once_with("target-org")
        
        # Verify message structure
        producer_mock = mock_kafka_manager.get_producer.return_value
        call_args = producer_mock.send.call_args
        envelope = call_args[1]["value"]
        message_data = envelope["data"]
        
        assert message_data["type"] == "donation_transfer"
        assert message_data["request_id"] == "REQ-001"
        assert message_data["donor_organization"] == mock_settings.organization_id
        assert message_data["donations"] == donations
    
    @patch('messaging.config.Topics')
    def test_publish_donation_offer(self, mock_topics, mock_kafka_manager, mock_settings):
        """Test publishing donation offer"""
        mock_topics.DONATION_OFFERS = "donation-offers"
        
        producer = BaseProducer()
        
        donations = [
            {"category": "ALIMENTOS", "description": "Puré de tomates", "quantity": "2kg"}
        ]
        
        result = producer.publish_donation_offer("OFFER-001", donations)
        
        assert result is True
        
        # Verify message structure
        producer_mock = mock_kafka_manager.get_producer.return_value
        call_args = producer_mock.send.call_args
        envelope = call_args[1]["value"]
        message_data = envelope["data"]
        
        assert message_data["type"] == "donation_offer"
        assert message_data["offer_id"] == "OFFER-001"
        assert message_data["donor_organization"] == mock_settings.organization_id
        assert message_data["donations"] == donations
    
    @patch('messaging.config.Topics')
    def test_publish_request_cancellation(self, mock_topics, mock_kafka_manager, mock_settings):
        """Test publishing request cancellation"""
        mock_topics.REQUEST_CANCELLATIONS = "request-cancellations"
        
        producer = BaseProducer()
        
        result = producer.publish_request_cancellation("REQ-001")
        
        assert result is True
        
        # Verify message structure
        producer_mock = mock_kafka_manager.get_producer.return_value
        call_args = producer_mock.send.call_args
        envelope = call_args[1]["value"]
        message_data = envelope["data"]
        
        assert message_data["type"] == "request_cancellation"
        assert message_data["request_id"] == "REQ-001"
        assert message_data["organization_id"] == mock_settings.organization_id
    
    @patch('messaging.config.Topics')
    def test_publish_event(self, mock_topics, mock_kafka_manager, mock_settings):
        """Test publishing solidarity event"""
        mock_topics.SOLIDARITY_EVENTS = "solidarity-events"
        
        producer = BaseProducer()
        
        event_data = {
            "name": "Campaña de Donación",
            "description": "Recolección de alimentos",
            "event_date": "2024-02-15T09:00:00Z"
        }
        
        result = producer.publish_event("EVENT-001", event_data)
        
        assert result is True
        
        # Verify message structure
        producer_mock = mock_kafka_manager.get_producer.return_value
        call_args = producer_mock.send.call_args
        envelope = call_args[1]["value"]
        message_data = envelope["data"]
        
        assert message_data["type"] == "solidarity_event"
        assert message_data["event_id"] == "EVENT-001"
        assert message_data["name"] == event_data["name"]
        assert message_data["description"] == event_data["description"]
        assert message_data["event_date"] == event_data["event_date"]
        assert message_data["organization_id"] == mock_settings.organization_id
    
    @patch('messaging.config.Topics')
    def test_publish_event_cancellation(self, mock_topics, mock_kafka_manager, mock_settings):
        """Test publishing event cancellation"""
        mock_topics.EVENT_CANCELLATIONS = "event-cancellations"
        
        producer = BaseProducer()
        
        result = producer.publish_event_cancellation("EVENT-001")
        
        assert result is True
        
        # Verify message structure
        producer_mock = mock_kafka_manager.get_producer.return_value
        call_args = producer_mock.send.call_args
        envelope = call_args[1]["value"]
        message_data = envelope["data"]
        
        assert message_data["type"] == "event_cancellation"
        assert message_data["event_id"] == "EVENT-001"
        assert message_data["organization_id"] == mock_settings.organization_id
    
    @patch('messaging.config.Topics')
    def test_publish_event_adhesion(self, mock_topics, mock_kafka_manager, mock_settings):
        """Test publishing event adhesion"""
        mock_topics.get_adhesion_topic.return_value = "adhesion-target-org"
        
        producer = BaseProducer()
        
        volunteer_data = {
            "volunteer_id": "VOL-001",
            "name": "Juan",
            "surname": "Pérez",
            "phone": "+1234567890",
            "email": "juan.perez@example.com"
        }
        
        result = producer.publish_event_adhesion("target-org", "EVENT-001", volunteer_data)
        
        assert result is True
        
        # Verify topic selection
        mock_topics.get_adhesion_topic.assert_called_once_with("target-org")
        
        # Verify message structure
        producer_mock = mock_kafka_manager.get_producer.return_value
        call_args = producer_mock.send.call_args
        envelope = call_args[1]["value"]
        message_data = envelope["data"]
        
        assert message_data["type"] == "event_adhesion"
        assert message_data["event_id"] == "EVENT-001"
        assert message_data["volunteer"]["organization_id"] == mock_settings.organization_id
        assert message_data["volunteer"]["volunteer_id"] == volunteer_data["volunteer_id"]
        assert message_data["volunteer"]["name"] == volunteer_data["name"]
    
    def test_publish_donation_request_validation_failure(self, mock_kafka_manager):
        """Test donation request publishing with validation failure"""
        producer = BaseProducer()
        
        # Missing required field
        result = producer.publish_donation_request("", [])
        
        assert result is False
        
        # Verify no message was sent
        mock_kafka_manager.get_producer.return_value.send.assert_not_called()
    
    def test_publish_donation_transfer_validation_failure(self, mock_kafka_manager):
        """Test donation transfer publishing with validation failure"""
        producer = BaseProducer()
        
        # Missing required field
        result = producer.publish_donation_transfer("target-org", "", [])
        
        assert result is False
        
        # Verify no message was sent
        mock_kafka_manager.get_producer.return_value.send.assert_not_called()
    
    def test_publish_event_validation_failure(self, mock_kafka_manager):
        """Test event publishing with validation failure"""
        producer = BaseProducer()
        
        # Missing required fields
        event_data = {"description": "Test event"}
        result = producer.publish_event("EVENT-001", event_data)
        
        assert result is False
        
        # Verify no message was sent
        mock_kafka_manager.get_producer.return_value.send.assert_not_called()


class TestDonationRequestProducer:
    """Test cases for DonationRequestProducer (if it exists as a separate class)"""
    
    def test_donation_request_producer_inheritance(self):
        """Test that DonationRequestProducer inherits from BaseProducer if it exists"""
        try:
            from messaging.producers.donation_producer import DonationRequestProducer
            producer = DonationRequestProducer()
            assert isinstance(producer, BaseProducer)
        except ImportError:
            # DonationRequestProducer doesn't exist as separate class, skip test
            pytest.skip("DonationRequestProducer class not found")