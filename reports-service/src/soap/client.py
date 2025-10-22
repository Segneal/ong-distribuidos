"""
SOAP client for querying external ONG network data.
"""
import logging
from typing import List, Dict, Any, Optional
from zeep import Client, Settings
from zeep.exceptions import Fault, TransportError
from ..config import get_settings

logger = logging.getLogger(__name__)

class SOAPClient:
    """Client for interacting with the ONG network SOAP service."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the SOAP client with the WSDL URL."""
        try:
            # Configure zeep settings
            settings = Settings(
                strict=False,  # Allow non-strict mode for better compatibility
                xml_huge_tree=True,
                operation_timeout=self.settings.SOAP_TIMEOUT
            )
            
            # Create the SOAP client
            self.client = Client(
                wsdl=self.settings.SOAP_SERVICE_URL,
                settings=settings
            )
            
            logger.info(f"SOAP client initialized successfully with WSDL: {self.settings.SOAP_SERVICE_URL}")
            
        except Exception as e:
            logger.error(f"Failed to initialize SOAP client: {str(e)}")
            raise
    
    def get_president_data(self, organization_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Query president data for the given organization IDs.
        
        Args:
            organization_ids: List of organization IDs to query
            
        Returns:
            List of president data dictionaries
            
        Raises:
            SOAPServiceError: If the SOAP service call fails
        """
        if not organization_ids:
            return []
        
        try:
            logger.info(f"Querying president data for organizations: {organization_ids}")
            
            # Call the SOAP service method for president data
            # Note: The actual method name may need to be adjusted based on the WSDL
            response = self.client.service.getPresidentData(organizationIds=organization_ids)
            
            # Process the response
            president_data = []
            if response:
                # Handle different response formats
                if hasattr(response, 'presidents'):
                    presidents = response.presidents
                elif isinstance(response, list):
                    presidents = response
                else:
                    presidents = [response] if response else []
                
                for president in presidents:
                    president_info = {
                        'organization_id': getattr(president, 'organizationId', None),
                        'president_name': getattr(president, 'presidentName', None),
                        'president_email': getattr(president, 'presidentEmail', None),
                        'president_phone': getattr(president, 'presidentPhone', None),
                        'president_id': getattr(president, 'presidentId', None),
                        'start_date': getattr(president, 'startDate', None),
                        'status': getattr(president, 'status', None)
                    }
                    president_data.append(president_info)
            
            logger.info(f"Successfully retrieved {len(president_data)} president records")
            return president_data
            
        except Fault as e:
            logger.error(f"SOAP Fault when querying president data: {e}")
            raise SOAPServiceError(f"SOAP service error: {e}")
        except TransportError as e:
            logger.error(f"SOAP Transport error when querying president data: {e}")
            raise SOAPServiceError(f"SOAP transport error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error when querying president data: {e}")
            raise SOAPServiceError(f"Unexpected SOAP error: {e}")
    
    def get_organization_data(self, organization_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Query organization data for the given organization IDs.
        
        Args:
            organization_ids: List of organization IDs to query
            
        Returns:
            List of organization data dictionaries
            
        Raises:
            SOAPServiceError: If the SOAP service call fails
        """
        if not organization_ids:
            return []
        
        try:
            logger.info(f"Querying organization data for organizations: {organization_ids}")
            
            # Call the SOAP service method for organization data
            # Note: The actual method name may need to be adjusted based on the WSDL
            response = self.client.service.getOrganizationData(organizationIds=organization_ids)
            
            # Process the response
            organization_data = []
            if response:
                # Handle different response formats
                if hasattr(response, 'organizations'):
                    organizations = response.organizations
                elif isinstance(response, list):
                    organizations = response
                else:
                    organizations = [response] if response else []
                
                for org in organizations:
                    org_info = {
                        'organization_id': getattr(org, 'organizationId', None),
                        'organization_name': getattr(org, 'organizationName', None),
                        'organization_type': getattr(org, 'organizationType', None),
                        'address': getattr(org, 'address', None),
                        'city': getattr(org, 'city', None),
                        'country': getattr(org, 'country', None),
                        'phone': getattr(org, 'phone', None),
                        'email': getattr(org, 'email', None),
                        'website': getattr(org, 'website', None),
                        'registration_date': getattr(org, 'registrationDate', None),
                        'status': getattr(org, 'status', None),
                        'description': getattr(org, 'description', None)
                    }
                    organization_data.append(org_info)
            
            logger.info(f"Successfully retrieved {len(organization_data)} organization records")
            return organization_data
            
        except Fault as e:
            logger.error(f"SOAP Fault when querying organization data: {e}")
            raise SOAPServiceError(f"SOAP service error: {e}")
        except TransportError as e:
            logger.error(f"SOAP Transport error when querying organization data: {e}")
            raise SOAPServiceError(f"SOAP transport error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error when querying organization data: {e}")
            raise SOAPServiceError(f"Unexpected SOAP error: {e}")
    
    def get_combined_data(self, organization_ids: List[int]) -> Dict[str, Any]:
        """
        Query both president and organization data for the given organization IDs.
        
        Args:
            organization_ids: List of organization IDs to query
            
        Returns:
            Dictionary containing both president and organization data
            
        Raises:
            SOAPServiceError: If the SOAP service call fails
        """
        try:
            logger.info(f"Querying combined data for organizations: {organization_ids}")
            
            # Query both president and organization data
            president_data = self.get_president_data(organization_ids)
            organization_data = self.get_organization_data(organization_ids)
            
            return {
                'presidents': president_data,
                'organizations': organization_data,
                'query_ids': organization_ids,
                'total_presidents': len(president_data),
                'total_organizations': len(organization_data)
            }
            
        except Exception as e:
            logger.error(f"Error querying combined data: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test the SOAP service connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to get service info or make a simple call
            if self.client and hasattr(self.client, 'service'):
                logger.info("SOAP client connection test successful")
                return True
            return False
        except Exception as e:
            logger.error(f"SOAP connection test failed: {e}")
            return False


class SOAPServiceError(Exception):
    """Custom exception for SOAP service errors."""
    pass


# Global SOAP client instance
_soap_client: Optional[SOAPClient] = None

def get_soap_client() -> SOAPClient:
    """Get the global SOAP client instance."""
    global _soap_client
    if _soap_client is None:
        _soap_client = SOAPClient()
    return _soap_client