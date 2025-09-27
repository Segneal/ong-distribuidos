import json
import threading
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Optional
from kafka.errors import KafkaError, CommitFailedError
import structlog

from .kafka_connection import kafka_manager
from .config import settings

logger = structlog.get_logger(__name__)


class BaseConsumer(ABC):
    """Base class for Kafka message consumers"""
    
    def __init__(self, topics: List[str]):
        self.topics = topics
        self.organization_id = settings.organization_id
        self._consumer = None
        self._running = False
        self._thread = None
        self._message_handlers: Dict[str, Callable] = {}
        self._error_handlers: Dict[str, Callable] = {}
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register handler for specific message type"""
        self._message_handlers[message_type] = handler
        logger.info("Registered message handler", message_type=message_type)
    
    def register_error_handler(self, error_type: str, handler: Callable):
        """Register handler for specific error type"""
        self._error_handlers[error_type] = handler
        logger.info("Registered error handler", error_type=error_type)
    
    def _validate_message_envelope(self, message: Dict[str, Any]) -> bool:
        """Validate message envelope structure"""
        required_fields = ["message_id", "message_type", "organization_id", "timestamp", "data"]
        
        for field in required_fields:
            if field not in message:
                logger.error("Invalid message envelope: missing field", field=field)
                return False
        
        return True
    
    def _should_process_message(self, message: Dict[str, Any]) -> bool:
        """Determine if message should be processed (filter own messages)"""
        sender_org = message.get("organization_id")
        
        # Skip messages from our own organization
        if sender_org == self.organization_id:
            logger.debug("Skipping own message", sender_org=sender_org)
            return False
        
        return True
    
    def _process_message(self, message: Dict[str, Any]):
        """Process individual message"""
        try:
            # Validate message envelope
            if not self._validate_message_envelope(message):
                logger.error("Invalid message envelope", message=message)
                return
            
            # Check if we should process this message
            if not self._should_process_message(message):
                return
            
            message_type = message.get("message_type")
            message_data = message.get("data", {})
            
            logger.info(
                "Processing message",
                message_id=message.get("message_id"),
                message_type=message_type,
                sender_org=message.get("organization_id")
            )
            
            # Find and execute handler
            if message_type in self._message_handlers:
                handler = self._message_handlers[message_type]
                handler(message_data)
                logger.info("Message processed successfully", message_type=message_type)
            else:
                logger.warning("No handler found for message type", message_type=message_type)
                self._handle_unknown_message(message_data)
            
        except Exception as e:
            logger.error(
                "Error processing message",
                error=str(e),
                error_type=type(e).__name__,
                message=message
            )
            self._handle_processing_error(e, message)
    
    def _handle_unknown_message(self, message_data: Dict[str, Any]):
        """Handle messages with unknown types"""
        logger.warning("Received unknown message type", message_data=message_data)
    
    def _handle_processing_error(self, error: Exception, message: Dict[str, Any]):
        """Handle errors during message processing"""
        error_type = type(error).__name__
        
        if error_type in self._error_handlers:
            try:
                handler = self._error_handlers[error_type]
                handler(error, message)
            except Exception as handler_error:
                logger.error(
                    "Error in error handler",
                    handler_error=str(handler_error),
                    original_error=str(error)
                )
        else:
            logger.error("Unhandled processing error", error=str(error), error_type=error_type)
    
    def _consume_loop(self):
        """Main consumption loop"""
        logger.info("Starting consumer loop", topics=self.topics)
        
        try:
            # Create topics if needed
            kafka_manager.create_topics_if_not_exist(self.topics)
            
            # Get consumer
            self._consumer = kafka_manager.get_consumer(self.topics)
            
            while self._running:
                try:
                    # Poll for messages
                    message_batch = self._consumer.poll(timeout_ms=1000)
                    
                    if not message_batch:
                        continue
                    
                    # Process messages
                    for topic_partition, messages in message_batch.items():
                        for message in messages:
                            if not self._running:
                                break
                            
                            try:
                                if message.value:
                                    self._process_message(message.value)
                            except Exception as e:
                                logger.error(
                                    "Error processing individual message",
                                    error=str(e),
                                    topic=topic_partition.topic,
                                    partition=topic_partition.partition,
                                    offset=message.offset
                                )
                    
                    # Commit offsets
                    try:
                        self._consumer.commit()
                    except CommitFailedError as e:
                        logger.error("Failed to commit offsets", error=str(e))
                
                except KafkaError as e:
                    logger.error("Kafka error in consumer loop", error=str(e))
                    time.sleep(5)  # Wait before retrying
                except Exception as e:
                    logger.error("Unexpected error in consumer loop", error=str(e))
                    time.sleep(5)  # Wait before retrying
        
        except Exception as e:
            logger.error("Fatal error in consumer loop", error=str(e))
        finally:
            if self._consumer:
                try:
                    self._consumer.close()
                except Exception as e:
                    logger.error("Error closing consumer", error=str(e))
            logger.info("Consumer loop ended")
    
    def start(self):
        """Start the consumer in a separate thread"""
        if self._running:
            logger.warning("Consumer already running")
            return
        
        logger.info("Starting consumer", topics=self.topics)
        self._running = True
        self._thread = threading.Thread(target=self._consume_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the consumer"""
        if not self._running:
            logger.warning("Consumer not running")
            return
        
        logger.info("Stopping consumer")
        self._running = False
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=10)
            if self._thread.is_alive():
                logger.warning("Consumer thread did not stop gracefully")
    
    def is_running(self) -> bool:
        """Check if consumer is running"""
        return self._running
    
    @abstractmethod
    def setup_handlers(self):
        """Setup message handlers - must be implemented by subclasses"""
        pass


