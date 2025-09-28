"""
Messaging models for ONG Network Messaging System
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import jsonschema
from jsonschema import validate, ValidationError

class DonationCategory(Enum):
    ROPA = "ROPA"
    ALIMENTOS = "ALIMENTOS"
    JUGUETES = "JUGUETES"
    UTILES_ESCOLARES = "UTILES_ESCOLARES"

@dataclass
class DonationItem:
    """Individual donation item for requests and offers"""
    category: str
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'category': self.category,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DonationItem':
        return cls(
            category=data['category'],
            description=data['description']
        )

@dataclass
class DonationTransferItem:
    """Individual donation item for transfers with quantity"""
    category: str
    description: str
    quantity: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'category': self.category,
            'description': self.description,
            'quantity': self.quantity
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DonationTransferItem':
        return cls(
            category=data['category'],
            description=data['description'],
            quantity=data['quantity']
        )

@dataclass
class DonationOfferItem:
    """Individual donation item for offers with quantity"""
    category: str
    description: str
    quantity: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'category': self.category,
            'description': self.description,
            'quantity': self.quantity
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DonationOfferItem':
        return cls(
            category=data['category'],
            description=data['description'],
            quantity=data['quantity']
        )

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
class DonationRequest:
    """Donation request message model"""
    organization_id: str
    request_id: str
    donations: List[DonationItem]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'organization_id': self.organization_id,
            'request_id': self.request_id,
            'donations': [donation.to_dict() for donation in self.donations],
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DonationRequest':
        return cls(
            organization_id=data['organization_id'],
            request_id=data['request_id'],
            donations=[DonationItem.from_dict(d) for d in data['donations']],
            timestamp=data['timestamp']
        )

@dataclass
class DonationTransfer:
    """Donation transfer message model"""
    request_id: str
    donor_organization: str
    donations: List[DonationTransferItem]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_id': self.request_id,
            'donor_organization': self.donor_organization,
            'donations': [donation.to_dict() for donation in self.donations],
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DonationTransfer':
        return cls(
            request_id=data['request_id'],
            donor_organization=data['donor_organization'],
            donations=[DonationTransferItem.from_dict(d) for d in data['donations']],
            timestamp=data['timestamp']
        )

@dataclass
class DonationOffer:
    """Donation offer message model"""
    offer_id: str
    donor_organization: str
    donations: List[DonationOfferItem]
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'offer_id': self.offer_id,
            'donor_organization': self.donor_organization,
            'donations': [donation.to_dict() for donation in self.donations],
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DonationOffer':
        return cls(
            offer_id=data['offer_id'],
            donor_organization=data['donor_organization'],
            donations=[DonationOfferItem.from_dict(d) for d in data['donations']],
            timestamp=data['timestamp']
        )

@dataclass
class RequestCancellation:
    """Request cancellation message model"""
    organization_id: str
    request_id: str
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'organization_id': self.organization_id,
            'request_id': self.request_id,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RequestCancellation':
        return cls(
            organization_id=data['organization_id'],
            request_id=data['request_id'],
            timestamp=data['timestamp']
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