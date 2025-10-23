"""
GraphQL types for SOAP network consultation operations.
"""
import strawberry
from typing import List, Optional


@strawberry.type
class PresidentType:
    """GraphQL type for president data."""
    organization_id: Optional[int] = None
    president_name: Optional[str] = None
    president_email: Optional[str] = None
    president_phone: Optional[str] = None
    president_id: Optional[int] = None
    president_address: Optional[str] = None
    start_date: Optional[str] = None
    status: Optional[str] = None


@strawberry.type
class OrganizationType:
    """GraphQL type for organization data."""
    organization_id: Optional[int] = None
    organization_name: Optional[str] = None
    organization_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    registration_date: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None


@strawberry.type
class NetworkConsultationType:
    """GraphQL type for network consultation response."""
    presidents: List[PresidentType]
    organizations: List[OrganizationType]
    query_ids: List[int]
    total_presidents: int
    total_organizations: int
    errors: List[str]


@strawberry.input
class NetworkConsultationInput:
    """GraphQL input type for network consultation request."""
    organization_ids: List[int]


@strawberry.type
class SOAPConnectionTest:
    """GraphQL type for SOAP connection test result."""
    connected: bool
    service_url: str
    message: str