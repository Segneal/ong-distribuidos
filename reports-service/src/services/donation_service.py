"""
Donation service for handling donation reports and filtering.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from src.models.donation import Donation, DonationCategory
from src.models.user import User
from src.utils.database_utils import get_db_session


class DonationReportResult:
    """Data class for donation report results"""
    def __init__(self, categoria: DonationCategory, eliminado: bool, total_cantidad: int, registros: List[Donation]):
        self.categoria = categoria
        self.eliminado = eliminado
        self.total_cantidad = total_cantidad
        self.registros = registros


class DonationService:
    """Service for handling donation reports and filtering"""
    
    def __init__(self):
        pass
    
    def _get_current_organization(self, session) -> str:
        """Get current organization from configuration"""
        try:
            from ..models.database import Base
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
    
    def get_donation_report(
        self,
        categoria: Optional[DonationCategory] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        eliminado: Optional[bool] = None,
        user_organization: Optional[str] = None
    ) -> List[DonationReportResult]:
        """
        Get donation report with filtering and grouping by category and eliminated status.
        
        Args:
            categoria: Filter by donation category (optional)
            fecha_desde: Filter donations from this date (optional)
            fecha_hasta: Filter donations until this date (optional)
            eliminado: Filter by eliminated status - True, False, or None for both (optional)
            user_organization: Filter by user's organization (optional)
        
        Returns:
            List of DonationReportResult grouped by category and eliminated status
        """
        with get_db_session() as session:
            # Get current organization from configuration
            current_org = self._get_current_organization(session)
            
            # Use user_organization if provided, otherwise use current_org
            filter_org = user_organization or current_org
            
            # IMPORTANT: Filter donations by organization
            # For now, we'll filter based on the organization in the user's JWT token
            # This assumes that donations belong to the organization of the user who created them
            
            # Build base query with eager loading of user relationships
            from sqlalchemy.orm import joinedload
            query = session.query(Donation).options(
                joinedload(Donation.usuario_creador),
                joinedload(Donation.usuario_modificador)
            )
            
            # Add organization filter
            # Since we don't have a direct organization field in donations,
            # we'll filter by checking if the user's organization matches the filter
            if filter_org != current_org:
                # If user is from a different organization, show no donations
                # This is a simple approach - in reality you'd implement proper ownership logic
                query = query.filter(Donation.id == -1)  # No donations match
            
            # Apply filters
            filters = []
            
            if categoria is not None:
                filters.append(Donation.categoria == categoria)
            
            if fecha_desde is not None:
                filters.append(Donation.fecha_alta >= fecha_desde)
            
            if fecha_hasta is not None:
                filters.append(Donation.fecha_alta <= fecha_hasta)
            
            if eliminado is not None:
                filters.append(Donation.eliminado == eliminado)
            
            # Apply all filters
            if filters:
                query = query.filter(and_(*filters))
            
            # Get all matching donations
            donations = query.all()
            
            # Group by category and eliminated status
            grouped_results = {}
            
            for donation in donations:
                key = (donation.categoria, donation.eliminado)
                if key not in grouped_results:
                    grouped_results[key] = {
                        'categoria': donation.categoria,
                        'eliminado': donation.eliminado,
                        'total_cantidad': 0,
                        'registros': []
                    }
                
                grouped_results[key]['total_cantidad'] += donation.cantidad
                grouped_results[key]['registros'].append(donation)
            
            # Convert to result objects
            results = []
            for group_data in grouped_results.values():
                result = DonationReportResult(
                    categoria=group_data['categoria'],
                    eliminado=group_data['eliminado'],
                    total_cantidad=group_data['total_cantidad'],
                    registros=group_data['registros']
                )
                results.append(result)
            
            # Sort results by category and eliminated status for consistent output
            results.sort(key=lambda x: (x.categoria.value, x.eliminado))
            
            return results
    
    def get_donations_by_filters(
        self,
        categoria: Optional[DonationCategory] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        eliminado: Optional[bool] = None,
        user_organization: Optional[str] = None
    ) -> List[Donation]:
        """
        Get filtered donations without grouping.
        
        Args:
            categoria: Filter by donation category (optional)
            fecha_desde: Filter donations from this date (optional)
            fecha_hasta: Filter donations until this date (optional)
            eliminado: Filter by eliminated status - True, False, or None for both (optional)
        
        Returns:
            List of filtered donations
        """
        with get_db_session() as session:
            # Get current organization from configuration
            current_org = self._get_current_organization(session)
            
            # Use user_organization if provided, otherwise use current_org
            filter_org = user_organization or current_org
            
            # Build base query without relationships to avoid session issues
            query = session.query(Donation)
            
            # Add organization filter
            if filter_org != current_org:
                # If user is from a different organization, show no donations
                query = query.filter(Donation.id == -1)  # No donations match
            
            # Apply filters
            filters = []
            
            if categoria is not None:
                filters.append(Donation.categoria == categoria)
            
            if fecha_desde is not None:
                filters.append(Donation.fecha_alta >= fecha_desde)
            
            if fecha_hasta is not None:
                filters.append(Donation.fecha_alta <= fecha_hasta)
            
            if eliminado is not None:
                filters.append(Donation.eliminado == eliminado)
            
            # Apply all filters
            if filters:
                query = query.filter(and_(*filters))
            
            # Order by fecha_alta descending for consistent results
            query = query.order_by(Donation.fecha_alta.desc())
            
            return query.all()
    
    def get_category_totals(
        self,
        categoria: Optional[DonationCategory] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        eliminado: Optional[bool] = None
    ) -> Dict[str, int]:
        """
        Get total quantities by category with filtering.
        
        Args:
            categoria: Filter by donation category (optional)
            fecha_desde: Filter donations from this date (optional)
            fecha_hasta: Filter donations until this date (optional)
            eliminado: Filter by eliminated status - True, False, or None for both (optional)
        
        Returns:
            Dictionary with category names as keys and total quantities as values
        """
        with get_db_session() as session:
            # Build base query
            query = session.query(
                Donation.categoria,
                func.sum(Donation.cantidad).label('total_cantidad')
            )
            
            # Apply filters
            filters = []
            
            if categoria is not None:
                filters.append(Donation.categoria == categoria)
            
            if fecha_desde is not None:
                filters.append(Donation.fecha_alta >= fecha_desde)
            
            if fecha_hasta is not None:
                filters.append(Donation.fecha_alta <= fecha_hasta)
            
            if eliminado is not None:
                filters.append(Donation.eliminado == eliminado)
            
            # Apply all filters
            if filters:
                query = query.filter(and_(*filters))
            
            # Group by category
            query = query.group_by(Donation.categoria)
            
            results = query.all()
            
            # Convert to dictionary
            totals = {}
            for categoria_enum, total in results:
                totals[categoria_enum.value] = total or 0
            
            return totals
    
    def validate_user_access(self, user: User) -> bool:
        """
        Validate if user has access to donation reports.
        
        Args:
            user: User object to validate
        
        Returns:
            True if user can access donation reports, False otherwise
        """
        return user.can_access_donation_reports()