import logging
import time
from typing import Optional, Dict, Any
try:
    from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
    from kafka.admin import ConfigResource, ConfigResourceType, NewTopic
    from kafka.errors import KafkaError, NoBrokersAvailable, KafkaConnectionError
except ImportError:
    # Fallback for development/testing without Kafka
    class MockKafka:
        pass
    KafkaProducer = KafkaConsumer = KafkaAdminClient = MockKafka
    ConfigResource = ConfigResourceType = NewTopic = MockKafka
    KafkaError = NoBrokersAvailable = KafkaConnectionError = Exception
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import json
import structlog

from ..config import settings

logger = structlog.get_logger(__name__)


class KafkaConnectionManager:
    """Manages Kafka connections with automatic retry and error handling"""
    
    def __init__(self):
        self._producer: Optional[KafkaProducer] = None
        self._consumer: Optional[KafkaConsumer] = None
        self._admin_client: Optional[KafkaAdminClient] = None
        self._connection_status = "disconnected"
        self._last_error: Optional[str] = None
    
    @property
    def connection_status(self) -> str:
        return self._connection_status
    
    @property
    def last_error(self) -> Optional[str]:
        return self._last_error
    
    @retry(
        stop=stop_after_attempt(settings.kafka_retry_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=settings.kafka_retry_delay / 1000,
            max=settings.kafka_max_retry_delay / 1000
        ),
        retry=retry_if_exception_type((NoBrokersAvailable, KafkaConnectionError))
    )
    def _create_producer(self) -> KafkaProducer:
        """Create Kafka producer with retry logic"""
        logger.info("Creating Kafka producer", brokers=settings.kafka_bootstrap_servers)
        
        producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',
            retries=3,
            max_in_flight_requests_per_connection=1,
            request_timeout_ms=30000,
            retry_backoff_ms=100
        )
        
        # Test connection
        producer.bootstrap_connected()
        logger.info("Kafka producer created successfully")
        return producer
    
    @retry(
        stop=stop_after_attempt(settings.kafka_retry_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=settings.kafka_retry_delay / 1000,
            max=settings.kafka_max_retry_delay / 1000
        ),
        retry=retry_if_exception_type((NoBrokersAvailable, KafkaConnectionError))
    )
    def _create_consumer(self, topics: list) -> KafkaConsumer:
        """Create Kafka consumer with retry logic"""
        logger.info("Creating Kafka consumer", topics=topics, group_id=settings.kafka_group_id)
        
        consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            auto_commit_interval_ms=1000,
            session_timeout_ms=30000,
            heartbeat_interval_ms=3000,
            max_poll_records=10,
            max_poll_interval_ms=300000
        )
        
        logger.info("Kafka consumer created successfully")
        return consumer
    
    @retry(
        stop=stop_after_attempt(settings.kafka_retry_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=settings.kafka_retry_delay / 1000,
            max=settings.kafka_max_retry_delay / 1000
        ),
        retry=retry_if_exception_type((NoBrokersAvailable, KafkaConnectionError))
    )
    def _create_admin_client(self) -> KafkaAdminClient:
        """Create Kafka admin client with retry logic"""
        logger.info("Creating Kafka admin client", brokers=settings.kafka_bootstrap_servers)
        
        admin_client = KafkaAdminClient(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            client_id=f"{settings.organization_id}-admin"
        )
        
        logger.info("Kafka admin client created successfully")
        return admin_client
    
    def get_producer(self) -> KafkaProducer:
        """Get or create Kafka producer"""
        if self._producer is None:
            try:
                self._producer = self._create_producer()
                self._connection_status = "connected"
                self._last_error = None
            except Exception as e:
                self._connection_status = "error"
                self._last_error = str(e)
                logger.error("Failed to create Kafka producer", error=str(e))
                raise
        
        return self._producer
    
    def get_consumer(self, topics: list) -> KafkaConsumer:
        """Get or create Kafka consumer for specific topics"""
        try:
            consumer = self._create_consumer(topics)
            self._connection_status = "connected"
            self._last_error = None
            return consumer
        except Exception as e:
            self._connection_status = "error"
            self._last_error = str(e)
            logger.error("Failed to create Kafka consumer", error=str(e), topics=topics)
            raise
    
    def get_admin_client(self) -> KafkaAdminClient:
        """Get or create Kafka admin client"""
        if self._admin_client is None:
            try:
                self._admin_client = self._create_admin_client()
                self._connection_status = "connected"
                self._last_error = None
            except Exception as e:
                self._connection_status = "error"
                self._last_error = str(e)
                logger.error("Failed to create Kafka admin client", error=str(e))
                raise
        
        return self._admin_client
    
    def create_topics_if_not_exist(self, topic_names: list):
        """Create topics if they don't exist"""
        if not settings.kafka_auto_create_topics:
            logger.info("Auto topic creation disabled")
            return
        
        try:
            admin_client = self.get_admin_client()
            
            # Get existing topics
            existing_topics = admin_client.list_topics()
            
            # Create topics that don't exist
            topics_to_create = []
            for topic_name in topic_names:
                if topic_name not in existing_topics:
                    topic = NewTopic(
                        name=topic_name,
                        num_partitions=1,
                        replication_factor=settings.kafka_replication_factor
                    )
                    topics_to_create.append(topic)
            
            if topics_to_create:
                logger.info("Creating topics", topics=[t.name for t in topics_to_create])
                result = admin_client.create_topics(topics_to_create)
                
                # Wait for topic creation
                for topic_name, future in result.items():
                    try:
                        future.result()
                        logger.info("Topic created successfully", topic=topic_name)
                    except Exception as e:
                        logger.error("Failed to create topic", topic=topic_name, error=str(e))
            else:
                logger.info("All topics already exist")
                
        except Exception as e:
            logger.error("Failed to create topics", error=str(e))
            raise
    
    def close_connections(self):
        """Close all Kafka connections"""
        logger.info("Closing Kafka connections")
        
        if self._producer:
            try:
                self._producer.close()
                logger.info("Producer closed")
            except Exception as e:
                logger.error("Error closing producer", error=str(e))
            finally:
                self._producer = None
        
        if self._consumer:
            try:
                self._consumer.close()
                logger.info("Consumer closed")
            except Exception as e:
                logger.error("Error closing consumer", error=str(e))
            finally:
                self._consumer = None
        
        if self._admin_client:
            try:
                self._admin_client.close()
                logger.info("Admin client closed")
            except Exception as e:
                logger.error("Error closing admin client", error=str(e))
            finally:
                self._admin_client = None
        
        self._connection_status = "disconnected"
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on Kafka connections"""
        try:
            producer = self.get_producer()
            # Try to get metadata as a simple health check
            metadata = producer.bootstrap_connected()
            
            return {
                "status": "healthy",
                "connection_status": self._connection_status,
                "brokers": settings.kafka_bootstrap_servers,
                "organization_id": settings.organization_id,
                "last_error": self._last_error
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connection_status": "error",
                "brokers": settings.kafka_bootstrap_servers,
                "organization_id": settings.organization_id,
                "last_error": str(e)
            }


# Global connection manager instance
kafka_manager = KafkaConnectionManager()