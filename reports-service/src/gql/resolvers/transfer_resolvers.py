"""
GraphQL resolvers for transfer reports
"""
from typing import List, Optional
from datetime import datetime
from src.gql.types.transfer import TransferReportType, DonationTransferType, TransferTypeEnum, TransferStatusEnum, transfer_to_graphql
from src.gql.context import Context
from src.utils.auth import AuthorizationError
from src.services.transfer_service import TransferService
from src.models.transfer import TransferType as TransferTypeModel, TransferStatus as TransferStatusModel
import logging

logger = logging.getLogger(__name__)


class TransferResolver:
    """Transfer GraphQL resolvers"""
    
    @staticmethod
    def get_transfer_report(
        info,  # Remove strawberry.Info type annotation to avoid import issues
        tipo: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        estado: Optional[str] = None
    ) -> List[TransferReportType]:
        """
        Get transfer report with filtering and grouping
        
        Args:
            info: GraphQL info object
            tipo: Filter by transfer type (ENVIADA, RECIBIDA)
            fecha_desde: Filter transfers from this date (ISO format string)
            fecha_hasta: Filter transfers until this date (ISO format string)
            estado: Filter by transfer status (PENDIENTE, COMPLETADA, CANCELADA)
        
        Returns:
            List of TransferReportType grouped by organization and type
        """
        context = info.context
        
        try:
            # Require donation access (Presidentes and Vocales only)
            user = context.auth_context.require_donation_access()
            
            logger.info(f"User {user.id} ({user.rol.value}) requested transfer report")
            
            # Parse and validate parameters
            tipo_enum = None
            if tipo:
                try:
                    tipo_enum = TransferTypeModel(tipo)
                except ValueError:
                    raise ValueError(f"Invalid tipo: {tipo}. Must be one of: ENVIADA, RECIBIDA")
            
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
                    # If only date is provided (no time), set to end of day (23:59:59)
                    if fecha_hasta_dt.hour == 0 and fecha_hasta_dt.minute == 0 and fecha_hasta_dt.second == 0:
                        fecha_hasta_dt = fecha_hasta_dt.replace(hour=23, minute=59, second=59)
                except ValueError:
                    raise ValueError(f"Invalid fecha_hasta format: {fecha_hasta}. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
            
            estado_enum = None
            if estado:
                try:
                    estado_enum = TransferStatusModel(estado)
                except ValueError:
                    raise ValueError(f"Invalid estado: {estado}. Must be one of: PENDIENTE, COMPLETADA, CANCELADA")
            
            # Validate date range
            if fecha_desde_dt and fecha_hasta_dt and fecha_desde_dt > fecha_hasta_dt:
                raise ValueError("fecha_desde cannot be later than fecha_hasta")
            
            # Get transfer report from service
            try:
                transfer_service = TransferService()
                
                # Get user organization from JWT token
                user_organization = getattr(user, '_organization', 'empuje-comunitario')
                
                report_results = transfer_service.get_transfer_report(
                    tipo=tipo_enum,
                    fecha_desde=fecha_desde_dt,
                    fecha_hasta=fecha_hasta_dt,
                    estado=estado_enum,
                    user_organization=user_organization
                )
                logger.info(f"Got {len(report_results)} transfer report results from service")
            except Exception as service_error:
                logger.error(f"Error in transfer service: {service_error}")
                import traceback
                logger.error(f"Service traceback: {traceback.format_exc()}")
                raise service_error
            
            # Convert to GraphQL types
            graphql_results = []
            for result in report_results:
                try:
                    # Convert transfers to GraphQL types
                    transfer_types = []
                    for transfer in result.transferencias:
                        try:
                            transfer_type = transfer_to_graphql(transfer)
                            transfer_types.append(transfer_type)
                        except Exception as transfer_error:
                            logger.error(f"Error converting transfer {transfer.id}: {transfer_error}")
                            # Skip this transfer but continue with others
                            continue
                    
                    # Create report type
                    report_type = TransferReportType(
                        organizacion=result.organizacion,
                        tipo=TransferTypeEnum(result.tipo.value),
                        total_transferencias=result.total_transferencias,
                        total_items=result.total_items,
                        transferencias=transfer_types
                    )
                    graphql_results.append(report_type)
                    
                except Exception as group_error:
                    logger.error(f"Error processing group {result.organizacion}: {group_error}")
                    # Skip this group but continue with others
                    continue
            
            logger.info(f"Returning {len(graphql_results)} transfer report groups for user {user.id}")
            return graphql_results
            
        except AuthorizationError as e:
            logger.warning(f"Authorization error in transfer report: {e}")
            raise Exception(f"Authorization error: {str(e)}")
        except ValueError as e:
            logger.warning(f"Validation error in transfer report: {e}")
            raise Exception(f"Validation error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in transfer report: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception("Internal server error")