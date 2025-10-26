"""
SOAP-related GraphQL resolvers for Strawberry
"""
import strawberry
from typing import List
from ..types.soap import NetworkConsultationType, PresidentType, OrganizationType, SOAPConnectionTestType


class SOAPResolver:
    """Resolver class for SOAP-related GraphQL queries"""
    
    @staticmethod
    async def network_consultation(organization_ids: List[int]) -> NetworkConsultationType:
        """
        Resolve network consultation query.
        
        Args:
            organization_ids: List of organization IDs to query
            
        Returns:
            NetworkConsultationType with presidents and organizations data
        """
        try:
            from ...services.soap_service import get_soap_service
            
            soap_service = get_soap_service()
            response = await soap_service.get_network_consultation(organization_ids)
            
            # Convert response to GraphQL types
            presidents = [
                PresidentType(
                    organization_id=p.organization_id,
                    president_name=p.president_name,
                    president_email=p.president_email,
                    president_phone=p.president_phone,
                    president_id=p.president_id,
                    president_address=getattr(p, 'president_address', None),
                    start_date=p.start_date,
                    status=p.status
                ) for p in response.presidents
            ]
            
            organizations = [
                OrganizationType(
                    organization_id=o.organization_id,
                    organization_name=o.organization_name,
                    organization_type=o.organization_type,
                    address=o.address,
                    city=o.city,
                    country=o.country,
                    phone=o.phone,
                    email=o.email,
                    website=o.website,
                    registration_date=o.registration_date,
                    status=o.status,
                    description=o.description
                ) for o in response.organizations
            ]
            
            return NetworkConsultationType(
                presidents=presidents,
                organizations=organizations,
                query_ids=response.query_ids,
                total_presidents=response.total_presidents,
                total_organizations=response.total_organizations,
                errors=response.errors
            )
            
        except Exception as e:
            return NetworkConsultationType(
                presidents=[],
                organizations=[],
                query_ids=organization_ids,
                total_presidents=0,
                total_organizations=0,
                errors=[str(e)]
            )
    
    @staticmethod
    async def presidents_only(organization_ids: List[int]) -> List[PresidentType]:
        """
        Resolve presidents only query.
        
        Args:
            organization_ids: List of organization IDs to query
            
        Returns:
            List of PresidentType
        """
        try:
            from ...services.soap_service import get_soap_service
            
            soap_service = get_soap_service()
            presidents = await soap_service.get_president_data_only(organization_ids)
            
            return [
                PresidentType(
                    organization_id=p.organization_id,
                    president_name=p.president_name,
                    president_email=p.president_email,
                    president_phone=p.president_phone,
                    president_id=p.president_id,
                    president_address=getattr(p, 'president_address', None),
                    start_date=p.start_date,
                    status=p.status
                ) for p in presidents
            ]
            
        except Exception as e:
            return []
    
    @staticmethod
    async def organizations_only(organization_ids: List[int]) -> List[OrganizationType]:
        """
        Resolve organizations only query.
        
        Args:
            organization_ids: List of organization IDs to query
            
        Returns:
            List of OrganizationType
        """
        try:
            from ...services.soap_service import get_soap_service
            
            soap_service = get_soap_service()
            organizations = await soap_service.get_organization_data_only(organization_ids)
            
            return [
                OrganizationType(
                    organization_id=o.organization_id,
                    organization_name=o.organization_name,
                    organization_type=o.organization_type,
                    address=o.address,
                    city=o.city,
                    country=o.country,
                    phone=o.phone,
                    email=o.email,
                    website=o.website,
                    registration_date=o.registration_date,
                    status=o.status,
                    description=o.description
                ) for o in organizations
            ]
            
        except Exception as e:
            return []
    
    @staticmethod
    async def soap_connection_test() -> SOAPConnectionTestType:
        """
        Resolve SOAP connection test query.
        
        Returns:
            SOAPConnectionTestType with connection status
        """
        try:
            from ...services.soap_service import get_soap_service
            
            soap_service = get_soap_service()
            result = await soap_service.test_soap_connection()
            
            return SOAPConnectionTestType(
                connected=result['connected'],
                service_url=result['service_url'],
                message=result['message']
            )
            
        except Exception as e:
            return SOAPConnectionTestType(
                connected=False,
                service_url="Unknown",
                message=f"Connection test failed: {str(e)}"
            )