class NetworkConsumer(BaseConsumer):
    """Consumer for network-wide messages"""
    
    def __init__(self):
        from .config import Topics
        topics = [
            Topics.DONATION_REQUESTS,
            Topics.DONATION_OFFERS,
            Topics.REQUEST_CANCELLATIONS,
            Topics.SOLIDARITY_EVENTS,
            Topics.EVENT_CANCELLATIONS
        ]
        super().__init__(topics)
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup handlers for network messages"""
        self.register_message_handler("donation_request", self._handle_donation_request)
        self.register_message_handler("donation_offer", self._handle_donation_offer)
        self.register_message_handler("request_cancellation", self._handle_request_cancellation)
        self.register_message_handler("solidarity_event", self._handle_solidarity_event)
        self.register_message_handler("event_cancellation", self._handle_event_cancellation)
    
    def _handle_donation_request(self, message_data: Dict[str, Any]):
        """Handle incoming donation request"""
        logger.info("Handling donation request", data=message_data)
        
        # Use the dedicated donation request consumer logic
        from .donation_request_consumer import DonationRequestConsumer
        consumer = DonationRequestConsumer()
        
        # Create a message envelope for processing
        message_envelope = {
            "message_id": "network-consumer-msg",
            "message_type": "donation_request",
            "organization_id": message_data.get("organization_id"),
            "timestamp": message_data.get("timestamp"),
            "data": message_data
        }
        
        consumer.process_message(message_envelope)
    
    def _handle_donation_offer(self, message_data: Dict[str, Any]):
        """Handle incoming donation offer"""
        logger.info("Handling donation offer", data=message_data)
        # TODO: Implement donation offer handling
    
    def _handle_request_cancellation(self, message_data: Dict[str, Any]):
        """Handle request cancellation"""
        logger.info("Handling request cancellation", data=message_data)
        
        # Use the dedicated request cancellation consumer logic
        from .request_cancellation_consumer import RequestCancellationConsumer
        consumer = RequestCancellationConsumer()
        
        # Create a message envelope for processing
        message_envelope = {
            "message_id": "network-consumer-msg",
            "message_type": "request_cancellation",
            "organization_id": message_data.get("organization_id"),
            "timestamp": message_data.get("timestamp"),
            "data": message_data
        }
        
        consumer.process_message(message_envelope)
    
    def _handle_solidarity_event(self, message_data: Dict[str, Any]):
        """Handle incoming solidarity event"""
        logger.info("Handling solidarity event", data=message_data)
        # TODO: Implement solidarity event handling
    
    def _handle_event_cancellation(self, message_data: Dict[str, Any]):
        """Handle event cancellation"""
        logger.info("Handling event cancellation", data=message_data)
        # TODO: Implement event cancellation handling


class OrganizationConsumer(BaseConsumer):
    """Consumer for organization-specific messages"""
    
    def __init__(self):
        from .config import Topics
        topics = [
            Topics.get_transfer_topic(settings.organization_id),
            Topics.get_adhesion_topic(settings.organization_id)
        ]
        super().__init__(topics)
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup handlers for organization-specific messages"""
        self.register_message_handler("donation_transfer", self._handle_donation_transfer)
        self.register_message_handler("event_adhesion", self._handle_event_adhesion)
    
    def _handle_donation_transfer(self, message_data: Dict[str, Any]):
        """Handle incoming donation transfer"""
        logger.info("Handling donation transfer", data=message_data)
        # TODO: Implement donation transfer handling
    
    def _handle_event_adhesion(self, message_data: Dict[str, Any]):
        """Handle incoming event adhesion"""
        logger.info("Handling event adhesion", data=message_data)
        # TODO: Implement event adhesion handling