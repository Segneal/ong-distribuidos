"""
GraphQL resolvers for donation reports
"""
from typing import List, Optional
from datetime import datetime
from src.gql.types.donation import DonationReportType, DonationType, DonationCategoryType, donation_to_graphql
from src.gql.context import Context
from src.utils.auth import AuthorizationError
from src.services.donation_service import DonationService
from src.models.donation import DonationCategory
import logging

logger = logging.getLogger(__name__)


class DonationResolver:
    """Donation GraphQL resolvers"""
    
    @staticmethod
    def get_donation_report(
        info,  # Remove strawberry.Info type annotation to avoid import issues
        categoria: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        eliminado: Optional[bool] = None
    ) -> List[DonationReportType]:
        """
        Get donation report with filtering and grouping
        
        Args:
            info: GraphQL info object
            categoria: Filter by donation category (ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES)
            fecha_desde: Filter donations from this date (ISO format string)
            fecha_hasta: Filter donations until this date (ISO format string)
            eliminado: Filter by eliminated status - True, False, or None for both
        
        Returns:
            List of DonationReportType grouped by category and eliminated status
        """
        context = info.context
        
        try:
            # Require donation access (Presidentes and Vocales only)
            user = context.auth_context.require_donation_access()
            
            logger.info(f"User {user.id} ({user.rol.value}) requested donation report")
            
            # Parse and validate parameters
            categoria_enum = None
            if categoria:
                try:
                    categoria_enum = DonationCategory(categoria)
                except ValueError:
                    raise ValueError(f"Invalid categoria: {categoria}. Must be one of: ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES")
            
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
            
            # Get donation report from service
            donation_service = DonationService()
            report_results = donation_service.get_donation_report(
                categoria=categoria_enum,
                fecha_desde=fecha_desde_dt,
                fecha_hasta=fecha_hasta_dt,
                eliminado=eliminado
            )
            
            # Convert to GraphQL types
            graphql_results = []
            for result in report_results:
                # Convert donations to GraphQL types
                donation_types = [donation_to_graphql(donation) for donation in result.registros]
                
                # Create report type
                report_type = DonationReportType(
                    categoria=DonationCategoryType(result.categoria.value),
                    eliminado=result.eliminado,
                    total_cantidad=result.total_cantidad,
                    registros=donation_types
                )
                graphql_results.append(report_type)
            
            logger.info(f"Returning {len(graphql_results)} donation report groups for user {user.id}")
            return graphql_results
            
        except AuthorizationError as e:
            logger.warning(f"Authorization error in donation report: {e}")
            # For GraphQL, we'll return an error in a different way since strawberry import is problematic
            raise Exception(f"Authorization error: {str(e)}")
        except ValueError as e:
            logger.warning(f"Validation error in donation report: {e}")
            raise Exception(f"Validation error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in donation report: {e}")
            raise Exception("Internal server error")