"""
Request Service for managing donation requests
"""
import uuid
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import structlog

from messaging.config import settings
from messaging.database.connection import get_db_connection
from messaging.producers.base_producer import BaseProducer

logger = structlog.get_logger(__name__)


class RequestService:
    """Service for managing donation requests"""
    
    def __init__(self):
        self.producer = BaseProducer()
    
    def create_donation_request(self, donations: List[Dict], user_id: int, notes: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new donation request and publish it to the network
        
        Args:
            donations: List of donation items needed
            user_id: ID of the user creating the request
            notes: Optional notes for the request
            
        Returns:
            Tuple of (success, message, request_id)
        """
        try:
            # Generate request ID
            request_id = f"req-{settings.organization_id}-{uuid.uuid4().hex[:8]}"
            
            # Validate donations
            if not donations or not isinstance(donations, list):
                return False, "Donations list is required", None
            
            for donation in donations:
                if not donation.get('category') or not donation.get('description'):
                    return False, "Each donation must have category and description", None
            
            # Store request in database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                # Insert into solicitudes_externas table
                cursor.execute("""
                    INSERT INTO solicitudes_externas 
                    (solicitud_id, organizacion_solicitante, donaciones, fecha_creacion, activa, notas)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    request_id,
                    settings.organization_id,
                    str(donations),  # Store as JSON string
                    datetime.now(),
                    True,
                    notes or ''
                ))
                
                conn.commit()
                
                logger.info(
                    "Donation request stored in database",
                    request_id=request_id,
                    donations_count=len(donations)
                )
                
            except Exception as e:
                conn.rollback()
                logger.error("Failed to store donation request in database", error=str(e))
                return False, f"Database error: {str(e)}", None
            finally:
                cursor.close()
                conn.close()
            
            # Publish to Kafka
            success = self.producer.publish_donation_request(request_id, donations)
            
            if success:
                logger.info(
                    "Donation request published successfully",
                    request_id=request_id,
                    organization_id=settings.organization_id
                )
                return True, "Donation request created and published successfully", request_id
            else:
                logger.error("Failed to publish donation request to Kafka")
                return False, "Failed to publish request to network", None
                
        except Exception as e:
            logger.error("Error creating donation request", error=str(e))
            return False, f"Internal error: {str(e)}", None
    
    def get_external_requests(self, active_only: bool = True) -> List[Dict]:
        """
        Get external donation requests from other organizations
        
        Args:
            active_only: If True, only return active requests
            
        Returns:
            List of external donation requests
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                query = """
                    SELECT 
                        solicitud_id as request_id,
                        organizacion_solicitante as organization_id,
                        organizacion_solicitante as organization_name,
                        donaciones as donations,
                        fecha_creacion as timestamp,
                        activa as active,
                        notas as notes
                    FROM solicitudes_externas 
                    WHERE organizacion_solicitante != %s
                """
                
                params = [settings.organization_id]
                
                if active_only:
                    query += " AND activa = true"
                
                query += " ORDER BY fecha_creacion DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                requests = []
                for row in rows:
                    # Parse donations JSON
                    donations_str = row[3]
                    try:
                        if isinstance(donations_str, str):
                            import json
                            donations = json.loads(donations_str)
                        else:
                            donations = donations_str
                    except:
                        donations = []
                    
                    requests.append({
                        'request_id': row[0],
                        'organization_id': row[1],
                        'organization_name': row[2],
                        'donations': donations,
                        'timestamp': row[4].isoformat() if row[4] else None,
                        'active': row[5],
                        'notes': row[6] or ''
                    })
                
                logger.info(
                    "Retrieved external donation requests",
                    count=len(requests),
                    active_only=active_only
                )
                
                return requests
                
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            logger.error("Error getting external donation requests", error=str(e))
            return []
    
    def get_active_requests(self) -> List[Dict]:
        """
        Get our own active donation requests
        
        Returns:
            List of our active donation requests
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT 
                        solicitud_id as request_id,
                        organizacion_solicitante as organization_id,
                        donaciones as donations,
                        fecha_creacion as timestamp,
                        activa as active,
                        notas as notes
                    FROM solicitudes_externas 
                    WHERE organizacion_solicitante = %s AND activa = true
                    ORDER BY fecha_creacion DESC
                """, (settings.organization_id,))
                
                rows = cursor.fetchall()
                
                requests = []
                for row in rows:
                    # Parse donations JSON
                    donations_str = row[2]
                    try:
                        if isinstance(donations_str, str):
                            import json
                            donations = json.loads(donations_str)
                        else:
                            donations = donations_str
                    except:
                        donations = []
                    
                    requests.append({
                        'request_id': row[0],
                        'organization_id': row[1],
                        'donations': donations,
                        'timestamp': row[3].isoformat() if row[3] else None,
                        'active': row[4],
                        'notes': row[5] or ''
                    })
                
                logger.info(
                    "Retrieved active donation requests",
                    count=len(requests)
                )
                
                return requests
                
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            logger.error("Error getting active donation requests", error=str(e))
            return []
    
    def cancel_donation_request(self, request_id: str, user_id: int) -> Tuple[bool, str]:
        """
        Cancel a donation request
        
        Args:
            request_id: ID of the request to cancel
            user_id: ID of the user canceling the request
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Update request in database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                # Check if request exists and belongs to our organization
                cursor.execute("""
                    SELECT organizacion_solicitante, activa 
                    FROM solicitudes_externas 
                    WHERE solicitud_id = %s
                """, (request_id,))
                
                row = cursor.fetchone()
                if not row:
                    return False, "Request not found"
                
                if row[0] != settings.organization_id:
                    return False, "Cannot cancel request from another organization"
                
                if not row[1]:
                    return False, "Request is already inactive"
                
                # Update request to inactive
                cursor.execute("""
                    UPDATE solicitudes_externas 
                    SET activa = false 
                    WHERE solicitud_id = %s
                """, (request_id,))
                
                conn.commit()
                
                logger.info(
                    "Donation request cancelled in database",
                    request_id=request_id,
                    user_id=user_id
                )
                
            except Exception as e:
                conn.rollback()
                logger.error("Failed to cancel donation request in database", error=str(e))
                return False, f"Database error: {str(e)}"
            finally:
                cursor.close()
                conn.close()
            
            # Publish cancellation to Kafka
            success = self.producer.publish_request_cancellation(request_id)
            
            if success:
                logger.info(
                    "Donation request cancellation published successfully",
                    request_id=request_id
                )
                return True, "Donation request cancelled successfully"
            else:
                logger.error("Failed to publish request cancellation to Kafka")
                return False, "Failed to publish cancellation to network"
                
        except Exception as e:
            logger.error("Error cancelling donation request", error=str(e))
            return False, f"Internal error: {str(e)}"