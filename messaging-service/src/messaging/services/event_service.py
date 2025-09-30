"""
Event Service for managing solidarity events in the ONG network
Handles creation, publishing, and management of solidarity events
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import structlog
import sys
import os

# Import network repository
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from network_repository import NetworkRepository

# Add events service to path for event validation
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'events-service', 'src'))

from ..producers.base_producer import BaseProducer
from ..config import settings

logger = structlog.get_logger(__name__)


class EventService:
    """Service for managing solidarity events in the network"""
    
    def __init__(self):
        self.network_repo = NetworkRepository()
        self.producer = BaseProducer()
        self.organization_id = settings.organization_id
    
    def publish_event(self, event_id: str, name: str, description: str, 
                     event_date: str, user_id: int) -> Tuple[bool, str]:
        """
        Publish a solidarity event to the network
        
        Args:
            event_id: ID of the event to publish
            name: Event name
            description: Event description
            event_date: Event date in ISO format
            user_id: ID of the user publishing the event
            
        Returns:
            Tuple of (success, message)
        """
        try:
            logger.info(
                "Publishing solidarity event",
                event_id=event_id,
                name=name,
                event_date=event_date,
                user_id=user_id
            )
            
            # Validate event data
            if not all([event_id, name, event_date]):
                return False, "Event ID, name, and date are required"
            
            # Validate event date is in the future
            try:
                event_datetime = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
                if event_datetime <= datetime.now():
                    return False, "Event date must be in the future"
            except ValueError:
                return False, "Invalid event date format"
            
            # Prepare event data
            event_data = {
                "name": name,
                "description": description or "",
                "event_date": event_date
            }
            
            # Publish event to Kafka
            success = self.producer.publish_event(event_id, event_data)
            
            if not success:
                return False, "Failed to publish event to network"
            
            logger.info(
                "Solidarity event published successfully",
                event_id=event_id,
                organization_id=self.organization_id
            )
            
            return True, f"Event {event_id} published successfully to the network"
            
        except Exception as e:
            logger.error(
                "Error publishing solidarity event",
                error=str(e),
                event_id=event_id,
                user_id=user_id
            )
            return False, f"Internal error: {str(e)}"
    
    def get_external_events(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get external solidarity events from other organizations
        
        Args:
            active_only: If True, only return active events
            
        Returns:
            List of external events
        """
        try:
            logger.info("Getting external solidarity events", active_only=active_only)
            
            if active_only:
                events = self.network_repo.get_active_external_events()
            else:
                # For now, we only support active events
                events = self.network_repo.get_active_external_events()
            
            # Format response
            formatted_events = []
            for event in events:
                try:
                    formatted_events.append({
                        'id': event['id'],
                        'organization_id': event['organizacion_id'],
                        'event_id': event['evento_id'],
                        'name': event['nombre'],
                        'description': event['descripcion'],
                        'event_date': event['fecha_evento'].isoformat() if event['fecha_evento'] else None,
                        'created_at': event['fecha_creacion'].isoformat() if event['fecha_creacion'] else None
                    })
                except Exception as e:
                    logger.error(
                        "Error parsing event data",
                        event_id=event.get('evento_id'),
                        error=str(e)
                    )
                    continue
            
            logger.info(
                "Retrieved external events",
                count=len(formatted_events)
            )
            
            return formatted_events
            
        except Exception as e:
            logger.error("Error getting external events", error=str(e))
            return []
    
    def process_external_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process an external event received from Kafka
        
        Args:
            event_data: Event data from Kafka message
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            logger.info(
                "Processing external event",
                event_id=event_data.get('event_id'),
                organization=event_data.get('organization_id')
            )
            
            # Skip our own events
            if event_data.get('organization_id') == self.organization_id:
                logger.info("Skipping own event", event_id=event_data.get('event_id'))
                return True
            
            # Validate required fields
            required_fields = ['event_id', 'organization_id', 'name', 'event_date']
            for field in required_fields:
                if field not in event_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate event date is in the future
            try:
                event_datetime = datetime.fromisoformat(event_data['event_date'].replace('Z', '+00:00'))
                if event_datetime <= datetime.now():
                    logger.info(
                        "Skipping past event",
                        event_id=event_data['event_id'],
                        event_date=event_data['event_date']
                    )
                    return True
            except ValueError:
                logger.error(
                    "Invalid event date format",
                    event_id=event_data['event_id'],
                    event_date=event_data['event_date']
                )
                return False
            
            # Check if event already exists
            existing_event = self.network_repo.get_external_event_by_id(
                event_data['organization_id'],
                event_data['event_id']
            )
            
            if existing_event:
                logger.info(
                    "Event already exists",
                    event_id=event_data['event_id'],
                    organization=event_data['organization_id']
                )
                return True
            
            # Store external event
            result = self.network_repo.create_external_event(
                event_data['organization_id'],
                event_data['event_id'],
                event_data['name'],
                event_data.get('description', ''),
                event_data['event_date']
            )
            
            if result:
                logger.info(
                    "External event stored successfully",
                    event_id=event_data['event_id'],
                    organization=event_data['organization_id'],
                    db_id=result['id']
                )
                return True
            else:
                logger.error(
                    "Failed to store external event",
                    event_id=event_data['event_id']
                )
                return False
                
        except Exception as e:
            logger.error(
                "Error processing external event",
                event_id=event_data.get('event_id'),
                error=str(e)
            )
            return False
    
    def cancel_event(self, event_id: str, user_id: int) -> Tuple[bool, str]:
        """
        Cancel a solidarity event and publish cancellation to the network
        
        Args:
            event_id: ID of the event to cancel
            user_id: ID of the user canceling the event
            
        Returns:
            Tuple of (success, message)
        """
        try:
            logger.info(
                "Canceling solidarity event",
                event_id=event_id,
                user_id=user_id
            )
            
            # Validate event ID
            if not event_id:
                return False, "Event ID is required"
            
            # Publish event cancellation to Kafka
            success = self.producer.publish_event_cancellation(event_id)
            
            if not success:
                return False, "Failed to publish event cancellation to network"
            
            logger.info(
                "Event cancellation published successfully",
                event_id=event_id,
                organization_id=self.organization_id
            )
            
            return True, f"Event {event_id} cancellation published successfully"
            
        except Exception as e:
            logger.error(
                "Error canceling solidarity event",
                error=str(e),
                event_id=event_id,
                user_id=user_id
            )
            return False, f"Internal error: {str(e)}"
    
    def process_event_cancellation(self, cancellation_data: Dict[str, Any]) -> bool:
        """
        Process an event cancellation received from Kafka
        
        Args:
            cancellation_data: Cancellation data from Kafka message
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            logger.info(
                "Processing event cancellation",
                event_id=cancellation_data.get('event_id'),
                organization=cancellation_data.get('organization_id')
            )
            
            # Skip our own cancellations
            if cancellation_data.get('organization_id') == self.organization_id:
                logger.info("Skipping own event cancellation", event_id=cancellation_data.get('event_id'))
                return True
            
            # Validate required fields
            required_fields = ['event_id', 'organization_id']
            for field in required_fields:
                if field not in cancellation_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Update event status in database
            result = self.network_repo.deactivate_external_event(
                cancellation_data['organization_id'],
                cancellation_data['event_id']
            )
            
            if result:
                logger.info(
                    "External event deactivated successfully",
                    event_id=cancellation_data['event_id'],
                    organization=cancellation_data['organization_id']
                )
                return True
            else:
                logger.warning(
                    "Event not found for cancellation",
                    event_id=cancellation_data['event_id'],
                    organization=cancellation_data['organization_id']
                )
                return True  # Not an error if event doesn't exist
                
        except Exception as e:
            logger.error(
                "Error processing event cancellation",
                event_id=cancellation_data.get('event_id'),
                error=str(e)
            )
            return False