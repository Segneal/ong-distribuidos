"""
Event service for handling event participation reports and filtering.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from ..models.event import Event, DonacionRepartida
from ..models.user import User, UserRole
from ..models.donation import Donation
from ..utils.database_utils import get_db_session


class EventDetail:
    """Data class for event details in monthly reports"""
    def __init__(self, dia: int, nombre: str, descripcion: str, donaciones: List[Dict]):
        self.dia = dia
        self.nombre = nombre
        self.descripcion = descripcion
        self.donaciones = donaciones


class EventParticipationReport:
    """Data class for monthly event participation reports"""
    def __init__(self, mes: str, eventos: List[EventDetail]):
        self.mes = mes
        self.eventos = eventos


class EventService:
    """Service for handling event participation reports and filtering"""
    
    def __init__(self):
        pass
    
    def get_event_participation_report(
        self,
        usuario_id: int,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        repartodonaciones: Optional[bool] = None,
        requesting_user: User = None
    ) -> List[EventParticipationReport]:
        """
        Get event participation report grouped by month with event details.
        Only includes non-cancelled events.
        
        Args:
            usuario_id: ID of the user to get participation for (required)
            fecha_desde: Filter events from this date (optional)
            fecha_hasta: Filter events until this date (optional)
            repartodonaciones: Filter by donation distribution status (optional)
            requesting_user: User making the request for permission validation
        
        Returns:
            List of EventParticipationReport grouped by month
        """
        # Validate user access permissions
        if not self.validate_user_access(requesting_user, usuario_id):
            raise PermissionError("User does not have permission to access this user's event reports")
        
        with get_db_session() as session:
            # Get the target user
            target_user = session.query(User).filter(User.id == usuario_id).first()
            if not target_user:
                raise ValueError(f"User with ID {usuario_id} not found")
            
            # Build base query for events where user participated
            # Only include non-cancelled events (all events in DB are considered non-cancelled)
            query = session.query(Event).join(
                Event.participantes
            ).filter(
                User.id == usuario_id
            )
            
            # Apply date filters
            filters = []
            
            if fecha_desde is not None:
                filters.append(Event.fecha_evento >= fecha_desde)
            
            if fecha_hasta is not None:
                filters.append(Event.fecha_evento <= fecha_hasta)
            
            # Apply donation distribution filter
            if repartodonaciones is not None:
                if repartodonaciones:
                    # Events with donation distribution
                    filters.append(Event.donaciones_repartidas.any())
                else:
                    # Events without donation distribution
                    filters.append(~Event.donaciones_repartidas.any())
            
            # Apply all filters
            if filters:
                query = query.filter(and_(*filters))
            
            # Order by event date
            query = query.order_by(Event.fecha_evento.asc())
            
            events = query.all()
            
            # Group events by month
            monthly_events = {}
            
            for event in events:
                # Create month key (YYYY-MM format)
                month_key = event.fecha_evento.strftime("%Y-%m")
                month_display = event.fecha_evento.strftime("%B %Y")  # e.g., "January 2024"
                
                if month_key not in monthly_events:
                    monthly_events[month_key] = {
                        'mes': month_display,
                        'eventos': []
                    }
                
                # Get donations for this event
                donaciones = self._get_event_donations(session, event.id)
                
                event_detail = EventDetail(
                    dia=event.fecha_evento.day,
                    nombre=event.nombre,
                    descripcion=event.descripcion or "",
                    donaciones=donaciones
                )
                
                monthly_events[month_key]['eventos'].append(event_detail)
            
            # Convert to result objects
            results = []
            for month_key in sorted(monthly_events.keys()):
                month_data = monthly_events[month_key]
                result = EventParticipationReport(
                    mes=month_data['mes'],
                    eventos=month_data['eventos']
                )
                results.append(result)
            
            return results
    
    def _get_event_donations(self, session: Session, event_id: int) -> List[Dict]:
        """
        Get donations associated with an event through DonacionRepartida.
        Returns dictionary data to avoid SQLAlchemy session issues.
        
        Args:
            session: Database session
            event_id: ID of the event
        
        Returns:
            List of donation dictionaries
        """
        donations = session.query(Donation).join(
            DonacionRepartida, Donation.id == DonacionRepartida.donacion_id
        ).filter(
            DonacionRepartida.evento_id == event_id
        ).all()
        
        # Convert to dictionaries to avoid session issues
        donation_dicts = []
        for donation in donations:
            donation_dict = {
                'id': donation.id,
                'categoria': donation.categoria.value if donation.categoria else None,
                'descripcion': donation.descripcion,
                'cantidad': donation.cantidad,
                'eliminado': donation.eliminado,
                'fecha_alta': donation.fecha_alta,
                'fecha_modificacion': donation.fecha_modificacion
            }
            donation_dicts.append(donation_dict)
        
        return donation_dicts
    
    def get_user_events(
        self,
        usuario_id: int,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        repartodonaciones: Optional[bool] = None,
        requesting_user: User = None
    ) -> List[Event]:
        """
        Get events where a user participated with filtering.
        
        Args:
            usuario_id: ID of the user to get events for (required)
            fecha_desde: Filter events from this date (optional)
            fecha_hasta: Filter events until this date (optional)
            repartodonaciones: Filter by donation distribution status (optional)
            requesting_user: User making the request for permission validation
        
        Returns:
            List of filtered events
        """
        # Validate user access permissions
        if not self.validate_user_access(requesting_user, usuario_id):
            raise PermissionError("User does not have permission to access this user's events")
        
        with get_db_session() as session:
            # Build base query for events where user participated
            query = session.query(Event).join(
                Event.participantes
            ).filter(
                User.id == usuario_id
            )
            
            # Apply filters
            filters = []
            
            if fecha_desde is not None:
                filters.append(Event.fecha_evento >= fecha_desde)
            
            if fecha_hasta is not None:
                filters.append(Event.fecha_evento <= fecha_hasta)
            
            # Apply donation distribution filter
            if repartodonaciones is not None:
                if repartodonaciones:
                    # Events with donation distribution
                    filters.append(Event.donaciones_repartidas.any())
                else:
                    # Events without donation distribution
                    filters.append(~Event.donaciones_repartidas.any())
            
            # Apply all filters
            if filters:
                query = query.filter(and_(*filters))
            
            # Order by event date descending
            query = query.order_by(Event.fecha_evento.desc())
            
            return query.all()
    
    def validate_user_access(self, requesting_user: User, target_user_id: int) -> bool:
        """
        Validate if requesting user has access to target user's event reports.
        
        Args:
            requesting_user: User making the request
            target_user_id: ID of the user whose reports are being accessed
        
        Returns:
            True if access is allowed, False otherwise
        """
        if not requesting_user:
            return False
        
        # Presidentes and Coordinadores can access any user's reports
        if requesting_user.can_access_all_event_reports():
            return True
        
        # Other users can only access their own reports
        return requesting_user.id == target_user_id
    
    def get_monthly_event_summary(
        self,
        usuario_id: int,
        year: int,
        month: int,
        requesting_user: User = None
    ) -> Dict[str, Any]:
        """
        Get summary of events for a specific month.
        
        Args:
            usuario_id: ID of the user to get summary for
            year: Year to get summary for
            month: Month to get summary for (1-12)
            requesting_user: User making the request for permission validation
        
        Returns:
            Dictionary with event summary data
        """
        # Validate user access permissions
        if not self.validate_user_access(requesting_user, usuario_id):
            raise PermissionError("User does not have permission to access this user's event summary")
        
        with get_db_session() as session:
            # Build query for events in specific month
            query = session.query(Event).join(
                Event.participantes
            ).filter(
                User.id == usuario_id,
                extract('year', Event.fecha_evento) == year,
                extract('month', Event.fecha_evento) == month
            )
            
            events = query.all()
            
            # Calculate summary statistics
            total_events = len(events)
            events_with_donations = sum(1 for event in events if event.tiene_donaciones_repartidas)
            events_without_donations = total_events - events_with_donations
            
            return {
                'year': year,
                'month': month,
                'total_events': total_events,
                'events_with_donations': events_with_donations,
                'events_without_donations': events_without_donations,
                'events': events
            }