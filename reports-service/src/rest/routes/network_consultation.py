"""
REST endpoints for network consultation via SOAP.
"""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from ...services.soap_service import get_soap_service, SOAPService
from ...soap.schemas import (
    NetworkConsultationRequest,
    NetworkConsultationResponse,
    SOAPErrorResponse
)
from ...utils.auth import get_current_user, require_president_role
from ...models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/network", tags=["Network Consultation"])


@router.post(
    "/consultation",
    response_model=NetworkConsultationResponse,
    summary="Consultar datos de la red de ONGs",
    description="Consulta información de presidentes y organizaciones de la red externa vía SOAP. Solo disponible para Presidentes."
)
async def network_consultation(
    request: NetworkConsultationRequest,
    current_user: User = Depends(get_current_user),
    soap_service: SOAPService = Depends(get_soap_service)
):
    """
    Consulta datos de presidentes y organizaciones de la red externa.
    
    - **organization_ids**: Lista de IDs de organizaciones a consultar
    
    Requiere rol de Presidente para acceder.
    """
    try:
        # Validate user permissions - only Presidents can access
        require_president_role(current_user)
        
        logger.info(f"Network consultation requested by user {current_user.id} for organizations: {request.organization_ids}")
        
        # Validate request
        if not request.organization_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Se debe proporcionar al menos un ID de organización"
            )
        
        if len(request.organization_ids) > 50:  # Reasonable limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pueden consultar más de 50 organizaciones a la vez"
            )
        
        # Validate organization IDs
        invalid_ids = [id for id in request.organization_ids if not isinstance(id, int) or id <= 0]
        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"IDs de organización inválidos: {invalid_ids}"
            )
        
        # Perform SOAP consultation
        result = await soap_service.get_network_consultation(request.organization_ids)
        
        # Check if there were errors
        if result.errors:
            logger.warning(f"SOAP consultation completed with errors: {result.errors}")
            # Return partial results with errors
            return result
        
        logger.info(f"Network consultation completed successfully. "
                   f"Found {result.total_presidents} presidents and {result.total_organizations} organizations")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in network consultation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor durante la consulta de red"
        )


@router.get(
    "/presidents/{organization_id}",
    summary="Consultar datos de presidente por organización",
    description="Consulta información del presidente de una organización específica. Solo disponible para Presidentes."
)
async def get_president_by_organization(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    soap_service: SOAPService = Depends(get_soap_service)
):
    """
    Consulta datos del presidente de una organización específica.
    
    - **organization_id**: ID de la organización
    
    Requiere rol de Presidente para acceder.
    """
    try:
        # Validate user permissions - only Presidents can access
        require_president_role(current_user)
        
        logger.info(f"President data requested by user {current_user.id} for organization: {organization_id}")
        
        # Validate organization ID
        if organization_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de organización inválido"
            )
        
        # Query president data
        presidents = await soap_service.get_president_data_only([organization_id])
        
        if not presidents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró información del presidente para la organización {organization_id}"
            )
        
        return presidents[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying president data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al consultar datos del presidente"
        )


@router.get(
    "/organizations/{organization_id}",
    summary="Consultar datos de organización",
    description="Consulta información de una organización específica. Solo disponible para Presidentes."
)
async def get_organization_by_id(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    soap_service: SOAPService = Depends(get_soap_service)
):
    """
    Consulta datos de una organización específica.
    
    - **organization_id**: ID de la organización
    
    Requiere rol de Presidente para acceder.
    """
    try:
        # Validate user permissions - only Presidents can access
        require_president_role(current_user)
        
        logger.info(f"Organization data requested by user {current_user.id} for organization: {organization_id}")
        
        # Validate organization ID
        if organization_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de organización inválido"
            )
        
        # Query organization data
        organizations = await soap_service.get_organization_data_only([organization_id])
        
        if not organizations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró información para la organización {organization_id}"
            )
        
        return organizations[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying organization data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al consultar datos de la organización"
        )


@router.get(
    "/test-connection",
    summary="Probar conexión SOAP",
    description="Prueba la conexión con el servicio SOAP de la red. Solo disponible para Presidentes."
)
async def test_soap_connection(
    current_user: User = Depends(get_current_user),
    soap_service: SOAPService = Depends(get_soap_service)
):
    """
    Prueba la conexión con el servicio SOAP de la red.
    
    Requiere rol de Presidente para acceder.
    """
    try:
        # Validate user permissions - only Presidents can access
        require_president_role(current_user)
        
        logger.info(f"SOAP connection test requested by user {current_user.id}")
        
        # Test connection
        result = await soap_service.test_soap_connection()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing SOAP connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al probar la conexión SOAP"
        )