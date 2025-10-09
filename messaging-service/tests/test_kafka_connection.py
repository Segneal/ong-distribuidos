"""
Unit tests for Kafka connection management
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from kafka.errors import KafkaError, NoBrokersAvailable

from messaging.kafka.connection import KafkaConnectionManager


class TestKafkaConnectionManager:
    """Test cases for KafkaConnectionManager"""
    
    def test_init(self, mock_settings):
        """Test KafkaConnectionManager initialization"""
        manager = KafkaConnectionManager()
        
        assert manager._producer is None
        assert manager._admin_client is None
        assert manager.connection_status == "disconnected"
    
    @patch('messaging.kafka.connection.KafkaProducer')
    @patch('messaging.kafka.connection.logger')
    def test_get_producer_success(self, mock_logger, mock_kafka_producer_class, mock_settings):
        """Test successful producer creation"""
        manager = KafkaConnectionManager()
        
        # Mock successful producer creation
        mock_producer = Mock()
        mock_kafka_producer_class.return_value = mock_producer
        
        result = manager.get_producer()
        
        assert result == mock_producer
        assert manager._producer == mock_producer
        
        # Verify producer was created with correct config
        mock_kafka_producer_class.assert_called_once()
        call_args = mock_kafka_producer_class.call_args
        assert call_args[1]['bootstrap_servers'] == mock_settings.kafka_bootstrap_servers
        assert call_args[1]['acks'] == 'all'
        assert call_args[1]['retries'] == 3
    
    @patch('messaging.kafka.connection.KafkaProducer')
    @patch('messaging.kafka.connection.logger')
    def test_get_producer_cached(self, mock_logger, mock_kafka_producer_class, mock_settings):
        """Test producer caching"""
        manager = KafkaConnectionManager()
        
        # Mock producer
        mock_producer = Mock()
        mock_kafka_producer_class.return_value = mock_producer
        
        # First call
        result1 = manager.get_producer()
        
        # Second call should return cached producer
        result2 = manager.get_producer()
        
        assert result1 == result2
        assert result1 == mock_producer
        
        # Verify producer was only created once
        mock_kafka_producer_class.assert_called_once()
    
    @patch('messaging.kafka.connection.KafkaProducer')
    @patch('messaging.kafka.connection.logger')
    def test_get_producer_error(self, mock_logger, mock_kafka_producer_class):
        """Test producer creation error"""
        manager = KafkaConnectionManager()
        
        # Mock producer creation error
        mock_kafka_producer_class.side_effect = NoBrokersAvailable("No brokers available")
        
        with pytest.raises(NoBrokersAvailable):
            manager.get_producer()
        
        # Verify error was logged
        mock_logger.error.assert_called()
    
    @patch('messaging.kafka.connection.KafkaConsumer')
    @patch('messaging.kafka.connection.logger')
    def test_get_consumer_success(self, mock_logger, mock_kafka_consumer_class, mock_settings):
        """Test successful consumer creation"""
        manager = KafkaConnectionManager()
        
        # Mock successful consumer creation
        mock_consumer = Mock()
        mock_kafka_consumer_class.return_value = mock_consumer
        
        topics = ["topic1", "topic2"]
        result = manager.get_consumer(topics)
        
        assert result == mock_consumer
        
        # Verify consumer was created with correct config
        mock_kafka_consumer_class.assert_called_once_with(
            *topics,
            bootstrap_servers=mock_settings.kafka_bootstrap_servers,
            group_id=mock_settings.kafka_group_id,
            value_deserializer=manager._json_deserializer,
            key_deserializer=manager._string_deserializer,
            auto_offset_reset='earliest',
            enable_auto_commit=False
        )
    
    @patch('messaging.kafka.connection.KafkaConsumer')
    @patch('messaging.kafka.connection.logger')
    def test_get_consumer_error(self, mock_logger, mock_kafka_consumer_class):
        """Test consumer creation error"""
        manager = KafkaConnectionManager()
        
        # Mock consumer creation error
        mock_kafka_consumer_class.side_effect = KafkaError("Connection failed")
        
        with pytest.raises(KafkaError):
            manager.get_consumer(["topic1"])
        
        # Verify error was logged
        mock_logger.error.assert_called()
    
    @patch('messaging.kafka.connection.KafkaAdminClient')
    @patch('messaging.kafka.connection.logger')
    def test_get_admin_client_success(self, mock_logger, mock_admin_client_class, mock_settings):
        """Test successful admin client creation"""
        manager = KafkaConnectionManager()
        
        # Mock successful admin client creation
        mock_admin = Mock()
        mock_admin_client_class.return_value = mock_admin
        
        result = manager.get_admin_client()
        
        assert result == mock_admin
        assert manager._admin_client == mock_admin
        
        # Verify admin client was created with correct config
        mock_admin_client_class.assert_called_once_with(
            bootstrap_servers=mock_settings.kafka_bootstrap_servers
        )
    
    @patch('messaging.kafka.connection.KafkaAdminClient')
    @patch('messaging.kafka.connection.logger')
    def test_get_admin_client_cached(self, mock_logger, mock_admin_client_class):
        """Test admin client caching"""
        manager = KafkaConnectionManager()
        
        # Mock admin client
        mock_admin = Mock()
        mock_admin_client_class.return_value = mock_admin
        
        # First call
        result1 = manager.get_admin_client()
        
        # Second call should return cached admin client
        result2 = manager.get_admin_client()
        
        assert result1 == result2
        assert result1 == mock_admin
        
        # Verify admin client was only created once
        mock_admin_client_class.assert_called_once()
    
    @patch('messaging.kafka.connection.NewTopic')
    @patch('messaging.kafka.connection.logger')
    def test_create_topics_if_not_exist_success(self, mock_logger, mock_new_topic_class):
        """Test successful topic creation"""
        manager = KafkaConnectionManager()
        
        # Mock admin client
        mock_admin = Mock()
        manager._admin_client = mock_admin
        
        # Mock successful topic creation
        mock_admin.create_topics.return_value = {}
        
        # Mock NewTopic creation
        mock_topic = Mock()
        mock_new_topic_class.return_value = mock_topic
        
        topics = ["topic1", "topic2"]
        manager.create_topics_if_not_exist(topics)
        
        # Verify topics were created
        assert mock_new_topic_class.call_count == 2
        mock_admin.create_topics.assert_called_once()
    
    @patch('messaging.kafka.connection.NewTopic')
    @patch('messaging.kafka.connection.logger')
    def test_create_topics_if_not_exist_already_exists(self, mock_logger, mock_new_topic_class):
        """Test topic creation when topics already exist"""
        from kafka.errors import TopicAlreadyExistsError
        
        manager = KafkaConnectionManager()
        
        # Mock admin client
        mock_admin = Mock()
        manager._admin_client = mock_admin
        
        # Mock topic already exists error
        mock_admin.create_topics.side_effect = TopicAlreadyExistsError("Topic exists")
        
        topics = ["topic1"]
        manager.create_topics_if_not_exist(topics)
        
        # Verify warning was logged
        mock_logger.warning.assert_called()
    
    @patch('messaging.kafka.connection.NewTopic')
    @patch('messaging.kafka.connection.logger')
    def test_create_topics_if_not_exist_error(self, mock_logger, mock_new_topic_class):
        """Test topic creation with error"""
        manager = KafkaConnectionManager()
        
        # Mock admin client
        mock_admin = Mock()
        manager._admin_client = mock_admin
        
        # Mock creation error
        mock_admin.create_topics.side_effect = KafkaError("Creation failed")
        
        topics = ["topic1"]
        manager.create_topics_if_not_exist(topics)
        
        # Verify error was logged
        mock_logger.error.assert_called()
    

class TestKafkaManagerSingleton:
    """Test cases for KafkaManager singleton behavior"""
    
    def test_kafka_manager_singleton(self):
        """Test that kafka_manager is a singleton"""
        from messaging.kafka.connection import kafka_manager
        
        # Get another reference
        from messaging.kafka.connection import kafka_manager as kafka_manager2
        
        # Should be the same instance
        assert kafka_manager is kafka_manager2
    
    def test_kafka_manager_instance(self):
        """Test kafka_manager instance type"""
        from messaging.kafka.connection import kafka_manager
        
        assert isinstance(kafka_manager, KafkaManager)