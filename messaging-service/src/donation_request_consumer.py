"""
Donation Request Consumer for ONG Network Messaging
Handles processing external donation requests from other organizations
"""
import json
from typing import Dict, Any, Optional
import structlog

from .base_consumer import BaseConsumer
from .models import DonationRequest, DonationItem
from .schemas import MessageValidator
from .config import Topics, settings

logger = structlog.get_logger(__name__)


class DonationRequestConsumer(BaseConsumer):
    """Consumer for external donation request messages"""
    
    def __init__(self):
        super().__init__(
            topics=[Topics.DONATION_REQUESTS]
        )
    
    def setup_handlers(self):
        """Setup message handlers - required by BaseConsumer"""
        # This consumer processes messages directly via process_message method
        pass
    
    def process_message(self, message: Dict[str, Any]) -> bool:
        """
        Process incoming donation request message
        
        Args:
            message: Kafka message containing donation request
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            logger.info(
                "Processing donation request message",
                message_id=message.get("message_id"),
                organization_id=message.get("organization_id")
            )
            
            # Extract message data
            message_data = message.get("data", {})
            
            # Skip our own messages
            if message_data.get("organization_id") == settings.organization_id:
                logger.info(
                    "Skipping own donation request message",
                    request_id=message_data.get("request_id")
                )
                return True
            
            # Validate message format
            if not self._validate_message_format(message_data):
                logger.error("Invalid donation request message format", message=message_data)
                return False
            
            # Validate against schema
            try:
                MessageValidator.validate_message("donation_request", message_data)
            except Exception as e:
                logger.error(
                    "Message schema validation failed",
                    error=str(e),
                    message=message_data
                )
                return False
            
            # Create donation request model
            donation_request = DonationRequest.from_dict(message_data)
            
            # Store external request in database
            success = self._store_external_request(donation_request)
            
            if success:
                logger.info(
                    "External donation request processed successfully",
                    organization_id=donation_request.organization_id,
                    request_id=donation_request.request_id,
                    donations_count=len(donation_request.donations)
                )
                
                # Log message processing for audit
                self._log_message_processing(message, "PROCESADO")
                
                return True
            else:
                logger.error(
                    "Failed to store external donation request",
                    organization_id=donation_request.organization_id,
                    request_id=donation_request.request_id
                )
                
                # Log processing error
                self._log_message_processing(message, "ERROR", "Failed to store in database")
                
                return False
                
        except Exception as e:
            logger.error(
                "Error processing donation request message",
                error=str(e),
                error_type=type(e).__name__,
                message=message
            )
            
            # Log processing error
            self._log_message_processing(message, "ERROR", str(e))
            
            return False
    
    def get_external_requests(self, active_only: bool = True) -> list:
        """
        Get external donation requests from database
        
        Args:
            active_only: If True, return only active requests
            
        Returns:
            List of external donation requests
        """
        try:
            from .database import get_database_connection
            
            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    if active_only:
                        cursor.execute("""
                            SELECT organizacion_solicitante, solicitud_id, donaciones, fecha_creacion
                            FROM solicitudes_externas 
                            WHERE activa = true
                            ORDER BY fecha_creacion DESC
                        """)
                    else:
                        cursor.execute("""
                            SELECT organizacion_solicitante, solicitud_id, donaciones, fecha_creacion, activa
                            FROM solicitudes_externas 
                            ORDER BY fecha_creacion DESC
                        """)
                    
                    results = cursor.fetchall()
                    requests = []
                    
                    for row in results:
                        request_data = {
                            "organization_id": row[0],
                            "request_id": row[1],
                            "donations": row[2],
                            "created_date": row[3].isoformat() if row[3] else None
                        }
                        
                        if not active_only:
                            request_data["active"] = row[4]
                        
                        requests.append(request_data)
                    
                    return requests
                    
        except Exception as e:
            logger.error("Error getting external requests", error=str(e))
            return []
    
    def _validate_message_format(self, message_data: Dict[str, Any]) -> bool:
        """Validate basic message format"""
        required_fields = ["organization_id", "request_id", "donations", "timestamp"]
        
        for field in required_fields:
            if field not in message_data:
                logger.error("Missing required field", field=field)
                return False
        
        # Validate donations is a list
        if not isinstance(message_data["donations"], list) or len(message_data["donations"]) == 0:
            logger.error("Donations must be a non-empty list")
            return False
        
        # Validate each donation item
        for i, donation in enumerate(message_data["donations"]):
            if not isinstance(donation, dict):
                logger.error("Donation item must be a dict", index=i)
                return False
            
            if "category" not in donation or "description" not in donation:
                logger.error("Donation item missing required fields", index=i, donation=donation)
                return False
        
        return True
    
    def _store_external_request(self, donation_request: DonationRequest) -> bool:
        """Store external donation request in database"""
        try:
            from .database import get_database_connection
            
            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    # Check if request already exists
                    cursor.execute("""
                        SELECT id FROM solicitudes_externas 
                        WHERE organizacion_solicitante = %s AND solicitud_id = %s
                    """, (donation_request.organization_id, donation_request.request_id))
                    
                    existing = cursor.fetchone()
                    
                    if existing:
                        logger.info(
                            "External donation request already exists, updating",
                            organization_id=donation_request.organization_id,
                            request_id=donation_request.request_id
                        )
                        
                        # Update existing request
                        cursor.execute("""
                            UPDATE solicitudes_externas 
                            SET donaciones = %s, activa = true, fecha_creacion = CURRENT_TIMESTAMP
                            WHERE organizacion_solicitante = %s AND solicitud_id = %s
                        """, (
                            json.dumps([d.to_dict() for d in donation_request.donations]),
                            donation_request.organization_id,
                            donation_request.request_id
                        ))
                    else:
                        # Insert new request
                        cursor.execute("""
                            INSERT INTO solicitudes_externas 
                            (organizacion_solicitante, solicitud_id, donaciones, activa)
                            VALUES (%s, %s, %s, true)
                        """, (
                            donation_request.organization_id,
                            donation_request.request_id,
                            json.dumps([d.to_dict() for d in donation_request.donations])
                        ))
                    
                    conn.commit()
                    
                    logger.info(
                        "External donation request stored successfully",
                        organization_id=donation_request.organization_id,
                        request_id=donation_request.request_id
                    )
                    
                    return True
                    
        except Exception as e:
            logger.error(
                "Error storing external donation request",
                error=str(e),
                organization_id=donation_request.organization_id,
                request_id=donation_request.request_id
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
                        Topics.DONATION_REQUESTS,
                        "donation_request",
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