# SOAP client module
from .client import SOAPClient, get_soap_client, SOAPServiceError
from .schemas import (
    PresidentData,
    OrganizationData,
    NetworkConsultationRequest,
    NetworkConsultationResponse,
    SOAPErrorResponse
)

__all__ = [
    'SOAPClient',
    'get_soap_client',
    'SOAPServiceError',
    'PresidentData',
    'OrganizationData',
    'NetworkConsultationRequest',
    'NetworkConsultationResponse',
    'SOAPErrorResponse'
]