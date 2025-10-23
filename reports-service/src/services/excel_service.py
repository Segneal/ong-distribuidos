"""
Excel export service for generating donation reports in Excel format.
"""
import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from sqlalchemy.orm import Session

from ..models.donation import Donation, DonationCategory
from ..models.filter import ExcelFile
from ..models.user import User
from ..services.donation_service import DonationService
from ..utils.database_utils import get_db_session
from ..config import settings


class ExcelExportService:
    """Service for generating Excel exports of donation reports"""
    
    def __init__(self):
        self.donation_service = DonationService()
        self.storage_path = settings.excel_storage_path
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
    
    def generate_donation_excel(
        self,
        user_id: int,
        categoria: Optional[DonationCategory] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        eliminado: Optional[bool] = None
    ) -> ExcelFile:
        """
        Generate Excel file with donation data filtered by the provided criteria.
        
        Args:
            user_id: ID of the user requesting the export
            categoria: Filter by donation category (optional)
            fecha_desde: Filter donations from this date (optional)
            fecha_hasta: Filter donations until this date (optional)
            eliminado: Filter by eliminated status (optional)
        
        Returns:
            ExcelFile object with file information
        """
        print("[EXCEL] Getting donations from service...")
        # Get filtered donations using the service
        donations = self.donation_service.get_donations_by_filters(
            categoria=categoria,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            eliminado=eliminado
        )
        
        print(f"[EXCEL] Got {len(donations)} donations")
        
        # Group donations by category
        print("[EXCEL] Grouping donations by category...")
        donations_by_category = self._group_donations_by_category(donations)
        print(f"[EXCEL] Grouped into {len(donations_by_category)} categories")
        
        # Generate Excel file
        file_id = str(uuid.uuid4())
        filename = self._generate_filename(categoria, fecha_desde, fecha_hasta)
        file_path = os.path.join(self.storage_path, f"{file_id}_{filename}")
        
        workbook = self._create_workbook(donations_by_category)
        workbook.save(file_path)
        
        # Save file record to database
        with get_db_session() as session:
            excel_file = ExcelFile.create_with_expiration(
                usuario_id=user_id,
                nombre_archivo=filename,
                ruta_archivo=file_path,
                hours_to_expire=24  # Files expire after 24 hours
            )
            session.add(excel_file)
            session.commit()
            session.refresh(excel_file)
            
            return excel_file
    
    def _group_donations_by_category(self, donations: List[Donation]) -> Dict[DonationCategory, List[Donation]]:
        """Group donations by category"""
        grouped = {}
        for i, donation in enumerate(donations):
            print(f"[EXCEL] Processing donation {i+1}: ID={donation.id}")
            try:
                categoria = donation.categoria
                print(f"[EXCEL] Donation {i+1} category: {categoria}")
                if categoria not in grouped:
                    grouped[categoria] = []
                grouped[categoria].append(donation)
            except Exception as e:
                print(f"[EXCEL] Error processing donation {i+1}: {e}")
                raise
        return grouped
    
    def _generate_filename(
        self,
        categoria: Optional[DonationCategory] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None
    ) -> str:
        """Generate descriptive filename for the Excel export"""
        parts = ["reporte_donaciones"]
        
        if categoria:
            parts.append(f"categoria_{categoria.value.lower()}")
        
        if fecha_desde:
            parts.append(f"desde_{fecha_desde.strftime('%Y%m%d')}")
        
        if fecha_hasta:
            parts.append(f"hasta_{fecha_hasta.strftime('%Y%m%d')}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        parts.append(timestamp)
        
        return f"{'_'.join(parts)}.xlsx"
    
    def _create_workbook(self, donations_by_category: Dict[DonationCategory, List[Donation]]) -> Workbook:
        """Create Excel workbook with separate sheets for each category"""
        workbook = Workbook()
        
        # Remove default sheet
        workbook.remove(workbook.active)
        
        # Create sheets for each category
        for category, donations in donations_by_category.items():
            sheet_name = self._get_sheet_name(category)
            worksheet = workbook.create_sheet(title=sheet_name)
            self._populate_worksheet(worksheet, donations, category)
        
        # If no donations, create an empty summary sheet
        if not donations_by_category:
            worksheet = workbook.create_sheet(title="Sin Datos")
            worksheet['A1'] = "No se encontraron donaciones con los filtros aplicados"
            worksheet['A1'].font = Font(bold=True)
        
        return workbook
    
    def _get_sheet_name(self, category: DonationCategory) -> str:
        """Get human-readable sheet name for category"""
        category_names = {
            DonationCategory.ROPA: "Ropa",
            DonationCategory.ALIMENTOS: "Alimentos",
            DonationCategory.JUGUETES: "Juguetes",
            DonationCategory.UTILES_ESCOLARES: "Útiles Escolares"
        }
        return category_names.get(category, category.value)
    
    def _populate_worksheet(self, worksheet, donations: List[Donation], category: DonationCategory):
        """Populate worksheet with donation data"""
        # Define headers
        headers = [
            "ID",
            "Fecha Alta",
            "Descripción",
            "Cantidad",
            "Eliminado",
            "Usuario Creación",
            "Usuario Modificación",
            "Fecha Modificación"
        ]
        
        # Style for headers
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        # Add headers
        for col, header in enumerate(headers, 1):
            cell = worksheet.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # Add data rows
        for row, donation in enumerate(donations, 2):
            worksheet.cell(row=row, column=1, value=donation.id)
            worksheet.cell(row=row, column=2, value=donation.fecha_alta.strftime("%Y-%m-%d %H:%M:%S") if donation.fecha_alta else "")
            worksheet.cell(row=row, column=3, value=donation.descripcion or "")
            worksheet.cell(row=row, column=4, value=donation.cantidad)
            worksheet.cell(row=row, column=5, value="Sí" if donation.eliminado else "No")
            
            # Usuario creación - usar ID por ahora
            usuario_creacion = f"Usuario ID: {donation.usuario_alta}" if donation.usuario_alta else "N/A"
            worksheet.cell(row=row, column=6, value=usuario_creacion)
            
            # Usuario modificación - usar ID por ahora
            usuario_modificacion = f"Usuario ID: {donation.usuario_modificacion}" if donation.usuario_modificacion else "N/A"
            worksheet.cell(row=row, column=7, value=usuario_modificacion)
            
            # Fecha modificación
            fecha_mod = ""
            if donation.fecha_modificacion:
                fecha_mod = donation.fecha_modificacion.strftime("%Y-%m-%d %H:%M:%S")
            worksheet.cell(row=row, column=8, value=fecha_mod)
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)  # Max width of 50
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Add summary row at the bottom
        if donations:
            summary_row = len(donations) + 3
            worksheet.cell(row=summary_row, column=3, value="TOTAL:")
            worksheet.cell(row=summary_row, column=3).font = Font(bold=True)
            
            total_cantidad = sum(d.cantidad for d in donations)
            worksheet.cell(row=summary_row, column=4, value=total_cantidad)
            worksheet.cell(row=summary_row, column=4).font = Font(bold=True)
    
    def get_file_by_id(self, file_id: str) -> Optional[ExcelFile]:
        """Get Excel file record by ID"""
        with get_db_session() as session:
            return session.query(ExcelFile).filter(ExcelFile.id == file_id).first()
    
    def cleanup_expired_files(self):
        """Remove expired Excel files from database and filesystem"""
        with get_db_session() as session:
            expired_files = session.query(ExcelFile).filter(
                ExcelFile.fecha_expiracion < datetime.utcnow()
            ).all()
            
            for excel_file in expired_files:
                # Remove file from filesystem
                try:
                    if os.path.exists(excel_file.ruta_archivo):
                        os.remove(excel_file.ruta_archivo)
                except Exception as e:
                    print(f"Error removing file {excel_file.ruta_archivo}: {e}")
                
                # Remove record from database
                session.delete(excel_file)
            
            session.commit()
            return len(expired_files)