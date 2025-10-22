"""
SOAP service for network consultation operations.
"""
import logging
from typing import List, Dict, Any
from ..soap.client import get_soap_client, SOAPServiceError
from ..soap.schemas import NetworkConsultationResponse, PresidentData, OrganizationData

logger = logging.getLogger(__name__)


class SOAPService:
    """Service class for SOAP network consultation operations."""
    
    def __init__(self):
        self.soap_client = get_soap_client()
    
    async def get_network_consultation(self, organization_ids: List[int]) -> NetworkConsultationResponse:
        """
        Get network consultation data for the given organization IDs.
        
        Args:
            organization_ids: List of organization IDs to query
            
        Returns:
            NetworkConsultationResponse with president and organization data
            
        Raises:
            SOAPServiceError: If the SOAP service call fails
        """
        try:
            logger.info(f"Processing network consultation for organizations: {organization_ids}")
            
            # Validate input
            if not organization_ids:
                return NetworkConsultationResponse(
                    errors=["No organization IDs provided"]
                )
            
            # Remove duplicates and invalid IDs
            valid_ids = list(set([id for id in organization_ids if isinstance(id, int) and id > 0]))
            
            if not valid_ids:
                return NetworkConsultationResponse(
                    errors=["No valid organization IDs provided"]
                )
            
            # Query combined data from SOAP service
            combined_data = self.soap_client.get_combined_data(valid_ids)
            
            # Convert to Pydantic models
            presidents = [
                PresidentData(**president_data) 
                for president_data in combined_data.get('presidents', [])
            ]
            
            organizations = [
                OrganizationData(**org_data) 
                for org_data in combined_data.get('organizations', [])
            ]
            
            response = NetworkConsultationResponse(
                presidents=presidents,
                organizations=organizations,
                query_ids=valid_ids,
                total_presidents=len(presidents),
                total_organizations=len(organizations)
            )
            
            logger.info(f"Network consultation completed successfully. "
                       f"Found {len(presidents)} presidents and {len(organizations)} organizations")
            
            return response
            
        except SOAPServiceError as e:
            logger.error(f"SOAP service error during network consultation: {e}")
            return NetworkConsultationResponse(
                query_ids=organization_ids,
                errors=[str(e)]
            )
        except Exception as e:
            logger.error(f"Unexpected error during network consultation: {e}")
            return NetworkConsultationResponse(
                query_ids=organization_ids,
                errors=[f"Internal server error: {str(e)}"]
            )
    
    async def get_president_data_only(self, organization_ids: List[int]) -> List[PresidentData]:
        """
        Get only president data for the given organization IDs.
        
        Args:
            organization_ids: List of organization IDs to query
            
        Returns:
            List of PresidentData objects
            
        Raises:
            SOAPServiceError: If the SOAP service call fails
        """
        try:
            logger.info(f"Querying president data for organizations: {organization_ids}")
            
            if not organization_ids:
                return []
            
            # Remove duplicates and invalid IDs
            valid_ids = list(set([id for id in organization_ids if isinstance(id, int) and id > 0]))
            
            if not valid_ids:
                return []
            
            president_data = self.soap_client.get_president_data(valid_ids)
            
            return [
                PresidentData(**data) 
                for data in president_data
            ]
            
        except Exception as e:
            logger.error(f"Error querying president data: {e}")
            raise
    
    async def get_organization_data_only(self, organization_ids: List[int]) -> List[OrganizationData]:
        """
        Get only organization data for the given organization IDs.
        
        Args:
            organization_ids: List of organization IDs to query
            
        Returns:
            List of OrganizationData objects
            
        Raises:
            SOAPServiceError: If the SOAP service call fails
        """
        try:
            logger.info(f"Querying organization data for organizations: {organization_ids}")
            
            if not organization_ids:
                return []
            
            # Remove duplicates and invalid IDs
            valid_ids = list(set([id for id in organization_ids if isinstance(id, int) and id > 0]))
            
            if not valid_ids:
                return []
            
            organization_data = self.soap_client.get_organization_data(valid_ids)
            
            return [
                OrganizationData(**data) 
                for data in organization_data
            ]
            
        except Exception as e:
            logger.error(f"Error querying organization data: {e}")
            raise
    
    async def test_soap_connection(self) -> Dict[str, Any]:
        """
        Test the SOAP service connection.
        
        Returns:
            Dictionary with connection test results
        """
        try:
            is_connected = self.soap_client.test_connection()
            
            return {
                'connected': is_connected,
                'service_url': self.soap_client.settings.SOAP_SERVICE_URL,
                'message': 'SOAP service is available' if is_connected else 'SOAP service is not available'
            }
            
        except Exception as e:
            logger.error(f"Error testing SOAP connection: {e}")
            return {
                'connected': False,
                'service_url': self.soap_client.settings.SOAP_SERVICE_URL,
                'message': f'Connection test failed: {str(e)}'
            }


# Global service instance
_soap_service = None

def get_soap_service() -> SOAPService:
    """Get the global SOAP service instance."""
    global _soap_service
    if _soap_service is None:
        _soap_service = SOAPService()
    return _soap_service