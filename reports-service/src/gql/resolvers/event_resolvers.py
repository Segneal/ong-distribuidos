"""
GraphQL resolvers for event reports
"""
from typing import List, Optional
from datetime import datetime
from src.gql.types.event import EventParticipationReportType, EventDetailType, SavedEventFilterType, EventFilterInput, EventFilterType
from src.gql.types.donation import DonationType, donation_to_graphql
from src.gql.types.user import UserType, UserRoleType, user_to_graphql
from src.gql.context import Context
from src.utils.auth import AuthorizationError
from src.services.event_service import EventService
from src.services.event_filter_service import EventFilterService
from src.utils.database_utils import get_db_session
from src.models.user import User
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
        
        # Get authenticated user - ALL users can access this endpoint
        user = context.auth_context.require_authentication()
        
        logger.info(f"User {user.id} ({user.rol.value}) requested event participation report for user {usuario_id}")
        
        # Validate that usuario_id is provided (required parameter)
        if not usuario_id:
            raise ValueError("usuario_id is required and cannot be empty")
        
        # Validate user access for the requested user_id
        # PRESIDENTE and COORDINADOR can see any user, others only themselves
        if not (user.can_access_all_event_reports() or user.id == usuario_id):
            raise AuthorizationError("You can only access your own event reports")
        
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
    
    @staticmethod
    def get_saved_event_filters(info) -> List[SavedEventFilterType]:
        """
        Get saved event filters for the current user
        
        Returns:
            List of SavedEventFilterType
        """
        context = info.context
        
        # Get authenticated user
        user = context.auth_context.require_authentication()
        
        logger.info(f"User {user.id} requested saved event filters")
        
        # Get saved filters from service
        filter_service = EventFilterService()
        saved_filters = filter_service.get_saved_filters(user.id)
        
        # Convert to GraphQL types
        graphql_results = []
        for filter_data in saved_filters:
            filter_type = SavedEventFilterType(
                id=filter_data['id'],
                nombre=filter_data['nombre'],
                filtros=EventFilterType(
                    usuarioId=filter_data['filtros']['usuarioId'],
                    fechaDesde=filter_data['filtros']['fechaDesde'],
                    fechaHasta=filter_data['filtros']['fechaHasta'],
                    repartodonaciones=filter_data['filtros']['repartodonaciones']
                ),
                fechaCreacion=filter_data['fechaCreacion']
            )
            graphql_results.append(filter_type)
        
        logger.info(f"Returning {len(graphql_results)} saved event filters for user {user.id}")
        return graphql_results
    
    @staticmethod
    def save_event_filter(info, nombre: str, filtros: EventFilterInput) -> SavedEventFilterType:
        """
        Save a new event filter
        
        Args:
            info: GraphQL info object
            nombre: Name of the filter
            filtros: Filter parameters
        
        Returns:
            SavedEventFilterType
        """
        context = info.context
        
        # Get authenticated user
        user = context.auth_context.require_authentication()
        
        logger.info(f"User {user.id} saving event filter: {nombre}")
        
        # Convert GraphQL input to dict
        filtros_dict = {
            'usuarioId': filtros.usuarioId,
            'fechaDesde': filtros.fechaDesde,
            'fechaHasta': filtros.fechaHasta,
            'repartodonaciones': filtros.repartodonaciones
        }
        
        # Save filter using service
        filter_service = EventFilterService()
        saved_filter = filter_service.save_filter(user.id, nombre, filtros_dict)
        
        # Convert to GraphQL type
        result = SavedEventFilterType(
            id=saved_filter['id'],
            nombre=saved_filter['nombre'],
            filtros=EventFilterType(
                usuarioId=saved_filter['filtros']['usuarioId'],
                fechaDesde=saved_filter['filtros']['fechaDesde'],
                fechaHasta=saved_filter['filtros']['fechaHasta'],
                repartodonaciones=saved_filter['filtros']['repartodonaciones']
            ),
            fechaCreacion=saved_filter['fechaCreacion']
        )
        
        logger.info(f"Event filter saved successfully with ID: {result.id}")
        return result
    
    @staticmethod
    def update_event_filter(
        info, 
        id: str, 
        nombre: Optional[str] = None, 
        filtros: Optional[EventFilterInput] = None
    ) -> SavedEventFilterType:
        """
        Update an existing event filter
        
        Args:
            info: GraphQL info object
            id: Filter ID
            nombre: New name (optional)
            filtros: New filter parameters (optional)
        
        Returns:
            SavedEventFilterType
        """
        context = info.context
        
        # Get authenticated user
        user = context.auth_context.require_authentication()
        
        logger.info(f"User {user.id} updating event filter: {id}")
        
        # Convert GraphQL input to dict if provided
        filtros_dict = None
        if filtros:
            filtros_dict = {
                'usuarioId': filtros.usuarioId,
                'fechaDesde': filtros.fechaDesde,
                'fechaHasta': filtros.fechaHasta,
                'repartodonaciones': filtros.repartodonaciones
            }
        
        # Update filter using service
        filter_service = EventFilterService()
        updated_filter = filter_service.update_filter(id, user.id, nombre, filtros_dict)
        
        # Convert to GraphQL type
        result = SavedEventFilterType(
            id=updated_filter['id'],
            nombre=updated_filter['nombre'],
            filtros=EventFilterType(
                usuarioId=updated_filter['filtros']['usuarioId'],
                fechaDesde=updated_filter['filtros']['fechaDesde'],
                fechaHasta=updated_filter['filtros']['fechaHasta'],
                repartodonaciones=updated_filter['filtros']['repartodonaciones']
            ),
            fechaCreacion=updated_filter['fechaCreacion']
        )
        
        logger.info(f"Event filter updated successfully: {id}")
        return result
    
    @staticmethod
    def delete_event_filter(info, id: str) -> bool:
        """
        Delete an event filter
        
        Args:
            info: GraphQL info object
            id: Filter ID
        
        Returns:
            True if deleted successfully
        """
        context = info.context
        
        # Get authenticated user
        user = context.auth_context.require_authentication()
        
        logger.info(f"User {user.id} deleting event filter: {id}")
        
        # Delete filter using service
        filter_service = EventFilterService()
        success = filter_service.delete_filter(id, user.id)
        
        logger.info(f"Event filter deleted successfully: {id}")
        return success
    
    @staticmethod
    def get_organization_users(info) -> List[UserType]:
        """
        Get all users from the current user's organization
        
        Returns:
            List of UserType
        """
        context = info.context
        
        # Get authenticated user
        user = context.auth_context.require_authentication()
        
        # Only PRESIDENTE and COORDINADOR can see all users
        if not user.can_access_all_event_reports():
            raise AuthorizationError("You don't have permission to view all users")
        
        logger.info(f"User {user.id} requested organization users")
        
        try:
            with get_db_session() as session:
                # Get all active users from the same organization
                users = session.query(User).filter(
                    User.organizacion == user.organizacion,
                    User.activo == True
                ).order_by(User.nombre, User.apellido).all()
                
                # Convert to GraphQL types manually to avoid import issues
                graphql_results = []
                for u in users:
                    user_type = UserType(
                        id=u.id,
                        nombre_usuario=u.nombre_usuario,
                        nombre=u.nombre,
                        apellido=u.apellido,
                        telefono=u.telefono,
                        email=u.email,
                        rol=UserRoleType(u.rol.value),
                        activo=u.activo,
                        fecha_creacion=u.fecha_creacion,
                        fecha_actualizacion=u.fecha_actualizacion
                    )
                    graphql_results.append(user_type)
                
                logger.info(f"Returning {len(graphql_results)} organization users")
                return graphql_results
        except Exception as e:
            logger.error(f"Error getting organization users: {e}")
            raise Exception("Error retrieving organization users")