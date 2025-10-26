"""
SOAP client for querying external ONG network data.
"""
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import requests
from ..config import get_settings

logger = logging.getLogger(__name__)

class SOAPClient:
    """Client for interacting with the ONG network SOAP service."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://soap-app-latest.onrender.com/"
        self.auth_group = "GrupoA-TM"
        self.auth_key = "clave-tm-a"
    
    def _create_soap_envelope(self, action: str, org_ids: List[int]) -> str:
        """Create SOAP envelope for the request."""
        org_ids_xml = "\n        ".join([f"<tns:string>{org_id}</tns:string>" for org_id in org_ids])
        
        return f"""<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:auth="auth.headers" xmlns:tns="soap.backend">
  <soapenv:Header>
    <auth:Auth>
      <auth:Grupo>{self.auth_group}</auth:Grupo>
      <auth:Clave>{self.auth_key}</auth:Clave>
    </auth:Auth>
  </soapenv:Header>
  <soapenv:Body>
    <tns:{action}>
      <tns:org_ids>
        {org_ids_xml}
      </tns:org_ids>
    </tns:{action}>
  </soapenv:Body>
</soapenv:Envelope>"""
    
    def _make_soap_request(self, action: str, org_ids: List[int]) -> str:
        """Make SOAP request and return response."""
        try:
            soap_envelope = self._create_soap_envelope(action, org_ids)
            
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': action
            }
            
            response = requests.post(
                self.base_url,
                data=soap_envelope,
                headers=headers,
                timeout=30
            )
            
            # Handle different HTTP status codes
            if response.status_code == 500:
                # Check if it's a SOAP fault or server error
                try:
                    # Try to parse as XML to see if it's a SOAP fault
                    root = ET.fromstring(response.text)
                    
                    # Look for SOAP fault
                    fault_elements = root.findall('.//{http://schemas.xmlsoap.org/soap/envelope/}Fault')
                    if fault_elements:
                        fault_string = fault_elements[0].find('.//{http://schemas.xmlsoap.org/soap/envelope/}faultstring')
                        fault_message = fault_string.text if fault_string is not None else "Unknown SOAP fault"
                        logger.warning(f"SOAP fault received: {fault_message}")
                        
                        # If it's about non-existent IDs, return empty response instead of error
                        if any(keyword in fault_message.lower() for keyword in ['not found', 'no data', 'empty', 'invalid id']):
                            logger.info(f"No data found for organization IDs: {org_ids}")
                            return self._create_empty_soap_response(action)
                        
                        raise SOAPServiceError(f"SOAP fault: {fault_message}")
                    else:
                        # Not a SOAP fault, might be server error
                        logger.warning(f"Server returned 500 but no SOAP fault found. Response: {response.text[:200]}")
                        # Try to return empty response for graceful degradation
                        return self._create_empty_soap_response(action)
                        
                except ET.ParseError:
                    # Not valid XML, treat as server error
                    logger.error(f"Server error (500) with non-XML response: {response.text[:200]}")
                    raise SOAPServiceError(f"Server error: HTTP 500 - {response.text[:100]}")
            
            elif response.status_code != 200:
                logger.error(f"HTTP error {response.status_code}: {response.text[:200]}")
                response.raise_for_status()
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"SOAP request failed: {e}")
            raise SOAPServiceError(f"SOAP request failed: {e}")
        except ET.ParseError as e:
            logger.error(f"Failed to parse SOAP response: {e}")
            raise SOAPServiceError(f"Invalid SOAP response: {e}")
    
    def _create_empty_soap_response(self, action: str) -> str:
        """Create an empty SOAP response for graceful error handling."""
        if action == 'list_presidents':
            return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <tns:list_presidentsResponse xmlns:tns="soap.backend">
      <tns:presidents></tns:presidents>
    </tns:list_presidentsResponse>
  </soap:Body>
</soap:Envelope>"""
        elif action == 'list_associations':
            return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <tns:list_associationsResponse xmlns:tns="soap.backend">
      <tns:associations></tns:associations>
    </tns:list_associationsResponse>
  </soap:Body>
</soap:Envelope>"""
        else:
            return """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <tns:emptyResponse xmlns:tns="soap.backend">
    </tns:emptyResponse>
  </soap:Body>
