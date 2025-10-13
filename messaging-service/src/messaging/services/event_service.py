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
from .notification_service import NotificationService

logger = structlog.get_logger(__name__)


class EventService:
    """Service for managing solidarity events in the network"""
    
    def __init__(self):
        self.network_repo = NetworkRepository()
        self.producer = BaseProducer()
        self.notification_service = NotificationService()
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
        Also notifies all volunteers who had adhesions to the event
        
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
            
            # Get event information and affected volunteers before canceling
            try:
                # Get event details from local database first
                from messaging.database.connection import get_database_connection
                
                with get_database_connection() as conn:
                    cursor = conn.cursor(dictionary=True)
                    
                    # Get event information from network table (since local event may be deleted)
                    # Don't filter by organization since we need to handle cancellations from any org
                    event_query = """
                        SELECT nombre, descripcion, fecha_evento, organizacion_origen as organizacion
                        FROM eventos_red 
                        WHERE evento_id = %s
                    """
                    cursor.execute(event_query, (event_id,))
                    event_info = cursor.fetchone()
                    
                    if not event_info:
                        logger.warning(f"Event {event_id} not found in network database")
                        event_info = {
                            'nombre': f'Evento {event_id}',
                            'descripcion': '',
                            'organizacion': self.organization_id
                        }
                    
                    # Get all volunteers with adhesions to this event
                    adhesions_query = """
                        SELECT aee.voluntario_id, aee.datos_voluntario, u.nombre, u.apellido, u.email
                        FROM adhesiones_eventos_externos aee
                        JOIN usuarios u ON aee.voluntario_id = u.id
                        WHERE aee.evento_externo_id = %s 
                        AND aee.estado IN ('PENDIENTE', 'CONFIRMADA')
                    """
                    cursor.execute(adhesions_query, (event_id,))
                    affected_volunteers = cursor.fetchall()
                    
                    logger.info(f"Found {len(affected_volunteers)} affected volunteers for event {event_id}")
                    
                    # Cancel all adhesions
                    if affected_volunteers:
                        cancel_adhesions_query = """
                            UPDATE adhesiones_eventos_externos 
                            SET estado = 'CANCELADA'
                            WHERE evento_externo_id = %s 
                            AND estado IN ('PENDIENTE', 'CONFIRMADA')
                        """
                        cursor.execute(cancel_adhesions_query, (event_id,))
                        conn.commit()
                        
                        logger.info(f"Cancelled {len(affected_volunteers)} adhesions for event {event_id}")
                    
                    # Send notifications to affected volunteers
                    if affected_volunteers:
                        for volunteer in affected_volunteers:
                            try:
                                self.notification_service.create_notification(
                                    user_id=volunteer['voluntario_id'],
                                    notification_type='evento_cancelado',
                                    title='❌ Evento cancelado',
                                    message=f'Lamentamos informarte que el evento "{event_info["nombre"]}" de {event_info["organizacion"]} ha sido cancelado.\n\nTu adhesión ha sido automáticamente cancelada. Te notificaremos sobre futuros eventos similares.',
                                    additional_data={
                                        'evento_id': event_id,
                                        'evento_nombre': event_info['nombre'],
                                        'organizacion_origen': event_info['organizacion'],
                                        'fecha_cancelacion': datetime.now().isoformat()
                                    }
                                )
                                logger.info(f"Notification sent to volunteer {volunteer['voluntario_id']}")
                            except Exception as notif_error:
                                logger.error(f"Error sending notification to volunteer {volunteer['voluntario_id']}: {notif_error}")
                        
                        logger.info(f"Sent cancellation notifications to {len(affected_volunteers)} volunteers")
                
            except Exception as db_error:
                logger.error(f"Error handling local event cancellation: {db_error}")
                # Continue with Kafka publishing even if local handling fails
            
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
        Notifies local volunteers who had adhesions to the cancelled event
        
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
            
            event_id = cancellation_data['event_id']
            organization_id = cancellation_data['organization_id']
            
            # Get affected volunteers before deactivating the event
            try:
                from messaging.database.connection import get_database_connection
                
                with get_database_connection() as conn:
                    cursor = conn.cursor(dictionary=True)
                    
                    # Get event information and affected volunteers
                    event_volunteers_query = """
                        SELECT 
                            ee.nombre as event_name,
                            ee.descripcion as event_description,
                            aee.voluntario_id, 
                            aee.datos_voluntario, 
                            u.nombre, 
                            u.apellido, 
                            u.email
                        FROM eventos_externos ee
                        LEFT JOIN adhesiones_eventos_externos aee ON ee.id = aee.evento_externo_id
                        LEFT JOIN usuarios u ON aee.voluntario_id = u.id
                        WHERE ee.evento_id = %s 
                        AND ee.organizacion_id = %s
                        AND (aee.estado IN ('PENDIENTE', 'CONFIRMADA') OR aee.estado IS NULL)
                    """
                    cursor.execute(event_volunteers_query, (event_id, organization_id))
                    results = cursor.fetchall()
                    
                    event_name = None
                    affected_volunteers = []
                    
                    for row in results:
                        if event_name is None:
                            event_name = row['event_name'] or f'Evento {event_id}'
                        
                        if row['voluntario_id']:  # Only add if there's a volunteer
                            affected_volunteers.append(row)
                    
                    # Cancel all adhesions for this event
                    if affected_volunteers:
                        cancel_adhesions_query = """
                            UPDATE adhesiones_eventos_externos 
                            SET estado = 'CANCELADA'
                            WHERE evento_externo_id IN (
                                SELECT id FROM eventos_externos 
                                WHERE evento_id = %s AND organizacion_id = %s
                            )
                            AND estado IN ('PENDIENTE', 'CONFIRMADA')
                        """
                        cursor.execute(cancel_adhesions_query, (event_id, organization_id))
                        conn.commit()
                        
                        logger.info(f"Cancelled {len(affected_volunteers)} adhesions for external event {event_id}")
                    
                    # Send notifications to affected volunteers
                    if affected_volunteers:
                        for volunteer in affected_volunteers:
                            try:
                                self.notification_service.create_notification(
                                    user_id=volunteer['voluntario_id'],
                                    notification_type='evento_cancelado',
                                    title='❌ Evento externo cancelado',
                                    message=f'Lamentamos informarte que el evento "{event_name}" de {organization_id} ha sido cancelado.\n\nTu adhesión ha sido automáticamente cancelada. Te notificaremos sobre futuros eventos similares.',
                                    additional_data={
                                        'evento_id': event_id,
                                        'evento_nombre': event_name,
                                        'organizacion_origen': organization_id,
                                        'fecha_cancelacion': datetime.now().isoformat()
                                    }
                                )
                                logger.info(f"Cancellation notification sent to volunteer {volunteer['voluntario_id']}")
                            except Exception as notif_error:
                                logger.error(f"Error sending cancellation notification to volunteer {volunteer['voluntario_id']}: {notif_error}")
                        
                        logger.info(f"Sent external event cancellation notifications to {len(affected_volunteers)} volunteers")
                
            except Exception as db_error:
                logger.error(f"Error handling external event cancellation notifications: {db_error}")
                # Continue with deactivation even if notifications fail
            
            # Update event status in database
            result = self.network_repo.deactivate_external_event(
                organization_id,
                event_id
            )
            
            if result:
                logger.info(
                    "External event deactivated successfully",
                    event_id=event_id,
                    organization=organization_id
                )
                return True
            else:
                logger.warning(
                    "Event not found for cancellation",
                    event_id=event_id,
                    organization=organization_id
                )
                return True  # Not an error if event doesn't exist
                
        except Exception as e:
            logger.error(
                "Error processing event cancellation",
                event_id=cancellation_data.get('event_id'),
                error=str(e)
            )
            return False