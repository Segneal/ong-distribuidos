"""
Consumer for donation request messages
"""
import json
from datetime import datetime
from typing import Dict, Any
import structlog

from messaging.consumers.base_consumer import BaseConsumer
from messaging.database.connection import get_db_connection
from messaging.config import settings, Topics

logger = structlog.get_logger(__name__)


class DonationRequestConsumer(BaseConsumer):
    """Consumer for processing donation request messages"""
    
    def __init__(self):
        super().__init__(
            topics=[Topics.DONATION_REQUESTS],
            consumer_group=f"donation-requests-{settings.organization_id}"
        )
    
    def process_message(self, message: Dict[str, Any]) -> bool:
        """
        Process donation request message
        
        Args:
            message: The message data
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            message_type = message.get("type")
            
            if message_type == "donation_request":
                return self._handle_donation_request(message)
            else:
                logger.warning("Unknown message type", message_type=message_type)
                return True  # Don't retry unknown message types
                
        except Exception as e:
            logger.error("Error processing donation request message", error=str(e))
            return False
    
    def _handle_donation_request(self, message: Dict[str, Any]) -> bool:
        """
        Handle incoming donation request
        
        Args:
            message: The donation request message
            
        Returns:
            True if handled successfully, False otherwise
        """
        try:
            # Extract message data
            organization_id = message.get("organization_id")
            request_id = message.get("request_id")
            donations = message.get("donations", [])
            timestamp_str = message.get("timestamp")
            
            # Skip our own messages
            if organization_id == settings.organization_id:
                logger.debug("Skipping own donation request message", request_id=request_id)
                return True
            
            # Validate required fields
            if not all([organization_id, request_id, donations]):
                logger.error("Missing required fields in donation request", message=message)
                return False
            
            # Parse timestamp
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.utcnow()
            
            # Store in database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                # Check if request already exists
                cursor.execute("""
                    SELECT solicitud_id FROM solicitudes_externas 
                    WHERE solicitud_id = %s
                """, (request_id,))
                
                if cursor.fetchone():
                    logger.debug("Donation request already exists", request_id=request_id)
                    return True
                
                # Insert new request
                cursor.execute("""
                    INSERT INTO solicitudes_externas 
                    (solicitud_id, organizacion_solicitante, donaciones, fecha_creacion, activa, notas)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    request_id,
                    organization_id,
                    json.dumps(donations),
                    timestamp,
                    True,
                    ''
                ))
                
                conn.commit()
                
                logger.info(
                    "Donation request stored successfully",
                    request_id=request_id,
                    organization_id=organization_id,
                    donations_count=len(donations)
                )
                
                return True
                
            except Exception as e:
                conn.rollback()
                logger.error("Database error storing donation request", error=str(e))
                return False
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            logger.error("Error handling donation request", error=str(e))
            return False


class RequestCancellationConsumer(BaseConsumer):
    """Consumer for processing request cancellation messages"""
    
    def __init__(self):
        super().__init__(
            topics=[Topics.REQUEST_CANCELLATIONS],
            consumer_group=f"request-cancellations-{settings.organization_id}"
        )
    
    def process_message(self, message: Dict[str, Any]) -> bool:
        """
        Process request cancellation message
        
        Args:
            message: The message data
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            message_type = message.get("type")
            
            if message_type == "request_cancellation":
                return self._handle_request_cancellation(message)
            else:
                logger.warning("Unknown message type", message_type=message_type)
                return True
                
        except Exception as e:
            logger.error("Error processing request cancellation message", error=str(e))
            return False
    
    def _handle_request_cancellation(self, message: Dict[str, Any]) -> bool:
        """
        Handle request cancellation
        
        Args:
            message: The cancellation message
            
        Returns:
            True if handled successfully, False otherwise
        """
        try:
            # Extract message data
            organization_id = message.get("organization_id")
            request_id = message.get("request_id")
            
            # Skip our own messages
            if organization_id == settings.organization_id:
                logger.debug("Skipping own request cancellation message", request_id=request_id)
                return True
            
            # Validate required fields
            if not all([organization_id, request_id]):
                logger.error("Missing required fields in request cancellation", message=message)
                return False
            
            # Update in database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                # Update request to inactive
                cursor.execute("""
                    UPDATE solicitudes_externas 
                    SET activa = false 
                    WHERE solicitud_id = %s AND organizacion_solicitante = %s
                """, (request_id, organization_id))
                
                rows_affected = cursor.rowcount
                conn.commit()
                
                if rows_affected > 0:
                    logger.info(
                        "Request cancelled successfully",
                        request_id=request_id,
                        organization_id=organization_id
                    )
                else:
                    logger.warning(
                        "Request not found for cancellation",
                        request_id=request_id,
                        organization_id=organization_id
                    )
                
                return True
                
            except Exception as e:
                conn.rollback()
                logger.error("Database error cancelling request", error=str(e))
                return False
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            logger.error("Error handling request cancellation", error=str(e))
            return False