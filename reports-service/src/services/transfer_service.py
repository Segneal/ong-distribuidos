"""
Transfer service for handling donation transfer reports and filtering.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from src.models.transfer import DonationTransfer, TransferType, TransferStatus
from src.utils.database_utils import get_db_session


class TransferReportResult:
    """Data class for transfer report results"""
    def __init__(self, organizacion: str, tipo: TransferType, total_transferencias: int, total_items: int, transferencias: List[DonationTransfer]):
        self.organizacion = organizacion
        self.tipo = tipo
        self.total_transferencias = total_transferencias
        self.total_items = total_items
        self.transferencias = transferencias


class TransferService:
    """Service for handling transfer reports and filtering"""
    
    def __init__(self):
        pass
    
    def _get_current_organization(self, session) -> str:
        """Get current organization from configuration"""
        try:
            from sqlalchemy import text
            
            result = session.execute(
                text("SELECT valor FROM configuracion_organizacion WHERE clave = 'ORGANIZATION_ID'")
            ).fetchone()
            
            if result:
                return result[0]
            else:
                return 'empuje-comunitario'  # Default organization
        except Exception:
            return 'empuje-comunitario'  # Fallback to default
    
    def get_transfer_report(
        self,
        tipo: Optional[TransferType] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        estado: Optional[TransferStatus] = None,
        user_organization: Optional[str] = None
    ) -> List[TransferReportResult]:
        """
        Get transfer report with filtering and grouping by organization and type.
        
        Args:
            tipo: Filter by transfer type (ENVIADA, RECIBIDA) (optional)
            fecha_desde: Filter transfers from this date (optional)
            fecha_hasta: Filter transfers until this date (optional)
            estado: Filter by transfer status (optional)
            user_organization: Filter by user's organization (optional)
        
        Returns:
            List of TransferReportResult grouped by organization and type
        """
        with get_db_session() as session:
            # Get current organization from configuration
            current_org = self._get_current_organization(session)
            
            # Use user_organization if provided, otherwise use current_org
            filter_org = user_organization or current_org
            
            # Build base query
            from sqlalchemy.orm import joinedload
            query = session.query(DonationTransfer).options(
                joinedload(DonationTransfer.usuario)
            )
            
            # Filter by organization - show transfers where the user's organization is involved
            org_filters = []
            if filter_org:
                # Show transfers where user's org is either the owner or the counterpart
                org_filters.append(DonationTransfer.organizacion_propietaria == filter_org)
                org_filters.append(DonationTransfer.organizacion_contraparte == filter_org)
            
            if org_filters:
                query = query.filter(or_(*org_filters))
            
            # Apply other filters
            filters = []
            
            if tipo is not None:
                filters.append(DonationTransfer.tipo == tipo)
            
            if fecha_desde is not None:
                filters.append(DonationTransfer.fecha_transferencia >= fecha_desde)
            
            if fecha_hasta is not None:
                filters.append(DonationTransfer.fecha_transferencia <= fecha_hasta)
            
            if estado is not None:
                filters.append(DonationTransfer.estado == estado)
            
            # Apply all filters
            if filters:
                query = query.filter(and_(*filters))
            
            # Order by date descending
            query = query.order_by(DonationTransfer.fecha_transferencia.desc())
            
            # Get all matching transfers
            transfers = query.all()
            
            # Group by organization and type
            grouped_results = {}
            
            for transfer in transfers:
                # Determine the organization to group by
                # For sent transfers, group by counterpart organization
                # For received transfers, group by counterpart organization
                group_org = transfer.organizacion_contraparte
                
                key = (group_org, transfer.tipo)
                if key not in grouped_results:
                    grouped_results[key] = {
                        'organizacion': group_org,
                        'tipo': transfer.tipo,
                        'total_transferencias': 0,
                        'total_items': 0,
                        'transferencias': []
                    }
                
                grouped_results[key]['total_transferencias'] += 1
                grouped_results[key]['total_items'] += transfer.get_total_quantity()  # Use total quantity instead of item count
                grouped_results[key]['transferencias'].append(transfer)
            
            # Convert to result objects
            results = []
            for group_data in grouped_results.values():
                result = TransferReportResult(
                    organizacion=group_data['organizacion'],
                    tipo=group_data['tipo'],
                    total_transferencias=group_data['total_transferencias'],
                    total_items=group_data['total_items'],
                    transferencias=group_data['transferencias']
                )
                results.append(result)
            
            # Sort results by organization name and type
            results.sort(key=lambda x: (x.organizacion, x.tipo.value))
            
            return results
    
    def get_transfers_by_filters(
        self,
        tipo: Optional[TransferType] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        estado: Optional[TransferStatus] = None,
        user_organization: Optional[str] = None
    ) -> List[DonationTransfer]:
        """
        Get filtered transfers without grouping.
        
        Args:
            tipo: Filter by transfer type (optional)
            fecha_desde: Filter transfers from this date (optional)
            fecha_hasta: Filter transfers until this date (optional)
            estado: Filter by transfer status (optional)
            user_organization: Filter by user's organization (optional)
        
        Returns:
            List of filtered transfers
        """
        with get_db_session() as session:
            # Get current organization from configuration
            current_org = self._get_current_organization(session)
            
            # Use user_organization if provided, otherwise use current_org
            filter_org = user_organization or current_org
            
            # Build base query
            query = session.query(DonationTransfer)
            
            # Filter by organization
            org_filters = []
            if filter_org:
                org_filters.append(DonationTransfer.organizacion_propietaria == filter_org)
                org_filters.append(DonationTransfer.organizacion_contraparte == filter_org)
            
            if org_filters:
                query = query.filter(or_(*org_filters))
            
            # Apply other filters
            filters = []
            
            if tipo is not None:
                filters.append(DonationTransfer.tipo == tipo)
            
            if fecha_desde is not None:
                filters.append(DonationTransfer.fecha_transferencia >= fecha_desde)
            
            if fecha_hasta is not None:
                filters.append(DonationTransfer.fecha_transferencia <= fecha_hasta)
            
            if estado is not None:
                filters.append(DonationTransfer.estado == estado)
            
            # Apply all filters
            if filters:
                query = query.filter(and_(*filters))
            
            # Order by date descending
            query = query.order_by(DonationTransfer.fecha_transferencia.desc())
            
            return query.all()