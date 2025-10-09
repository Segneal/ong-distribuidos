"""
Pytest configuration and fixtures for messaging service tests
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import json
from datetime import datetime
from typing import Dict, Any, List


@pytest.fixture
def mock_kafka_producer():
    """Mock Kafka producer for testing"""
    producer = Mock()
    producer.send.return_value = Mock()
    producer.send.return_value.get.return_value = Mock(
        topic="test-topic",
        partition=0,
        offset=123
    )
    return producer


@pytest.fixture
def mock_kafka_consumer():
    """Mock Kafka consumer for testing"""
    consumer = Mock()
    consumer.poll.return_value = {}
    consumer.commit.return_value = None
    consumer.close.return_value = None
    return consumer


@pytest.fixture
def mock_kafka_manager(mock_kafka_producer, mock_kafka_consumer):
    """Mock Kafka manager for testing"""
    manager = Mock()
    manager.get_producer.return_value = mock_kafka_producer
    manager.get_consumer.return_value = mock_kafka_consumer
    manager.create_topics_if_not_exist.return_value = None
    return manager


@pytest.fixture
def mock_database_connection():
    """Mock database connection for testing"""
    connection = Mock()
    cursor = Mock()
    connection.cursor.return_value = cursor
    cursor.fetchall.return_value = []
    cursor.fetchone.return_value = None
    cursor.execute.return_value = None
    return connection


@pytest.fixture
def sample_donation_request():
    """Sample donation request data for testing"""
    return {
        "organization_id": "test-org",
        "request_id": "REQ-001",
        "donations": [
            {
                "category": "ALIMENTOS",
                "description": "Puré de tomates"
            },
            {
                "category": "ROPA",
                "description": "Camisetas talla M"
            }
        ],
        "timestamp": "2024-01-15T10:30:00Z"
    }


@pytest.fixture
def sample_donation_offer():
    """Sample donation offer data for testing"""
    return {
        "offer_id": "OFFER-001",
        "donor_organization": "test-org",
        "donations": [
            {
                "category": "ALIMENTOS",
                "description": "Puré de tomates",
                "quantity": "2kg"
            }
        ],
        "timestamp": "2024-01-15T11:00:00Z"
    }


@pytest.fixture
def sample_donation_transfer():
    """Sample donation transfer data for testing"""
    return {
        "request_id": "REQ-001",
        "donor_organization": "test-org",
        "donations": [
            {
                "category": "ALIMENTOS",
                "description": "Puré de tomates",
                "quantity": "2kg"
            }
        ],
        "timestamp": "2024-01-15T11:30:00Z"
    }


@pytest.fixture
def sample_event_data():
    """Sample event data for testing"""
    return {
        "organization_id": "test-org",
        "event_id": "EVENT-001",
        "name": "Campaña de Donación",
        "description": "Recolección de alimentos",
        "event_date": "2024-02-15T09:00:00Z",
        "timestamp": "2024-01-15T12:00:00Z"
    }


@pytest.fixture
def sample_volunteer_data():
    """Sample volunteer data for testing"""
    return {
        "volunteer_id": "VOL-001",
        "name": "Juan",
        "surname": "Pérez",
        "phone": "+1234567890",
        "email": "juan.perez@example.com"
    }


@pytest.fixture
def mock_message_envelope():
    """Mock message envelope for testing"""
    return {
        "message_id": "msg-123",
        "message_type": "donation_request",
        "organization_id": "test-org",
        "timestamp": "2024-01-15T10:30:00Z",
        "data": {
            "request_id": "REQ-001",
            "donations": []
        }
    }


@pytest.fixture
def mock_settings():
    """Mock settings for testing"""
    settings = Mock()
    settings.organization_id = "test-org"
    settings.kafka_brokers = "localhost:9092"
    settings.kafka_group_id = "test-group"
    return settings


@pytest.fixture(autouse=True)
def patch_kafka_manager(mock_kafka_manager):
    """Auto-patch kafka manager for all tests"""
    with patch('messaging.kafka.connection.kafka_manager', mock_kafka_manager):
        yield mock_kafka_manager


@pytest.fixture(autouse=True)
def patch_settings(mock_settings):
    """Auto-patch settings for all tests"""
    with patch('messaging.config.settings', mock_settings):
        yield mock_settings


class MockKafkaMessage:
    """Mock Kafka message for testing consumers"""
    
    def __init__(self, value: Dict[str, Any], topic: str = "test-topic", partition: int = 0, offset: int = 0):
        self.value = value
        self.topic = topic
        self.partition = partition
        self.offset = offset


class MockTopicPartition:
    """Mock Kafka TopicPartition for testing"""
    
    def __init__(self, topic: str, partition: int):
        self.topic = topic
        self.partition = partition