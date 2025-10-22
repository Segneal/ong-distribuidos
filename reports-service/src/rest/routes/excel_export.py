"""
REST endpoints for Excel export functionality.
"""
import os
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from ...models.donation import DonationCategory
from ...models.user import User
from ...services.excel_service import ExcelExportService
from ...utils.auth import get_current_user_from_token, require_donation_report_access


router = APIRouter(prefix="/api/reports", tags=["Excel Export"])


class DonationFilterInput(BaseModel):
    """Input model for donation filtering"""
    categoria: Optional[DonationCategory] = Field(None, description="Filter by donation category")
    fecha_desde: Optional[datetime] = Field(None, description="Filter donations from this date")
    fecha_hasta: Optional[datetime] = Field(None, description="Filter donations until this date")
    eliminado: Optional[bool] = Field(None, description="Filter by eliminated status - True, False, or None for both")


class ExcelExportResponse(BaseModel):
    """Response model for Excel export request"""
    file_id: str = Field(..., description="Unique identifier for the generated file")
    download_url: str = Field(..., description="URL to download the generated Excel file")
    filename: str = Field(..., description="Name of the generated file")
    expires_at: datetime = Field(..., description="When the file will expire")


@router.post("/donations/excel", response_model=ExcelExportResponse)
async def export_donations_to_excel(
    filters: DonationFilterInput,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Export donation data to Excel format with applied filters.
    
    Creates separate worksheets for each donation category containing detailed records.
    The generated file will be available for download for 24 hours.
    
    **Requirements:** User must be Presidente or Vocal to access donation reports.
    """
    # Validate user access
    require_donation_report_access(current_user)
    
    try:
        excel_service = ExcelExportService()
        
        # Generate Excel file
        excel_file = excel_service.generate_donation_excel(
            user_id=current_user.id,
            categoria=filters.categoria,
            fecha_desde=filters.fecha_desde,
            fecha_hasta=filters.fecha_hasta,
            eliminado=filters.eliminado
        )
        
        # Schedule cleanup of expired files in background
        background_tasks.add_task(excel_service.cleanup_expired_files)
        
        return ExcelExportResponse(
            file_id=excel_file.id,
            download_url=f"/api/reports/downloads/{excel_file.id}",
            filename=excel_file.nombre_archivo,
            expires_at=excel_file.fecha_expiracion
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating Excel file: {str(e)}"
        )


@router.get("/downloads/{file_id}")
async def download_excel_file(
    file_id: str,
    current_user: User = Depends(get_current_user_from_token)
):
    """
    Download a previously generated Excel file.
    
    **Requirements:** 
    - User must be authenticated
    - File must exist and not be expired
    - User must have access to donation reports
    """
    # Validate user access
    require_donation_report_access(current_user)
    
    try:
        excel_service = ExcelExportService()
        excel_file = excel_service.get_file_by_id(file_id)
        
        if not excel_file:
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Check if file has expired
        if excel_file.is_expired():
            raise HTTPException(
                status_code=410,
                detail="File has expired"
            )
        
        # Check if user owns the file (additional security)
        if excel_file.usuario_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: You can only download your own files"
            )
        
        # Check if file exists on filesystem
        if not os.path.exists(excel_file.ruta_archivo):
            raise HTTPException(
                status_code=404,
                detail="File not found on server"
            )
        
        return FileResponse(
            path=excel_file.ruta_archivo,
            filename=excel_file.nombre_archivo,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading file: {str(e)}"
        )


@router.get("/downloads")
async def list_user_files(
    current_user: User = Depends(get_current_user_from_token)
):
    """
    List all Excel files generated by the current user that haven't expired.
    
    **Requirements:** User must have access to donation reports.
    """
    # Validate user access
    require_donation_report_access(current_user)
    
    try:
        from ...utils.database_utils import get_db_session
        from ...models.filter import ExcelFile
        
        with get_db_session() as session:
            files = session.query(ExcelFile).filter(
                ExcelFile.usuario_id == current_user.id,
                ExcelFile.fecha_expiracion > datetime.utcnow()
            ).order_by(ExcelFile.fecha_creacion.desc()).all()
            
            return [
                {
                    "file_id": f.id,
                    "filename": f.nombre_archivo,
                    "created_at": f.fecha_creacion,
                    "expires_at": f.fecha_expiracion,
                    "download_url": f"/api/reports/downloads/{f.id}"
                }
                for f in files
            ]
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing files: {str(e)}"
        )