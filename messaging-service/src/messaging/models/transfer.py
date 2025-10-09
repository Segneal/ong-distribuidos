"""
Transfer-related models
"""
from typing import List, Dict, Any
from dataclasses import dataclass


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