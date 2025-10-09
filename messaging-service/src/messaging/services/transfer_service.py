"""
Transfer Service for managing donation transfers
"""
import uuid
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import structlog

from messaging.config import settings
from messaging.database.connection import get_db_connection
from messaging.producers.base_producer import BaseProducer

logger = structlog.get_logger(__name__)


class TransferService:
    """Service for managing donation transfers"""
    
    def __init__(self):
        self.producer = BaseProducer()
    
    def transfer_donations(self, target_organization: str, request_id: str, donations: List[Dict], user_id: int) -> Tuple[bool, str, Optional[str]]:
        """
        Transfer donations to another organization
        
        Args:
            target_organization: ID of the target organization
            request_id: ID of the donation request being fulfilled
            donations: List of donation items to transfer
            user_id: ID of the user making the transfer
            
        Returns:
            Tuple of (success, message, transfer_id)
        """
        try:
            # Generate transfer ID
            transfer_id = f"transfer-{settings.organization_id}-{uuid.uuid4().hex[:8]}"
            
            # Validate donations
            if not donations or not isinstance(donations, list):
                return False, "Donations list is required", None
            
            for donation in donations:
                if not donation.get('donation_id') or not donation.get('quantity'):
                    return False, "Each donation must have donation_id and quantity", None
                
                if donation.get('quantity', 0) <= 0:
                    return False, "Donation quantity must be positive", None
            
            # Store transfer in database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                # Check if we have enough inventory for each donation
                for donation in donations:
                    cursor.execute("""
                        SELECT quantity FROM donations 
                        WHERE id = %s AND organization_id = %s
                    """, (donation['donation_id'], settings.organization_id))
                    
                    row = cursor.fetchone()
                    if not row:
                        return False, f"Donation {donation['donation_id']} not found", None
                    
                    available_quantity = row[0]
                    requested_quantity = donation['quantity']
                    
                    if available_quantity < requested_quantity:
                        return False, f"Insufficient quantity for donation {donation['donation_id']}. Available: {available_quantity}, Requested: {requested_quantity}", None
                
                # Create transfer record
                cursor.execute("""
                    INSERT INTO transferencias_donaciones 
                    (transferencia_id, organizacion_origen, organizacion_destino, solicitud_id, donaciones, fecha_transferencia, usuario_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    transfer_id,
                    settings.organization_id,
                    target_organization,
                    request_id,
                    str(donations),  # Store as JSON string
                    datetime.now(),
                    user_id
                ))
                
                # Update inventory quantities
                for donation in donations:
                    cursor.execute("""
                        UPDATE donations 
                        SET quantity = quantity - %s 
                        WHERE id = %s AND organization_id = %s
                    """, (donation['quantity'], donation['donation_id'], settings.organization_id))
                
                conn.commit()
                
                logger.info(
                    "Donation transfer stored in database",
                    transfer_id=transfer_id,
                    target_organization=target_organization,
                    donations_count=len(donations)
                )
                
            except Exception as e:
                conn.rollback()
                logger.error("Failed to store donation transfer in database", error=str(e))
                return False, f"Database error: {str(e)}", None
            finally:
                cursor.close()
                conn.close()
            
            # Publish to Kafka
            transfer_data = {
                'transfer_id': transfer_id,
                'source_organization': settings.organization_id,
                'target_organization': target_organization,
                'request_id': request_id,
                'donations': donations,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id
            }
            
            success = self.producer.publish_donation_transfer(target_organization, transfer_data)
            
            if success:
                logger.info(
                    "Donation transfer published successfully",
                    transfer_id=transfer_id,
                    target_organization=target_organization
                )
                return True, "Donation transfer completed successfully", transfer_id
            else:
                logger.error("Failed to publish donation transfer to Kafka")
                return False, "Failed to publish transfer to network", None
                
        except Exception as e:
            logger.error("Error transferring donations", error=str(e))
            return False, f"Internal error: {str(e)}", None
    
    def get_transfer_history(self, organization_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """
        Get transfer history for an organization
        
        Args:
            organization_id: ID of the organization (defaults to current organization)
            limit: Maximum number of transfers to return
            
        Returns:
            List of transfer records
        """
        try:
            if organization_id is None:
                organization_id = settings.organization_id
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT 
                        transferencia_id as transfer_id,
                        organizacion_origen as source_organization,
                        organizacion_destino as target_organization,
                        solicitud_id as request_id,
                        donaciones as donations,
                        fecha_transferencia as timestamp,
                        usuario_id as user_id
                    FROM transferencias_donaciones 
                    WHERE organizacion_origen = %s OR organizacion_destino = %s
                    ORDER BY fecha_transferencia DESC
                    LIMIT %s
                """, (organization_id, organization_id, limit))
                
                rows = cursor.fetchall()
                
                transfers = []
                for row in rows:
                    # Parse donations JSON
                    donations_str = row[4]
                    try:
                        if isinstance(donations_str, str):
                            import json
                            donations = json.loads(donations_str)
                        else:
                            donations = donations_str
                    except:
                        donations = []
                    
                    transfers.append({
                        'transfer_id': row[0],
                        'source_organization': row[1],
                        'target_organization': row[2],
                        'request_id': row[3],
                        'donations': donations,
                        'timestamp': row[5].isoformat() if row[5] else None,
                        'user_id': row[6]
                    })
                
                logger.info(
                    "Retrieved transfer history",
                    count=len(transfers),
                    organization_id=organization_id
                )
                
                return transfers
                
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            logger.error("Error getting transfer history", error=str(e))
            return []