</soap:Envelope>"""
    
    def _parse_xml_response(self, xml_response: str, data_type: str) -> List[Dict[str, Any]]:
        """Parse XML response and extract data."""
        try:
            root = ET.fromstring(xml_response)
            
            # Define namespaces
            namespaces = {
                'soap11env': 'http://schemas.xmlsoap.org/soap/envelope/',
                'tns': 'soap.backend',
                's0': 'models'
            }
            
            results = []
            
            if data_type == 'organizations':
                # Find organization elements
                org_elements = root.findall('.//s0:OrganizationType', namespaces)
                for org in org_elements:
                    org_data = {
                        'id': self._get_element_text(org, 's0:id', namespaces),
                        'name': self._get_element_text(org, 's0:name', namespaces),
                        'address': self._get_element_text(org, 's0:address', namespaces),
                        'phone': self._get_element_text(org, 's0:phone', namespaces)
                    }
                    results.append(org_data)
            
            elif data_type == 'presidents':
                # Find president elements
                pres_elements = root.findall('.//s0:PresidentType', namespaces)
                for pres in pres_elements:
                    pres_data = {
                        'id': self._get_element_text(pres, 's0:id', namespaces),
                        'name': self._get_element_text(pres, 's0:name', namespaces),
                        'address': self._get_element_text(pres, 's0:address', namespaces),
                        'phone': self._get_element_text(pres, 's0:phone', namespaces),
                        'organization_id': self._get_element_text(pres, 's0:organization_id', namespaces)
                    }
                    results.append(pres_data)
            
            return results
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML response: {e}")
            raise SOAPServiceError(f"Failed to parse XML response: {e}")
    
    def _get_element_text(self, parent, tag, namespaces):
        """Get text content of an XML element."""
        element = parent.find(tag, namespaces)
        return element.text if element is not None else None
    
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
            
            # Make SOAP request for presidents
            xml_response = self._make_soap_request('list_presidents', organization_ids)
            
            # Parse response
            president_data = self._parse_xml_response(xml_response, 'presidents')
            
            # Convert to expected format
            formatted_data = []
            for pres in president_data:
                president_info = {
                    'organization_id': int(pres['organization_id']) if pres['organization_id'] else None,
                    'president_name': pres['name'],
                    'president_email': None,  # Not provided in current SOAP response
                    'president_phone': pres['phone'],
                    'president_id': int(pres['id']) if pres['id'] else None,
                    'president_address': pres['address'],
                    'start_date': None,  # Not provided in current SOAP response
                    'status': 'active'  # Default status
                }
                formatted_data.append(president_info)
            
            logger.info(f"Successfully retrieved {len(formatted_data)} president records")
            return formatted_data
            
        except SOAPServiceError:
            # Re-raise SOAP service errors as-is
            raise
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
            
            # Make SOAP request for organizations
            xml_response = self._make_soap_request('list_associations', organization_ids)
            
            # Parse response
            organization_data = self._parse_xml_response(xml_response, 'organizations')
            
            # Convert to expected format
            formatted_data = []
            for org in organization_data:
                org_info = {
                    'organization_id': int(org['id']) if org['id'] else None,
                    'organization_name': org['name'],
                    'organization_type': 'ONG',  # Default type
                    'address': org['address'],
                    'city': None,  # Not provided in current SOAP response
                    'country': None,  # Not provided in current SOAP response
                    'phone': org['phone'],
                    'email': None,  # Not provided in current SOAP response
                    'website': None,  # Not provided in current SOAP response
                    'registration_date': None,  # Not provided in current SOAP response
                    'status': 'active',  # Default status
                    'description': None  # Not provided in current SOAP response
                }
                formatted_data.append(org_info)
            
            logger.info(f"Successfully retrieved {len(formatted_data)} organization records")
            return formatted_data
            
        except SOAPServiceError:
            # Re-raise SOAP service errors as-is
            raise
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
        errors = []
        president_data = []
        organization_data = []
        
        try:
            logger.info(f"Querying combined data for organizations: {organization_ids}")
            
            # Query president data with error handling
            try:
                president_data = self.get_president_data(organization_ids)
            except SOAPServiceError as e:
                error_msg = f"Error querying president data: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
            
            # Query organization data with error handling
            try:
                organization_data = self.get_organization_data(organization_ids)
            except SOAPServiceError as e:
                error_msg = f"Error querying organization data: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
            
            # If both queries failed, raise an error
            if len(errors) == 2:
                raise SOAPServiceError(f"Both queries failed: {'; '.join(errors)}")
            
            return {
                'presidents': president_data,
                'organizations': organization_data,
                'query_ids': organization_ids,
                'total_presidents': len(president_data),
                'total_organizations': len(organization_data),
                'errors': errors
            }
            
        except SOAPServiceError:
            # Re-raise SOAP service errors as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error querying combined data: {e}")
            raise SOAPServiceError(f"Unexpected error: {e}")
    
    def test_connection(self) -> bool:
        """
        Test the SOAP service connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Test with a simple request
            test_response = self._make_soap_request('list_associations', [1])
            return True if test_response else False
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