"""
Adhesion Service for managing event adhesions in the ONG network
Handles volunteer adhesions to external events and processing incoming adhesions
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import structlog
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
from network_repository import NetworkRepository

# Add user service to path for volunteer validation
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'user-service', 'src'))

from ..producers.base_producer import BaseProducer
from ..config import settings

logger = structlog.get_logger(__name__)


class AdhesionService:
    """Service for managing event adhesions in the network"""
    
    def __init__(self):
        self.network_repo = NetworkRepository()
        self.producer = BaseProducer()
        self.organization_id = settings.organization_id
    
    def create_event_adhesion(self, event_id: str, volunteer_id: int, 
                            target_organization: str) -> Tuple[bool, str]:
        """
        Create an adhesion to an external event
        
        Args:
            event_id: ID of the external event
            volunteer_id: ID of the volunteer making the adhesion
            target_organization: Organization that owns the event
            
        Returns:
            Tuple of (success, message)
        """
        try:
            logger.info(
                "Creating event adhesion",
                event_id=event_id,
                volunteer_id=volunteer_id,
                target_organization=target_organization
            )
            
            # Validate required fields
            if not all([event_id, volunteer_id, target_organization]):
                return False, "Event ID, volunteer ID, and target organization are required"
            
            # Get volunteer data from user service
            volunteer_data = self._get_volunteer_data(volunteer_id)
            if not volunteer_data:
                return False, "Volunteer not found or invalid"
            
            # Validate that the event exists and is external
            external_event = self._get_external_event(event_id, target_organization)
            if not external_event:
                return False, "External event not found or not available"
            
            # Check if volunteer already has an adhesion to this event
            existing_adhesion = self._check_existing_adhesion(external_event['id'], volunteer_id)
            if existing_adhesion:
                return False, "Volunteer already has an adhesion to this event"
            
            # Create local adhesion record
            adhesion_record = self.network_repo.create_external_event_adhesion(
                external_event['id'],
                volunteer_id,
                volunteer_data
            )
            
            if not adhesion_record:
                return False, "Failed to create local adhesion record"
            
            # Publish adhesion to Kafka
            success = self.producer.publish_event_adhesion(
                target_organization,
                event_id,
                volunteer_data
            )
            
            if not success:
                # Rollback local record if Kafka publish fails
                logger.error("Failed to publish adhesion to Kafka, rolling back local record")
                return False, "Failed to publish adhesion to network"
            
            logger.info(
                "Event adhesion created successfully",
                event_id=event_id,
                volunteer_id=volunteer_id,
                target_organization=target_organization,
                adhesion_id=adhesion_record['id']
            )
            
            return True, f"Adhesion to event {event_id} created successfully"
            
        except Exception as e:
            logger.error(
                "Error creating event adhesion",
                error=str(e),
                event_id=event_id,
                volunteer_id=volunteer_id,
                target_organization=target_organization
            )
            return False, f"Internal error: {str(e)}"
    
    def process_incoming_adhesion(self, adhesion_data: Dict[str, Any]) -> bool:
        """
        Process an incoming adhesion from another organization
        
        Args:
            adhesion_data: Adhesion data from Kafka message
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            logger.info(
                "Processing incoming event adhesion",
                event_id=adhesion_data.get('event_id'),
                volunteer_org=adhesion_data.get('volunteer', {}).get('organization_id')
            )
            
            # Validate required fields
            required_fields = ['event_id', 'volunteer']
            for field in required_fields:
                if field not in adhesion_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            volunteer = adhesion_data['volunteer']
            required_volunteer_fields = ['organization_id', 'volunteer_id', 'name', 'surname', 'email']
            for field in required_volunteer_fields:
                if field not in volunteer:
                    logger.error(f"Missing required volunteer field: {field}")
                    return False
            
            # Skip our own adhesions (shouldn't happen but safety check)
            if volunteer.get('organization_id') == self.organization_id:
                logger.info("Skipping own adhesion", event_id=adhesion_data.get('event_id'))
                return True
            
            # Find the local event
            local_event = self._get_local_event(adhesion_data['event_id'])
            if not local_event:
                logger.warning(
                    "Received adhesion for unknown event",
                    event_id=adhesion_data['event_id']
                )
                return True  # Not an error, just ignore
            
            # Check if adhesion already exists
            existing_adhesion = self._check_incoming_adhesion_exists(
                local_event['id'],
                volunteer['organization_id'],
                volunteer['volunteer_id']
            )
            
            if existing_adhesion:
                logger.info(
                    "Adhesion already exists",
                    event_id=adhesion_data['event_id'],
                    volunteer_org=volunteer['organization_id'],
                    volunteer_id=volunteer['volunteer_id']
                )
                return True
            
            # Store the incoming adhesion
            result = self._store_incoming_adhesion(local_event['id'], volunteer)
            
            if result:
                logger.info(
                    "Incoming adhesion stored successfully",
                    event_id=adhesion_data['event_id'],
                    volunteer_org=volunteer['organization_id'],
                    volunteer_id=volunteer['volunteer_id'],
                    adhesion_id=result['id']
                )
                
                # TODO: Notify administrators about new adhesion
                # This could be implemented as an email notification or in-app notification
                
                return True
            else:
                logger.error(
                    "Failed to store incoming adhesion",
                    event_id=adhesion_data['event_id']
                )
                return False
                
        except Exception as e:
            logger.error(
                "Error processing incoming adhesion",
                event_id=adhesion_data.get('event_id'),
                error=str(e)
            )
            return False
    
    def get_volunteer_adhesions(self, volunteer_id: int) -> List[Dict[str, Any]]:
        """
        Get all adhesions for a specific volunteer
        
        Args:
            volunteer_id: ID of the volunteer
            
        Returns:
            List of adhesions
        """
        try:
            logger.info("Getting volunteer adhesions", volunteer_id=volunteer_id)
            
            adhesions = self.network_repo.get_volunteer_adhesions(volunteer_id)
            
            # Format response
            formatted_adhesions = []
            for adhesion in adhesions:
                try:
                    formatted_adhesions.append({
                        'id': adhesion['id'],
                        'event_id': adhesion['evento_externo_id'],
                        'event_name': adhesion['nombre'],
                        'event_description': adhesion['descripcion'],
                        'event_date': adhesion['fecha_evento'].isoformat() if adhesion['fecha_evento'] else None,
                        'organization_id': adhesion['organizacion_id'],
                        'adhesion_date': adhesion['fecha_adhesion'].isoformat() if adhesion['fecha_adhesion'] else None,
                        'status': adhesion['estado']
                    })
                except Exception as e:
                    logger.error(
                        "Error parsing adhesion data",
                        adhesion_id=adhesion.get('id'),
                        error=str(e)
                    )
                    continue
            
            logger.info(
                "Retrieved volunteer adhesions",
                volunteer_id=volunteer_id,
                count=len(formatted_adhesions)
            )
            
            return formatted_adhesions
            
        except Exception as e:
            logger.error("Error getting volunteer adhesions", volunteer_id=volunteer_id, error=str(e))
            return []
    
    def get_event_adhesions(self, event_id: str) -> List[Dict[str, Any]]:
        """
        Get all adhesions for a specific event (for administrators)
        
        Args:
            event_id: ID of the event
            
        Returns:
            List of adhesions to the event
        """
        try:
            logger.info("Getting event adhesions", event_id=event_id)
            
            # Find the local event
            local_event = self._get_local_event(event_id)
            if not local_event:
                logger.warning("Event not found", event_id=event_id)
                return []
            
            adhesions = self.network_repo.get_event_adhesions(local_event['id'])
            
            # Format response
            formatted_adhesions = []
            for adhesion in adhesions:
                try:
                    # Parse volunteer data if it exists
                    volunteer_data = adhesion.get('datos_voluntario', {})
                    if isinstance(volunteer_data, str):
                        import json
                        volunteer_data = json.loads(volunteer_data)
                    
                    formatted_adhesions.append({
                        'id': adhesion['id'],
                        'volunteer_id': adhesion['voluntario_id'],
                        'volunteer_name': adhesion.get('nombre', ''),
                        'volunteer_surname': adhesion.get('apellido', ''),
                        'volunteer_email': adhesion.get('email', ''),
                        'volunteer_phone': adhesion.get('telefono', ''),
                        'organization_id': volunteer_data.get('organization_id', ''),
                        'adhesion_date': adhesion['fecha_adhesion'].isoformat() if adhesion['fecha_adhesion'] else None,
                        'status': adhesion['estado'],
                        'external_volunteer': volunteer_data.get('organization_id') != self.organization_id
                    })
                except Exception as e:
                    logger.error(
                        "Error parsing adhesion data",
                        adhesion_id=adhesion.get('id'),
                        error=str(e)
                    )
                    continue
            
            logger.info(
                "Retrieved event adhesions",
                event_id=event_id,
                count=len(formatted_adhesions)
            )
            
            return formatted_adhesions
            
        except Exception as e:
            logger.error("Error getting event adhesions", event_id=event_id, error=str(e))
            return []
    
    def _get_volunteer_data(self, volunteer_id: int) -> Optional[Dict[str, Any]]:
        """Get volunteer data from user service"""
        try:
            # Import user repository
            from user_repository import UserRepository
            
            user_repo = UserRepository()
            volunteer = user_repo.get_user_by_id(volunteer_id)
            
            if not volunteer:
                return None
            
            return {
                'volunteer_id': volunteer_id,
                'name': volunteer.get('nombre', ''),
                'surname': volunteer.get('apellido', ''),
                'email': volunteer.get('email', ''),
                'phone': volunteer.get('telefono', '')
            }
            
        except Exception as e:
            logger.error("Error getting volunteer data", volunteer_id=volunteer_id, error=str(e))
            return None
    
    def _get_external_event(self, event_id: str, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get external event by ID and organization"""
        try:
            return self.network_repo.get_external_event_by_id(organization_id, event_id)
        except Exception as e:
            logger.error("Error getting external event", event_id=event_id, error=str(e))
            return None
    
    def _get_local_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get local event by ID"""
        try:
            # Import events repository
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'events-service', 'src'))
            from events_repository import EventsRepository
            
            events_repo = EventsRepository()
            return events_repo.get_event_by_id(event_id)
            
        except Exception as e:
            logger.error("Error getting local event", event_id=event_id, error=str(e))
            return None
    
    def _check_existing_adhesion(self, external_event_id: int, volunteer_id: int) -> bool:
        """Check if volunteer already has adhesion to external event"""
        try:
            adhesions = self.network_repo.get_volunteer_adhesions(volunteer_id)
            for adhesion in adhesions:
                if adhesion['evento_externo_id'] == external_event_id:
                    return True
            return False
        except Exception as e:
            logger.error("Error checking existing adhesion", error=str(e))
            return False
    
    def _check_incoming_adhesion_exists(self, local_event_id: int, volunteer_org: str, 
                                      volunteer_id: str) -> bool:
        """Check if incoming adhesion already exists"""
        try:
            adhesions = self.network_repo.get_event_adhesions(local_event_id)
            for adhesion in adhesions:
                volunteer_data = adhesion.get('datos_voluntario', {})
                if isinstance(volunteer_data, str):
                    import json
                    volunteer_data = json.loads(volunteer_data)
                
                if (volunteer_data.get('organization_id') == volunteer_org and 
                    str(volunteer_data.get('volunteer_id')) == str(volunteer_id)):
                    return True
            return False
        except Exception as e:
            logger.error("Error checking incoming adhesion", error=str(e))
            return False
    
    def _store_incoming_adhesion(self, local_event_id: int, volunteer_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Store incoming adhesion from external volunteer"""
        try:
            # Create a temporary volunteer record or use external volunteer ID
            # For now, we'll use a negative ID to indicate external volunteer
            external_volunteer_id = -(hash(f"{volunteer_data['organization_id']}-{volunteer_data['volunteer_id']}") % 1000000)
            
            return self.network_repo.create_external_event_adhesion(
                local_event_id,
                external_volunteer_id,
                volunteer_data
            )
            
        except Exception as e:
            logger.error("Error storing incoming adhesion", error=str(e))
            return None