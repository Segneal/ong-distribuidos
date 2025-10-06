"""
Fixed Donation model for inventory service with organization support
"""
from datetime import datetime
from typing import Optional
from enum import Enum

class DonationCategory(Enum):
    ROPA = "ROPA"
    ALIMENTOS = "ALIMENTOS"
    JUGUETES = "JUGUETES"
    UTILES_ESCOLARES = "UTILES_ESCOLARES"

class Donation:
    """Donation model class with organization support"""
    
    def __init__(self, id: Optional[int] = None, category: DonationCategory = DonationCategory.ALIMENTOS,
                 description: Optional[str] = None, quantity: int = 0, organization: str = 'empuje-comunitario',
                 deleted: bool = False, created_at: Optional[datetime] = None, created_by: Optional[int] = None,
                 updated_at: Optional[datetime] = None, updated_by: Optional[int] = None):
        self.id = id
        self.category = category if isinstance(category, DonationCategory) else DonationCategory(category)
        self.description = description
        self.quantity = quantity
        self.organization = organization
        self.deleted = deleted
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by
    
    def to_dict(self):
        """Convert to dictionary for gRPC response"""
        return {
            'id': self.id,
            'category': self.category.value if isinstance(self.category, DonationCategory) else self.category,
            'description': self.description,
            'quantity': self.quantity,
            'organization': self.organization,
            'deleted': self.deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }
    
    def __str__(self):
        return f"Donation(id={self.id}, category={self.category.value}, description={self.description}, quantity={self.quantity}, organization={self.organization})"
    
    def __repr__(self):
        return self.__str__()