"""
Donation-related models
"""
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


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
class DonationOffer:
    """Donation offer message model"""
    offer_id: str
    donor_organization: str
    donations: List['DonationOfferItem']
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