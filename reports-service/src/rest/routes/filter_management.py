"""
REST endpoints for filter management functionality.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ...models.filter import SavedFilter, FilterType
from ...models.user import User
from ...services.filter_service import FilterService
from ...utils.auth import get_current_user_from_token


router = APIRouter(prefix="/api/filters", tags=["Filter Management"])


class EventFilterInput(BaseModel):
    """Input model for event filtering configuration"""
    fecha_desde: Optional[datetime] = Field(None, description="Filter events from this date")
    fecha_hasta: Optional[datetime] = Field(None, description="Filter events until this date")
    usuario_id: Optional[int] = Field(None, description="Filter by user ID")
    reparto_donaciones: Optional[bool] = Field(None, description="Filter by donation distribution status")


class CreateEventFilterRequest(BaseModel):
    """Request model for creating event filters"""
    nombre: str = Field(..., min_length=1, max_length=255, description="Descriptive name for the filter")
    filtros: EventFilterInput = Field(..., description="Filter configuration")


class UpdateEventFilterRequest(BaseModel):
    """Request model for updating event filters"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated name for the filter")
    filtros: Optional[EventFilterInput] = Field(None, description="Updated filter configuration")


class SavedFilterResponse(BaseModel):
    """Response model for saved filters"""
    id: int = Field(..., description="Filter ID")
    nombre: str = Field(..., description="Filter name")
    tipo: FilterType = Field(..., description="Filter type")
    configuracion: dict = Field(..., description="Filter configuration")
    fecha_creacion: datetime = Field(..., description="Creation date")
    fecha_actualizacion: datetime = Field(..., description="Last update date")


@router.post("/events", response_model=SavedFilterResponse)
async def create_event_filter(
    request: CreateEventFilterRequest,
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Create a new saved filter for event reports.
    
    **Requirements:** User must be authenticated.
    """
    try:
        filter_service = FilterService()
        
        # Convert EventFilterInput to dict for storage
        filter_config = request.filtros.dict(exclude_none=True)
        
        saved_filter = filter_service.create_filter(
            user_id=current_user.id,
            nombre=request.nombre,
            tipo=FilterType.EVENTOS,
            configuracion=filter_config
        )
        
        return SavedFilterResponse(
            id=saved_filter.id,
            nombre=saved_filter.nombre,
            tipo=saved_filter.tipo,
            configuracion=saved_filter.configuracion,
            fecha_creacion=saved_filter.fecha_creacion,
            fecha_actualizacion=saved_filter.fecha_actualizacion
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating filter: {str(e)}"
        )


@router.get("/events", response_model=List[SavedFilterResponse])
async def get_event_filters(
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Get all saved event filters for the current user.
    
    **Requirements:** User must be authenticated.
    """
    try:
        filter_service = FilterService()
        
        filters = filter_service.get_user_filters(
            user_id=current_user.id,
            tipo=FilterType.EVENTOS
        )
        
        return [
            SavedFilterResponse(
                id=f.id,
                nombre=f.nombre,
                tipo=f.tipo,
                configuracion=f.configuracion,
                fecha_creacion=f.fecha_creacion,
                fecha_actualizacion=f.fecha_actualizacion
            )
            for f in filters
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving filters: {str(e)}"
        )


@router.get("/events/{filter_id}", response_model=SavedFilterResponse)
async def get_event_filter(
    filter_id: int,
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Get a specific event filter by ID.
    
    **Requirements:** 
    - User must be authenticated
    - User must own the filter
    """
    try:
        filter_service = FilterService()
        
        saved_filter = filter_service.get_filter_by_id(filter_id)
        
        if not saved_filter:
            raise HTTPException(status_code=404, detail="Filter not found")
        
        # Check ownership
        if saved_filter.usuario_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: You can only access your own filters"
            )
        
        # Check filter type
        if saved_filter.tipo != FilterType.EVENTOS:
            raise HTTPException(
                status_code=400,
                detail="Invalid filter type: Expected event filter"
            )
        
        return SavedFilterResponse(
            id=saved_filter.id,
            nombre=saved_filter.nombre,
            tipo=saved_filter.tipo,
            configuracion=saved_filter.configuracion,
            fecha_creacion=saved_filter.fecha_creacion,
            fecha_actualizacion=saved_filter.fecha_actualizacion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving filter: {str(e)}"
        )


@router.put("/events/{filter_id}", response_model=SavedFilterResponse)
async def update_event_filter(
    filter_id: int,
    request: UpdateEventFilterRequest,
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Update an existing event filter.
    
    **Requirements:** 
    - User must be authenticated
    - User must own the filter
    - At least one field must be provided for update
    """
    try:
        filter_service = FilterService()
        
        # Check if filter exists and user owns it
        existing_filter = filter_service.get_filter_by_id(filter_id)
        
        if not existing_filter:
            raise HTTPException(status_code=404, detail="Filter not found")
        
        if existing_filter.usuario_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: You can only update your own filters"
            )
        
        if existing_filter.tipo != FilterType.EVENTOS:
            raise HTTPException(
                status_code=400,
                detail="Invalid filter type: Expected event filter"
            )
        
        # Prepare update data
        update_data = {}
        
        if request.nombre is not None:
            update_data['nombre'] = request.nombre
        
        if request.filtros is not None:
            update_data['configuracion'] = request.filtros.dict(exclude_none=True)
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="At least one field must be provided for update"
            )
        
        # Update filter
        updated_filter = filter_service.update_filter(filter_id, **update_data)
        
        return SavedFilterResponse(
            id=updated_filter.id,
            nombre=updated_filter.nombre,
            tipo=updated_filter.tipo,
            configuracion=updated_filter.configuracion,
            fecha_creacion=updated_filter.fecha_creacion,
            fecha_actualizacion=updated_filter.fecha_actualizacion
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating filter: {str(e)}"
        )


@router.delete("/events/{filter_id}")
async def delete_event_filter(
    filter_id: int,
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Delete an event filter.
    
    **Requirements:** 
    - User must be authenticated
    - User must own the filter
    """
    try:
        filter_service = FilterService()
        
        # Check if filter exists and user owns it
        existing_filter = filter_service.get_filter_by_id(filter_id)
        
        if not existing_filter:
            raise HTTPException(status_code=404, detail="Filter not found")
        
        if existing_filter.usuario_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: You can only delete your own filters"
            )
        
        if existing_filter.tipo != FilterType.EVENTOS:
            raise HTTPException(
                status_code=400,
                detail="Invalid filter type: Expected event filter"
            )
        
        # Delete filter
        success = filter_service.delete_filter(filter_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete filter"
            )
        
        return {"success": True, "message": "Filter deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting filter: {str(e)}"
        )


# Additional endpoint for donation filters (for completeness)
@router.get("/donations", response_model=List[SavedFilterResponse])
async def get_donation_filters(
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Get all saved donation filters for the current user.
    
    **Requirements:** User must have access to donation reports.
    """
    from ...utils.auth import require_donation_report_access
    
    # Validate user access to donation reports
    require_donation_report_access(current_user)
    
    try:
        filter_service = FilterService()
        
        filters = filter_service.get_user_filters(
            user_id=current_user.id,
            tipo=FilterType.DONACIONES
        )
        
        return [
            SavedFilterResponse(
                id=f.id,
                nombre=f.nombre,
                tipo=f.tipo,
                configuracion=f.configuracion,
                fecha_creacion=f.fecha_creacion,
                fecha_actualizacion=f.fecha_actualizacion
            )
            for f in filters
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving donation filters: {str(e)}"
        )