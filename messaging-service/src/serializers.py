"""
Serialization and deserialization functions for Kafka messages
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, Union, Optional, Type, TypeVar
try:
    from .models import (
        DonationRequest, DonationTransfer, DonationOffer, RequestCancellation,
        ExternalEvent, EventCancellation, EventAdhesion
    )
    from .schemas import MessageValidator, ValidationError
except ImportError:
    from models import (
        DonationRequest, DonationTransfer, DonationOffer, RequestCancellation,
        ExternalEvent, EventCancellation, EventAdhesion
    )
    from schemas import MessageValidator, ValidationError

# Type variable for generic message types
T = TypeVar('T')

logger = logging.getLogger(__name__)

class SerializationError(Exception):
    """Custom exception for serialization errors"""
    pass

class DeserializationError(Exception):
    """Custom exception for deserialization errors"""
    pass

class MessageSerializer:
    """Message serializer for Kafka messages"""
    
    # Mapping of message types to their corresponding classes
    MESSAGE_CLASSES = {
        'donation_request': DonationRequest,
        'donation_transfer': DonationTransfer,
        'donation_offer': DonationOffer,
        'request_cancellation': RequestCancellation,
        'external_event': ExternalEvent,
        'event_cancellation': EventCancellation,
        'event_adhesion': EventAdhesion
    }
    
    @staticmethod
    def serialize_message(message_obj: Union[DonationRequest, DonationTransfer, DonationOffer, 
                                          RequestCancellation, ExternalEvent, EventCancellation, 
                                          EventAdhesion]) -> bytes:
        """
        Serialize a message object to JSON bytes for Kafka
        
        Args:
            message_obj: Message object to serialize
            
        Returns:
            JSON bytes representation of the message
            
        Raises:
            SerializationError: If serialization fails
        """
        try:
            # Convert message object to dictionary
            message_dict = message_obj.to_dict()
            
            # Determine message type for validation
            message_type = MessageSerializer._get_message_type(message_obj)
            
            # Validate message before serialization
            MessageValidator.validate_message(message_type, message_dict)
            
            # Serialize to JSON bytes
            json_str = json.dumps(message_dict, ensure_ascii=False, separators=(',', ':'))
            return json_str.encode('utf-8')
            
        except ValidationError as e:
            logger.error(f"Message validation failed during serialization: {e}")
            raise SerializationError(f"Message validation failed: {e}")
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            raise SerializationError(f"Failed to serialize message: {e}")
    
    @staticmethod
    def deserialize_message(message_bytes: bytes, message_type: str) -> Union[DonationRequest, DonationTransfer, 
                                                                           DonationOffer, RequestCancellation,
                                                                           ExternalEvent, EventCancellation, 
                                                                           EventAdhesion]:
        """
        Deserialize JSON bytes to a message object
        
        Args:
            message_bytes: JSON bytes from Kafka
            message_type: Type of message to deserialize to
            
        Returns:
            Deserialized message object
            
        Raises:
            DeserializationError: If deserialization fails
        """
        try:
            # Decode bytes to string and parse JSON
            json_str = message_bytes.decode('utf-8')
            message_dict = json.loads(json_str)
            
            # Validate message structure
            MessageValidator.validate_message(message_type, message_dict)
            
            # Get the appropriate message class
            if message_type not in MessageSerializer.MESSAGE_CLASSES:
                raise DeserializationError(f"Unknown message type: {message_type}")
            
            message_class = MessageSerializer.MESSAGE_CLASSES[message_type]
            
            # Create message object from dictionary
            return message_class.from_dict(message_dict)
            
        except ValidationError as e:
            logger.error(f"Message validation failed during deserialization: {e}")
            raise DeserializationError(f"Message validation failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise DeserializationError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            raise DeserializationError(f"Failed to deserialize message: {e}")
    
    @staticmethod
    def _get_message_type(message_obj: Any) -> str:
        """
        Determine message type from message object
        
        Args:
            message_obj: Message object
            
        Returns:
            Message type string
        """
        type_mapping = {
            DonationRequest: 'donation_request',
            DonationTransfer: 'donation_transfer',
            DonationOffer: 'donation_offer',
            RequestCancellation: 'request_cancellation',
            ExternalEvent: 'external_event',
            EventCancellation: 'event_cancellation',
            EventAdhesion: 'event_adhesion'
        }
        
        message_type = type_mapping.get(type(message_obj))
        if not message_type:
            raise SerializationError(f"Unknown message object type: {type(message_obj)}")
        
        return message_type
    
    @staticmethod
    def create_timestamp() -> str:
        """
        Create ISO format timestamp for messages
        
        Returns:
            ISO format timestamp string
        """
        return datetime.utcnow().isoformat() + 'Z'
    
    @staticmethod
    def validate_timestamp(timestamp: str) -> bool:
        """
        Validate timestamp format
        
        Args:
            timestamp: Timestamp string to validate
            
        Returns:
            True if valid timestamp format
        """
        try:
            # Try to parse the timestamp
            if timestamp.endswith('Z'):
                datetime.fromisoformat(timestamp[:-1])
            else:
                datetime.fromisoformat(timestamp)
            return True
        except ValueError:
            return False

class KafkaMessageHelper:
    """Helper class for Kafka message operations"""
    
    @staticmethod
    def create_donation_request(organization_id: str, request_id: str, 
                              donations: list) -> DonationRequest:
        """
        Create a donation request message
        
        Args:
            organization_id: ID of the requesting organization
            request_id: Unique request ID
            donations: List of donation items (dicts with category and description)
            
        Returns:
            DonationRequest object
        """
        try:
            from .models import DonationItem
        except ImportError:
            from models import DonationItem
        
        donation_items = [DonationItem.from_dict(d) for d in donations]
        
        return DonationRequest(
            organization_id=organization_id,
            request_id=request_id,
            donations=donation_items,
            timestamp=MessageSerializer.create_timestamp()
        )
    
    @staticmethod
    def create_donation_transfer(request_id: str, donor_organization: str, 
                               donations: list) -> DonationTransfer:
        """
        Create a donation transfer message
        
        Args:
            request_id: ID of the original request
            donor_organization: ID of the donating organization
            donations: List of donation items with quantities
            
        Returns:
            DonationTransfer object
        """
        try:
            from .models import DonationTransferItem
        except ImportError:
            from models import DonationTransferItem
        
        donation_items = [DonationTransferItem.from_dict(d) for d in donations]
        
        return DonationTransfer(
            request_id=request_id,
            donor_organization=donor_organization,
            donations=donation_items,
            timestamp=MessageSerializer.create_timestamp()
        )
    
    @staticmethod
    def create_donation_offer(offer_id: str, donor_organization: str, 
                            donations: list) -> DonationOffer:
        """
        Create a donation offer message
        
        Args:
            offer_id: Unique offer ID
            donor_organization: ID of the offering organization
            donations: List of donation items with quantities
            
        Returns:
            DonationOffer object
        """
        try:
            from .models import DonationOfferItem
        except ImportError:
            from models import DonationOfferItem
        
        donation_items = [DonationOfferItem.from_dict(d) for d in donations]
        
        return DonationOffer(
            offer_id=offer_id,
            donor_organization=donor_organization,
            donations=donation_items,
            timestamp=MessageSerializer.create_timestamp()
        )
    
    @staticmethod
    def create_request_cancellation(organization_id: str, request_id: str) -> RequestCancellation:
        """
        Create a request cancellation message
        
        Args:
            organization_id: ID of the organization cancelling the request
            request_id: ID of the request to cancel
            
        Returns:
            RequestCancellation object
        """
        return RequestCancellation(
            organization_id=organization_id,
            request_id=request_id,
            timestamp=MessageSerializer.create_timestamp()
        )
    
    @staticmethod
    def create_external_event(organization_id: str, event_id: str, name: str, 
                            description: str, event_date: str) -> ExternalEvent:
        """
        Create an external event message
        
        Args:
            organization_id: ID of the organizing organization
            event_id: Unique event ID
            name: Event name
            description: Event description
            event_date: Event date in ISO format
            
        Returns:
            ExternalEvent object
        """
        return ExternalEvent(
            organization_id=organization_id,
            event_id=event_id,
            name=name,
            description=description,
            event_date=event_date,
            timestamp=MessageSerializer.create_timestamp()
        )
    
    @staticmethod
    def create_event_cancellation(organization_id: str, event_id: str) -> EventCancellation:
        """
        Create an event cancellation message
        
        Args:
            organization_id: ID of the organization cancelling the event
            event_id: ID of the event to cancel
            
        Returns:
            EventCancellation object
        """
        return EventCancellation(
            organization_id=organization_id,
            event_id=event_id,
            timestamp=MessageSerializer.create_timestamp()
        )
    
    @staticmethod
    def create_event_adhesion(event_id: str, volunteer_data: dict) -> EventAdhesion:
        """
        Create an event adhesion message
        
        Args:
            event_id: ID of the event to join
            volunteer_data: Dictionary with volunteer information
            
        Returns:
            EventAdhesion object
        """
        try:
            from .models import VolunteerInfo
        except ImportError:
            from models import VolunteerInfo
        
        volunteer = VolunteerInfo.from_dict(volunteer_data)
        
        return EventAdhesion(
            event_id=event_id,
            volunteer=volunteer,
            timestamp=MessageSerializer.create_timestamp()
        )