"""
Event-related models
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class VolunteerInfo:
    """Volunteer information for event adhesions"""
    organization_id: str
    volunteer_id: int
    name: str
    last_name: str
    phone: Optional[str]
    email: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'organization_id': self.organization_id,
            'volunteer_id': self.volunteer_id,
            'name': self.name,
            'last_name': self.last_name,
            'phone': self.phone,
            'email': self.email
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VolunteerInfo':
        return cls(
            organization_id=data['organization_id'],
            volunteer_id=data['volunteer_id'],
            name=data['name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            email=data['email']
        )


@dataclass
class ExternalEvent:
    """External event message model"""
    organization_id: str
    event_id: str
    name: str
    description: str
    event_date: str
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'organization_id': self.organization_id,
            'event_id': self.event_id,
            'name': self.name,
            'description': self.description,
            'event_date': self.event_date,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExternalEvent':
        return cls(
            organization_id=data['organization_id'],
            event_id=data['event_id'],
            name=data['name'],
            description=data['description'],
            event_date=data['event_date'],
            timestamp=data['timestamp']
        )


@dataclass
class EventCancellation:
    """Event cancellation message model"""
    organization_id: str
    event_id: str
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'organization_id': self.organization_id,
            'event_id': self.event_id,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventCancellation':
        return cls(
            organization_id=data['organization_id'],
            event_id=data['event_id'],
            timestamp=data['timestamp']
        )


@dataclass
class EventAdhesion:
    """Event adhesion message model"""
    event_id: str
    volunteer: VolunteerInfo
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'volunteer': self.volunteer.to_dict(),
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventAdhesion':
        return cls(
            event_id=data['event_id'],
            volunteer=VolunteerInfo.from_dict(data['volunteer']),
            timestamp=data['timestamp']
        )