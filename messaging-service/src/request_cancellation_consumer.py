"""
Request Cancellation Consumer for ONG Network Messaging
Handles processing cancellation messages for donation requests
"""
import json
from typing import Dict, Any, Optional
import structlog

from .base_consumer import BaseConsumer
from .models import RequestCancellation
from .schemas import MessageValidator
from .config import Topics, settings

logger = structlog.get_logger(__name__)


class RequestCancellationConsumer(BaseConsumer):
    """Consumer for request cancellation messages"""
    
    def __init__(self):
        super().__init__(
            topics=[Topics.REQUEST_CANCELLATIONS]
        )
    
    def setup_handlers(self):
        """Setup message handlers - required by BaseConsumer"""
        # This consumer processes messages directly via process_message method
        pass
    
    def process_message(self, message: Dict[str, Any]) -> bool:
        """
        Process incoming request cancellation message
        
        Args:
            message: Kafka message containing request cancellation
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            logger.info(
                "Processing request cancellation message",
                message_id=message.get("message_id"),
                organization_id=message.get("organization_id")
            )
            
            # Extract message data
            message_data = message.get("data", {})
            
            # Skip our own messages
            if message_data.get("organization_id") == settings.organization_id:
                logger.info(
                    "Skipping own request cancellation message",
                    request_id=message_data.get("request_id")
                )
                return True
            
            # Validate message format
            if not self._validate_message_format(message_data):
                logger.error("Invalid request cancellation message format", message=message_data)
                return False
            
            # Validate against schema
            try:
                MessageValidator.validate_message("request_cancellation", message_data)
            except Exception as e:
                logger.error(
                    "Message schema validation failed",
                    error=str(e),
                    message=message_data
                )
                return False
            
            # Create request cancellation model
            cancellation = RequestCancellation.from_dict(message_data)
            
            # Process the cancellation
            success = self._process_request_cancellation(cancellation)
            
            if success:
                logger.info(
                    "Request cancellation processed successfully",
                    organization_id=cancellation.organization_id,
                    request_id=cancellation.request_id
                )
                
                # Log message processing for audit
                self._log_message_processing(message, "PROCESADO")
                
                return True
            else:
                logger.error(
                    "Failed to process request cancellation",
                    organization_id=cancellation.organization_id,
                    request_id=cancellation.request_id
                )
                
                # Log processing error
                self._log_message_processing(message, "ERROR", "Failed to update database")
                
                return False
                
        except Exception as e:
            logger.error(
                "Error processing request cancellation message",
                error=str(e),
                error_type=type(e).__name__,
                message=message
            )
            
            # Log processing error
            self._log_message_processing(message, "ERROR", str(e))
            
            return False
    
    def _validate_message_format(self, message_data: Dict[str, Any]) -> bool:
        """Validate basic message format"""
        required_fields = ["organization_id", "request_id", "timestamp"]
        
        for field in required_fields:
            if field not in message_data:
                logger.error("Missing required field", field=field)
                return False
        
        return True
    
    def _process_request_cancellation(self, cancellation: RequestCancellation) -> bool:
        """Process request cancellation by updating database"""
        try:
            from .database import get_database_connection
            
            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    # Update external request status to inactive
                    cursor.execute("""
                        UPDATE solicitudes_externas 
                        SET activa = false, fecha_creacion = CURRENT_TIMESTAMP
                        WHERE organizacion_solicitante = %s AND solicitud_id = %s
                    """, (cancellation.organization_id, cancellation.request_id))
                    
                    rows_affected = cursor.rowcount
                    conn.commit()
                    
                    if rows_affected > 0:
                        logger.info(
                            "External request marked as inactive",
                            organization_id=cancellation.organization_id,
                            request_id=cancellation.request_id,
                            rows_affected=rows_affected
                        )
                        return True
                    else:
                        logger.warning(
                            "No external request found to cancel",
                            organization_id=cancellation.organization_id,
                            request_id=cancellation.request_id
                        )
                        # Still return True as the cancellation was processed
                        return True
                    
        except Exception as e:
            logger.error(
                "Error processing request cancellation",
                error=str(e),
                organization_id=cancellation.organization_id,
                request_id=cancellation.request_id
            )
            return False
    
    def _log_message_processing(self, message: Dict[str, Any], status: str, error_detail: Optional[str] = None):
        """Log message processing for audit purposes"""
        try:
            from .database import get_database_connection
            
            message_data = message.get("data", {})
            
            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO historial_mensajes 
                        (topic, tipo_mensaje, mensaje_id, organizacion_origen, contenido, estado, error_detalle)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        Topics.REQUEST_CANCELLATIONS,
                        "request_cancellation",
                        message.get("message_id"),
                        message_data.get("organization_id"),
                        json.dumps(message),
                        status,
                        error_detail
                    ))
                    
                    conn.commit()
                    
        except Exception as e:
            logger.error("Error logging message processing", error=str(e))
            # Don't fail the main processing for logging errors