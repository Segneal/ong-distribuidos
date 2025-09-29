"""
Donation Request Producer for ONG Network Messaging
Handles publishing donation requests to the network
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import structlog

from .base_producer import BaseProducer
from ..models.donation import DonationRequest, DonationItem
from ..config import Topics

logger = structlog.get_logger(__name__)


class DonationRequestProducer(BaseProducer):
    """Producer for donation request messages"""
    
    def create_donation_request(self, donations: List[Dict[str, Any]], user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Create and publish a donation request to the network
        
        Args:
            donations: List of donation items with category and description
            user_id: ID of user creating the request (for database record)
            
        Returns:
            Dict with success status, request_id, and message
        """
        try:
            # Generate unique request ID
            request_id = f"REQ-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            logger.info(
                "Creating donation request",
                request_id=request_id,
                donations_count=len(donations),
                user_id=user_id
            )
            
            # Validate donation items
            validated_donations = []
            for donation_data in donations:
                if not self._validate_donation_item(donation_data):
                    return {
                        "success": False,
                        "error": f"Invalid donation item: {donation_data}",
                        "request_id": None
                    }
                
                donation_item = DonationItem(
                    category=donation_data["category"],
                    description=donation_data["description"]
                )
                validated_donations.append(donation_item)
            
            # Create donation request model
            donation_request = DonationRequest(
                organization_id=self.organization_id,
                request_id=request_id,
                donations=validated_donations,
                timestamp=datetime.utcnow().isoformat()
            )
            
            # Get message data
            message_data = donation_request.to_dict()
            
            # Store in local database first
            db_result = self._store_request_in_database(request_id, donations, user_id)
            if not db_result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to store request in database: {db_result['error']}",
                    "request_id": request_id
                }
            
            # Publish to Kafka
            success = self._publish_message(Topics.DONATION_REQUESTS, message_data)
            
            if success:
                logger.info(
                    "Donation request published successfully",
                    request_id=request_id,
                    organization_id=self.organization_id
                )
                return {
                    "success": True,
                    "message": "Solicitud de donación creada y publicada exitosamente",
                    "request_id": request_id
                }
            else:
                # If Kafka publish fails, mark database record as failed
                self._update_request_status(request_id, "DADA_DE_BAJA")
                return {
                    "success": False,
                    "error": "Failed to publish donation request to network",
                    "request_id": request_id
                }
                
        except Exception as e:
            logger.error(
                "Error creating donation request",
                error=str(e),
                error_type=type(e).__name__,
                donations=donations
            )
            return {
                "success": False,
                "error": f"Internal error: {str(e)}",
                "request_id": None
            }
    
    def cancel_donation_request(self, request_id: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Cancel a donation request and publish cancellation to network
        
        Args:
            request_id: ID of request to cancel
            user_id: ID of user canceling the request
            
        Returns:
            Dict with success status and message
        """
        try:
            logger.info(
                "Canceling donation request",
                request_id=request_id,
                user_id=user_id
            )
            
            # Check if request exists and is active
            request_data = self._get_request_from_database(request_id)
            if not request_data:
                return {
                    "success": False,
                    "error": "Solicitud de donación no encontrada"
                }
            
            if request_data["estado"] != "ACTIVA":
                return {
                    "success": False,
                    "error": "La solicitud ya no está activa"
                }
            
            # Update database status
            db_result = self._update_request_status(request_id, "DADA_DE_BAJA", user_id)
            if not db_result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to update request status: {db_result['error']}"
                }
            
            # Publish cancellation to Kafka
            success = self.publish_request_cancellation(request_id)
            
            if success:
                logger.info(
                    "Donation request cancellation published successfully",
                    request_id=request_id
                )
                return {
                    "success": True,
                    "message": "Solicitud de donación dada de baja exitosamente"
                }
            else:
                # Rollback database change if Kafka fails
                self._update_request_status(request_id, "ACTIVA", user_id)
                return {
                    "success": False,
                    "error": "Failed to publish cancellation to network"
                }
                
        except Exception as e:
            logger.error(
                "Error canceling donation request",
                error=str(e),
                request_id=request_id
            )
            return {
                "success": False,
                "error": f"Internal error: {str(e)}"
            }
    
    def get_active_requests(self) -> List[Dict[str, Any]]:
        """Get all active donation requests from our organization"""
        try:
            from .database import get_database_connection
            
            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT solicitud_id, donaciones, fecha_creacion, notas
                        FROM solicitudes_donaciones 
                        WHERE estado = 'ACTIVA'
                        ORDER BY fecha_creacion DESC
                    """)
                    
                    results = cursor.fetchall()
                    requests = []
                    
                    for row in results:
                        requests.append({
                            "request_id": row[0],
                            "donations": row[1],
                            "created_date": row[2].isoformat() if row[2] else None,
                            "notes": row[3]
                        })
                    
                    return requests
                    
        except Exception as e:
            logger.error("Error getting active requests", error=str(e))
            return []
    
    def _validate_donation_item(self, donation_data: Dict[str, Any]) -> bool:
        """Validate individual donation item"""
        required_fields = ["category", "description"]
        
        for field in required_fields:
            if field not in donation_data or not donation_data[field]:
                logger.error("Missing required field in donation item", field=field)
                return False
        
        # Validate category
        valid_categories = ["ROPA", "ALIMENTOS", "JUGUETES", "UTILES_ESCOLARES"]
        if donation_data["category"] not in valid_categories:
            logger.error("Invalid category", category=donation_data["category"])
            return False
        
        return True
    
    def _store_request_in_database(self, request_id: str, donations: List[Dict[str, Any]], user_id: Optional[int]) -> Dict[str, Any]:
        """Store donation request in local database"""
        try:
            from ..database.connection import get_database_connection
            import json
            
            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO solicitudes_donaciones 
                        (solicitud_id, donaciones, usuario_creacion)
                        VALUES (%s, %s, %s)
                    """, (request_id, json.dumps(donations), user_id))
                    
                    conn.commit()
                    
                    logger.info(
                        "Donation request stored in database",
                        request_id=request_id
                    )
                    
                    return {"success": True}
                    
        except Exception as e:
            logger.error(
                "Error storing request in database",
                error=str(e),
                request_id=request_id
            )
            return {"success": False, "error": str(e)}
    
    def _get_request_from_database(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get donation request from database"""
        try:
            from ..database.connection import get_database_connection
            
            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT solicitud_id, donaciones, estado, fecha_creacion, notas
                        FROM solicitudes_donaciones 
                        WHERE solicitud_id = %s
                    """, (request_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        return {
                            "solicitud_id": row[0],
                            "donaciones": row[1],
                            "estado": row[2],
                            "fecha_creacion": row[3],
                            "notas": row[4]
                        }
                    return None
                    
        except Exception as e:
            logger.error(
                "Error getting request from database",
                error=str(e),
                request_id=request_id
            )
            return None
    
    def _update_request_status(self, request_id: str, status: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Update donation request status in database"""
        try:
            from ..database.connection import get_database_connection
            
            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE solicitudes_donaciones 
                        SET estado = %s, usuario_actualizacion = %s, fecha_actualizacion = CURRENT_TIMESTAMP
                        WHERE solicitud_id = %s
                    """, (status, user_id, request_id))
                    
                    conn.commit()
                    
                    logger.info(
                        "Request status updated",
                        request_id=request_id,
                        status=status
                    )
                    
                    return {"success": True}
                    
        except Exception as e:
            logger.error(
                "Error updating request status",
                error=str(e),
                request_id=request_id,
                status=status
            )
            return {"success": False, "error": str(e)}