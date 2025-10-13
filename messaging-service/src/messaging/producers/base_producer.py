import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from kafka.errors import KafkaError
import structlog

from ..kafka.connection import kafka_manager
from ..config import settings

logger = structlog.get_logger(__name__)


class BaseProducer:
    """Base class for Kafka message producers"""
    
    def __init__(self):
        self.organization_id = settings.organization_id
    
    def _create_message_envelope(self, message_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create standardized message envelope"""
        return {
            "message_id": str(uuid.uuid4()),
            "message_type": message_type,
            "organization_id": self.organization_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
    
    def _publish_message(self, topic: str, message: Dict[str, Any], key: Optional[str] = None) -> bool:
        """Publish message to Kafka topic with error handling"""
        try:
            producer = kafka_manager.get_producer()
            
            # Create message envelope
            envelope = self._create_message_envelope(
                message_type=message.get("type", "unknown"),
                data=message
            )
            
            # Use organization_id as default key if not provided
            message_key = key or self.organization_id
            
            logger.info(
                "Publishing message",
                topic=topic,
                message_id=envelope["message_id"],
                message_type=envelope["message_type"],
                key=message_key
            )
            
            # Send message
            future = producer.send(
                topic=topic,
                value=envelope,
                key=message_key
            )
            
            # Wait for confirmation
            record_metadata = future.get(timeout=30)
            
            logger.info(
                "Message published successfully",
                topic=record_metadata.topic,
                partition=record_metadata.partition,
                offset=record_metadata.offset,
                message_id=envelope["message_id"]
            )
            
            return True
            
        except KafkaError as e:
            logger.error(
                "Kafka error publishing message",
                topic=topic,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
        except Exception as e:
            logger.error(
                "Unexpected error publishing message",
                topic=topic,
                error=str(e),
                error_type=type(e).__name__
            )
            return False
    
    def _validate_message(self, message: Dict[str, Any], required_fields: list) -> bool:
        """Validate message contains required fields"""
        for field in required_fields:
            if field not in message:
                logger.error("Missing required field in message", field=field, message=message)
                return False
        return True
    
    def publish_donation_request(self, request_id: str, donations: list) -> bool:
        """Publish donation request message"""
        message = {
            "type": "donation_request",
            "organization_id": self.organization_id,
            "request_id": request_id,
            "donations": donations,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if not self._validate_message(message, ["request_id", "donations"]):
            return False
        
        from ..config import Topics
        return self._publish_message(Topics.DONATION_REQUESTS, message)
    
    def publish_donation_transfer(self, target_org: str, transfer_data: Dict[str, Any]) -> bool:
        """Publish donation transfer message"""
        # Create message data
        message_data = {
            "type": "donation_transfer",
            "transfer_id": transfer_data.get("transfer_id"),
            "request_id": transfer_data.get("request_id"),
            "source_organization": transfer_data.get("source_organization"),
            "target_organization": transfer_data.get("target_organization"),
            "donations": transfer_data.get("donations"),
            "timestamp": transfer_data.get("timestamp"),
            "user_id": transfer_data.get("user_id")
        }
        
        if not self._validate_message(message_data, ["transfer_id", "request_id", "donations"]):
            return False
        
        from ..config import Topics
        topic = Topics.get_transfer_topic(target_org)
        return self._publish_message(topic, message_data)
    
    def publish_donation_offer(self, offer_id: str, donations: list) -> bool:
        """Publish donation offer message"""
        message = {
            "type": "donation_offer",
            "offer_id": offer_id,
            "donor_organization": self.organization_id,
            "donations": donations,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if not self._validate_message(message, ["offer_id", "donations"]):
            return False
        
        from ..config import Topics
        return self._publish_message(Topics.DONATION_OFFERS, message)
    
    def publish_request_cancellation(self, request_id: str) -> bool:
        """Publish request cancellation message"""
        message = {
            "type": "request_cancellation",
            "organization_id": self.organization_id,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if not self._validate_message(message, ["request_id"]):
            return False
        
        from ..config import Topics
        return self._publish_message(Topics.REQUEST_CANCELLATIONS, message)
    
    def publish_event(self, event_id: str, event_data: Dict[str, Any]) -> bool:
        """Publish solidarity event message"""
        message = {
            "type": "solidarity_event",
            "organization_id": self.organization_id,
            "event_id": event_id,
            "name": event_data.get("name"),
            "description": event_data.get("description"),
            "event_date": event_data.get("event_date"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if not self._validate_message(message, ["event_id", "name", "event_date"]):
            return False
        
        from ..config import Topics
        return self._publish_message(Topics.SOLIDARITY_EVENTS, message)
    
    def publish_event_cancellation(self, event_id: str) -> bool:
        """Publish event cancellation message"""
        message = {
            "type": "event_cancellation",
            "organization_id": self.organization_id,
            "event_id": event_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if not self._validate_message(message, ["event_id"]):
            return False
        
        from ..config import Topics
        return self._publish_message(Topics.EVENT_CANCELLATIONS, message)
    
    def publish_event_adhesion(self, target_org: str, event_id: str, volunteer_data: Dict[str, Any]) -> bool:
        """Publish event adhesion message"""
        message = {
            "type": "event_adhesion",
            "event_id": event_id,
            "volunteer": {
                "organization_id": self.organization_id,
                "volunteer_id": volunteer_data.get("volunteer_id"),
                "name": volunteer_data.get("name"),
                "surname": volunteer_data.get("surname"),
                "phone": volunteer_data.get("phone"),
                "email": volunteer_data.get("email")
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if not self._validate_message(message, ["event_id", "volunteer"]):
            return False
        
        from ..config import Topics
        topic = Topics.get_adhesion_topic(target_org)
        return self._publish_message(topic, message)