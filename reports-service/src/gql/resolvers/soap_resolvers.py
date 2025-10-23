"""
GraphQL resolvers for SOAP network consultation operations.
"""
import logging
import strawberry
from typing import List
from ..types.soap import (
    NetworkConsultationType, 
    NetworkConsultationInput, 
    SOAPConnectionTest,
    PresidentType,
    OrganizationType
)
from ...services.soap_service import get_soap_service
from ...soap.schemas import PresidentData, OrganizationData

logger = logging.getLogger(__name__)


def convert_president_data(president_data: PresidentData) -> PresidentType:
    """Convert PresidentData to GraphQL PresidentType."""
    return PresidentType(
        organization_id=president_data.organization_id,
        president_name=president_data.president_name,
        president_email=president_data.president_email,
        president_phone=president_data.president_phone,
        president_id=president_data.president_id,
        president_address=getattr(president_data, 'president_address', None),
        start_date=president_data.start_date,
        status=president_data.status
    )


def convert_organization_data(org_data: OrganizationData) -> OrganizationType:
    """Convert OrganizationData to GraphQL OrganizationType."""
    return OrganizationType(
        organization_id=org_data.organization_id,
        organization_name=org_data.organization_name,
        organization_type=org_data.organization_type,
        address=org_data.address,
        city=org_data.city,
        country=org_data.country,
        phone=org_data.phone,
        email=org_data.email,
        website=org_data.website,
        registration_date=org_data.registration_date,
        status=org_data.status,
        description=org_data.description
    )


@strawberry.type
class SOAPQuery:
    """SOAP-related GraphQL queries."""
    
    @strawberry.field
    async def network_consultation(self, input: NetworkConsultationInput) -> NetworkConsultationType:
        """
        Get network consultation data for the given organization IDs.
        
        Args:
            input: NetworkConsultationInput with organization IDs
            
        Returns:
            NetworkConsultationType with president and organization data
        """
        try:
            logger.info(f"GraphQL network consultation request for organizations: {input.organization_ids}")
            
            soap_service = get_soap_service()
            response = await soap_service.get_network_consultation(input.organization_ids)
            
            # Convert to GraphQL types
            presidents = [convert_president_data(p) for p in response.presidents]
            organizations = [convert_organization_data(o) for o in response.organizations]
            
            return NetworkConsultationType(
                presidents=presidents,
                organizations=organizations,
                query_ids=response.query_ids,
                total_presidents=response.total_presidents,
                total_organizations=response.total_organizations,
                errors=response.errors
            )
            
        except Exception as e:
            logger.error(f"Error in network consultation GraphQL resolver: {e}")
            return NetworkConsultationType(
                presidents=[],
                organizations=[],
                query_ids=input.organization_ids,
                total_presidents=0,
                total_organizations=0,
                errors=[f"Internal server error: {str(e)}"]
            )
    
    @strawberry.field
    async def presidents_only(self, organization_ids: List[int]) -> List[PresidentType]:
        """
        Get only president data for the given organization IDs.
        
        Args:
            organization_ids: List of organization IDs
            
        Returns:
            List of PresidentType objects
        """
        try:
            logger.info(f"GraphQL presidents query for organizations: {organization_ids}")
            
            soap_service = get_soap_service()
            presidents_data = await soap_service.get_president_data_only(organization_ids)
            
            return [convert_president_data(p) for p in presidents_data]
            
        except Exception as e:
            logger.error(f"Error in presidents GraphQL resolver: {e}")
            return []
    
    @strawberry.field
    async def organizations_only(self, organization_ids: List[int]) -> List[OrganizationType]:
        """
        Get only organization data for the given organization IDs.
        
        Args:
            organization_ids: List of organization IDs
            
        Returns:
            List of OrganizationType objects
        """
        try:
            logger.info(f"GraphQL organizations query for organizations: {organization_ids}")
            
            soap_service = get_soap_service()
            organizations_data = await soap_service.get_organization_data_only(organization_ids)
            
            return [convert_organization_data(o) for o in organizations_data]
            
        except Exception as e:
            logger.error(f"Error in organizations GraphQL resolver: {e}")
            return []
    
    @strawberry.field
    async def soap_connection_test(self) -> SOAPConnectionTest:
        """
        Test the SOAP service connection.
        
        Returns:
            SOAPConnectionTest with connection status
        """
        try:
            logger.info("Testing SOAP connection via GraphQL")
            
            soap_service = get_soap_service()
            test_result = await soap_service.test_soap_connection()
            
            return SOAPConnectionTest(
                connected=test_result['connected'],
                service_url=test_result['service_url'],
                message=test_result['message']
            )
            
        except Exception as e:
            logger.error(f"Error in SOAP connection test GraphQL resolver: {e}")
            return SOAPConnectionTest(
                connected=False,
                service_url="Unknown",
                message=f"Connection test failed: {str(e)}"
            )