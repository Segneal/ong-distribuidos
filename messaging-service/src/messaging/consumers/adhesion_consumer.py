"""
Consumer for processing event adhesion messages
"""
import json
from typing import Dict, Any
import structlog

from .base_consumer import BaseConsumer
from ..services.adhesion_service import AdhesionService
from ..services.notification_service import NotificationService
from ..config import Topics

logger = structlog.get_logger(__name__)


class AdhesionConsumer(BaseConsumer):
    """Consumer for processing event adhesion messages"""
    
    def __init__(self):
        # Subscribe to our organization's adhesion topic
        from ..config import settings
        topic = Topics.get_adhesion_topic(settings.organization_id)
        super().__init__([topic])  # BaseConsumer expects a list of topics
        self.adhesion_service = AdhesionService()
        self.notification_service = NotificationService()
        self.topic = topic  # Store for compatibility
        self.setup_handlers()
    
    def process_message(self, message_envelope: Dict[str, Any]):
        """Process adhesion message"""
        try:
            message_data = message_envelope.get("data", {})
            message_type = message_data.get("type")
            
            if message_type != "event_adhesion":
                logger.warning("Unexpected message type", type=message_type)
                return
            
            logger.info(
                "Processing event adhesion message",
                event_id=message_data.get("event_id"),
                volunteer_org=message_data.get("volunteer", {}).get("organization_id")
            )
            
            # Process the adhesion
            success = self.adhesion_service.process_incoming_adhesion(message_data)
            
            if success:
                # Send notification to administrators
                volunteer = message_data.get("volunteer", {})
                volunteer_name = f"{volunteer.get('name', '')} {volunteer.get('surname', '')}".strip()
                volunteer_email = volunteer.get("email", "")
                volunteer_org = volunteer.get("organization_id", "")
                event_id = message_data.get("event_id", "")
                
                self.notification_service.notify_new_event_adhesion(
                    event_id, volunteer_name, volunteer_email, volunteer_org
                )
                
                logger.info(
                    "Event adhesion processed and notification sent",
                    event_id=event_id,
                    volunteer_org=volunteer_org
                )
            else:
                logger.error("Failed to process event adhesion")
                
        except Exception as e:
            logger.error(
                "Error processing adhesion message",
                error=str(e),
                message=message_envelope
            )
    
    def setup_handlers(self):
        """Setup message handlers"""
        self.register_message_handler("event_adhesion", self._handle_event_adhesion)
    
    def _handle_event_adhesion(self, message_data: Dict[str, Any]):
        """Handle event adhesion message"""
        self.process_message({"data": message_data})
    
    def get_consumer_group(self) -> str:
        """Get consumer group ID"""
        from ..config import settings
        return f"{settings.organization_id}-adhesion-consumer"