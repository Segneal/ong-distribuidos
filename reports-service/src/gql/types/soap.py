"""
SOAP-related GraphQL types for Strawberry
"""
import strawberry
from typing import List, Optional


@strawberry.type
class PresidentType:
    """GraphQL type for president data from SOAP service"""
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
    """GraphQL type for organization data from SOAP service"""
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
    """GraphQL type for network consultation response"""
    presidents: List[PresidentType]
    organizations: List[OrganizationType]
    query_ids: List[int]
    total_presidents: int
    total_organizations: int
    errors: List[str]


@strawberry.type
class SOAPConnectionTestType:
    """GraphQL type for SOAP connection test response"""
    connected: bool
    service_url: str
    message: str