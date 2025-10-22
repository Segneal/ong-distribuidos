"""
GraphQL resolvers for event reports
"""
from typing import List, Optional
from datetime import datetime
from src.gql.types.event import EventParticipationReportType, EventDetailType
from src.gql.types.donation import DonationType, donation_to_graphql
from src.gql.context import Context
from src.utils.auth import AuthorizationError
from src.services.event_service import EventService
import logging

logger = logging.getLogger(__name__)


class EventResolver:
    """Event GraphQL resolvers"""
    
    @staticmethod
    def get_event_participation_report(
        info,  # Remove strawberry.Info type annotation to avoid import issues
        usuario_id: int,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        repartodonaciones: Optional[bool] = None
    ) -> List[EventParticipationReportType]:
        """
        Get event participation report with filtering and monthly grouping
        
        Args:
            info: GraphQL info object
            usuario_id: ID of the user to get participation for (required)
            fecha_desde: Filter events from this date (ISO format string)
            fecha_hasta: Filter events until this date (ISO format string)
            repartodonaciones: Filter by donation distribution status - True, False, or None for both
        
        Returns:
            List of EventParticipationReportType grouped by month
        """
        context = info.context
        
        try:
            # Validate user access for the requested user_id
            user = context.auth_context.validate_event_user_access(usuario_id)
            
            logger.info(f"User {user.id} ({user.rol.value}) requested event participation report for user {usuario_id}")
            
            # Validate that usuario_id is provided (required parameter)
            if not usuario_id:
                raise ValueError("usuario_id is required and cannot be empty")
            
            # Parse and validate date parameters
            fecha_desde_dt = None
            if fecha_desde:
                try:
                    fecha_desde_dt = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
                except ValueError:
                    raise ValueError(f"Invalid fecha_desde format: {fecha_desde}. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
            
            fecha_hasta_dt = None
            if fecha_hasta:
                try:
                    fecha_hasta_dt = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
                except ValueError:
                    raise ValueError(f"Invalid fecha_hasta format: {fecha_hasta}. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
            
            # Validate date range
            if fecha_desde_dt and fecha_hasta_dt and fecha_desde_dt > fecha_hasta_dt:
                raise ValueError("fecha_desde cannot be later than fecha_hasta")
            
            # Get event participation report from service
            event_service = EventService()
            report_results = event_service.get_event_participation_report(
                usuario_id=usuario_id,
                fecha_desde=fecha_desde_dt,
                fecha_hasta=fecha_hasta_dt,
                repartodonaciones=repartodonaciones,
                requesting_user=user
            )
            
            # Convert to GraphQL types
            graphql_results = []
            for result in report_results:
                # Convert event details to GraphQL types
                event_details = []
                for event_detail in result.eventos:
                    # Convert donations to GraphQL types
                    donation_types = [donation_to_graphql(donation) for donation in event_detail.donaciones]
                    
                    # Create event detail type
                    detail_type = EventDetailType(
                        dia=event_detail.dia,
                        nombre=event_detail.nombre,
                        descripcion=event_detail.descripcion,
                        donaciones=donation_types
                    )
                    event_details.append(detail_type)
                
                # Create participation report type
                report_type = EventParticipationReportType(
                    mes=result.mes,
                    eventos=event_details
                )
                graphql_results.append(report_type)
            
            logger.info(f"Returning {len(graphql_results)} monthly event reports for user {usuario_id}")
            return graphql_results
            
        except AuthorizationError as e:
            logger.warning(f"Authorization error in event participation report: {e}")
            raise Exception(f"Authorization error: {str(e)}")
        except PermissionError as e:
            logger.warning(f"Permission error in event participation report: {e}")
            raise Exception(f"Permission error: {str(e)}")
        except ValueError as e:
            logger.warning(f"Validation error in event participation report: {e}")
            raise Exception(f"Validation error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in event participation report: {e}")
            raise Exception("Internal server error")