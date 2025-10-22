"""
GraphQL resolvers for filter management
"""
from typing import List, Optional
import json
from src.gql.types.filter import SavedFilterType, SavedFilterInput, saved_filter_to_graphql
from src.gql.context import Context
from src.utils.auth import AuthenticationError
from src.services.filter_service import FilterService
from src.models.filter import FilterType
import logging

logger = logging.getLogger(__name__)


class FilterResolver:
    """Filter GraphQL resolvers"""
    
    @staticmethod
    def get_saved_donation_filters(
        info  # Remove strawberry.Info type annotation to avoid import issues
    ) -> List[SavedFilterType]:
        """
        Get saved donation filters for current user
        
        Args:
            info: GraphQL info object
        
        Returns:
            List of SavedFilterType for donation filters
        """
        context = info.context
        
        try:
            # Require authentication
            user = context.auth_context.require_authentication()
            
            logger.info(f"User {user.id} ({user.rol.value}) requested saved donation filters")
            
            # Get filters from service
            filter_service = FilterService()
            saved_filters = filter_service.get_user_filters(
                usuario_id=user.id,
                tipo=FilterType.DONACIONES
            )
            
            # Convert to GraphQL types
            graphql_filters = [saved_filter_to_graphql(filter_obj) for filter_obj in saved_filters]
            
            logger.info(f"Returning {len(graphql_filters)} saved donation filters for user {user.id}")
            return graphql_filters
            
        except AuthenticationError as e:
            logger.warning(f"Authentication error getting saved filters: {e}")
            raise Exception(f"Authentication error: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting saved filters: {e}")
            raise Exception("Internal server error")
    
    @staticmethod
    def save_donation_filter(
        info,  # Remove strawberry.Info type annotation to avoid import issues
        nombre: str,
        filtros: str  # JSON string
    ) -> SavedFilterType:
        """
        Save a new donation filter
        
        Args:
            info: GraphQL info object
            nombre: Name for the filter
            filtros: Filter configuration as JSON string
        
        Returns:
            SavedFilterType for the created filter
        """
        context = info.context
        
        try:
            # Require authentication
            user = context.auth_context.require_authentication()
            
            logger.info(f"User {user.id} ({user.rol.value}) saving donation filter: {nombre}")
            
            # Validate and parse filter configuration
            if not nombre or not nombre.strip():
                raise ValueError("Filter name is required and cannot be empty")
            
            if not filtros:
                raise ValueError("Filter configuration is required")
            
            try:
                filter_config = json.loads(filtros)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in filter configuration: {str(e)}")
            
            # Create filter using service
            filter_service = FilterService()
            saved_filter = filter_service.create_filter(
                usuario_id=user.id,
                nombre=nombre.strip(),
                tipo=FilterType.DONACIONES,
                configuracion=filter_config
            )
            
            # Convert to GraphQL type
            graphql_filter = saved_filter_to_graphql(saved_filter)
            
            logger.info(f"Created donation filter '{nombre}' with ID {saved_filter.id} for user {user.id}")
            return graphql_filter
            
        except AuthenticationError as e:
            logger.warning(f"Authentication error saving filter: {e}")
            raise Exception(f"Authentication error: {str(e)}")
        except ValueError as e:
            logger.warning(f"Validation error saving filter: {e}")
            raise Exception(f"Validation error: {str(e)}")
        except Exception as e:
            logger.error(f"Error saving filter: {e}")
            raise Exception("Internal server error")
    
    @staticmethod
    def update_donation_filter(
        info,  # Remove strawberry.Info type annotation to avoid import issues
        id: int,
        nombre: Optional[str] = None,
        filtros: Optional[str] = None
    ) -> SavedFilterType:
        """
        Update an existing donation filter
        
        Args:
            info: GraphQL info object
            id: ID of the filter to update
            nombre: New name for the filter (optional)
            filtros: New filter configuration as JSON string (optional)
        
        Returns:
            SavedFilterType for the updated filter
        """
        context = info.context
        
        try:
            # Require authentication
            user = context.auth_context.require_authentication()
            
            logger.info(f"User {user.id} ({user.rol.value}) updating donation filter: {id}")
            
            # Validate parameters
            if not id or id <= 0:
                raise ValueError("Filter ID is required and must be positive")
            
            if nombre is not None and not nombre.strip():
                raise ValueError("Filter name cannot be empty")
            
            filter_config = None
            if filtros is not None:
                try:
                    filter_config = json.loads(filtros)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in filter configuration: {str(e)}")
            
            # Update filter using service
            filter_service = FilterService()
            updated_filter = filter_service.update_filter(
                filter_id=id,
                usuario_id=user.id,
                nombre=nombre.strip() if nombre else None,
                configuracion=filter_config
            )
            
            # Convert to GraphQL type
            graphql_filter = saved_filter_to_graphql(updated_filter)
            
            logger.info(f"Updated donation filter ID {id} for user {user.id}")
            return graphql_filter
            
        except AuthenticationError as e:
            logger.warning(f"Authentication error updating filter: {e}")
            raise Exception(f"Authentication error: {str(e)}")
        except ValueError as e:
            logger.warning(f"Validation error updating filter: {e}")
            raise Exception(f"Validation error: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating filter: {e}")
            raise Exception("Internal server error")
    
    @staticmethod
    def delete_donation_filter(
        info,  # Remove strawberry.Info type annotation to avoid import issues
        id: int
    ) -> bool:
        """
        Delete a donation filter
        
        Args:
            info: GraphQL info object
            id: ID of the filter to delete
        
        Returns:
            True if filter was deleted, False if not found
        """
        context = info.context
        
        try:
            # Require authentication
            user = context.auth_context.require_authentication()
            
            logger.info(f"User {user.id} ({user.rol.value}) deleting donation filter: {id}")
            
            # Validate parameters
            if not id or id <= 0:
                raise ValueError("Filter ID is required and must be positive")
            
            # Delete filter using service
            filter_service = FilterService()
            deleted = filter_service.delete_filter(
                filter_id=id,
                usuario_id=user.id
            )
            
            if deleted:
                logger.info(f"Deleted donation filter ID {id} for user {user.id}")
            else:
                logger.warning(f"Filter ID {id} not found for user {user.id}")
            
            return deleted
            
        except AuthenticationError as e:
            logger.warning(f"Authentication error deleting filter: {e}")
            raise Exception(f"Authentication error: {str(e)}")
        except ValueError as e:
            logger.warning(f"Validation error deleting filter: {e}")
            raise Exception(f"Validation error: {str(e)}")
        except Exception as e:
            logger.error(f"Error deleting filter: {e}")
            raise Exception("Internal server error")