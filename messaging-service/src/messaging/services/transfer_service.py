"""
Transfer Service for managing donation transfers
"""
import uuid
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import structlog

from messaging.config import settings
from messaging.database.connection import get_db_connection, get_database_connection
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
                # Accept both formats: frontend format (inventoryId) and legacy format (donation_id)
                inventory_id = donation.get('inventoryId') or donation.get('donation_id')
                quantity_str = donation.get('quantity', '')
                
                if not inventory_id:
                    return False, "Each donation must have inventoryId or donation_id", None
                
                # Extract numeric quantity from string (e.g., "5kg" -> 5)
                try:
                    if isinstance(quantity_str, str):
                        # Extract number from string like "5kg", "10 unidades", etc.
                        import re
                        quantity_match = re.search(r'(\d+)', quantity_str)
                        if quantity_match:
                            quantity = int(quantity_match.group(1))
                        else:
                            quantity = 0
                    else:
                        quantity = int(quantity_str) if quantity_str else 0
                except (ValueError, TypeError):
                    quantity = 0
                
                if quantity <= 0:
                    return False, f"Donation quantity must be positive, got: {quantity_str}", None
                
                # Store the parsed quantity back in the donation for later use
                donation['parsed_quantity'] = quantity
                donation['inventory_id'] = inventory_id
            
            # Store transfer in database
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                try:
                    # Check if we have enough inventory for each donation
                    for donation in donations:
                        inventory_id = donation['inventory_id']
                        requested_quantity = donation['parsed_quantity']
                        
                        cursor.execute("""
                            SELECT cantidad FROM donaciones 
                            WHERE id = %s AND eliminado = 0
                        """, (inventory_id,))
                        
                        row = cursor.fetchone()
                        if not row:
                            return False, f"Donation {inventory_id} not found in inventory", None
                        
                        available_quantity = row[0]
                        
                        if available_quantity < requested_quantity:
                            return False, f"Insufficient quantity for donation {inventory_id}. Available: {available_quantity}, Requested: {requested_quantity}", None
                    
                    # Create transfer record
                    import json
                    cursor.execute("""
                        INSERT INTO transferencias_donaciones 
                        (tipo, organizacion_contraparte, solicitud_id, donaciones, estado, fecha_transferencia, notas, organizacion_propietaria)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        'ENVIADA',
                        target_organization,
                        request_id,
                        json.dumps(donations),  # Store as proper JSON string
                        'COMPLETADA',
                        datetime.now(),
                        f'Transfer {transfer_id} by user {user_id}',
                        settings.organization_id  # Current organization is the owner
                    ))
                    
                    # Update inventory quantities
                    for donation in donations:
                        inventory_id = donation['inventory_id']
                        requested_quantity = donation['parsed_quantity']
                        
                        cursor.execute("""
                            UPDATE donaciones 
                            SET cantidad = cantidad - %s 
                            WHERE id = %s
                        """, (requested_quantity, inventory_id))
                    
                    # Crear transferencia RECIBIDA directamente (temporal fix para consumer)
                    try:
                        logger.info("Creating RECIBIDA transfer", target_org=target_organization, source_org=settings.organization_id)
                        
                        cursor.execute("""
                            INSERT INTO transferencias_donaciones 
                            (tipo, organizacion_contraparte, solicitud_id, donaciones, estado, fecha_transferencia, notas, organizacion_propietaria)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            'RECIBIDA',
                            settings.organization_id,  # Organización que envía
                            request_id,
                            json.dumps(donations),
                            'COMPLETADA',
                            datetime.now(),
                            f'Transferencia recibida automáticamente - {transfer_id}',
                            target_organization  # Organización que recibe es la propietaria
                        ))
                        
                        recibida_id = cursor.lastrowid
                        logger.info("RECIBIDA transfer created", transfer_id=recibida_id)
                        
                        # Crear notificación para la organización receptora
                        # Buscar un admin de la organización destino
                        cursor.execute("""
                            SELECT id FROM usuarios 
                            WHERE organizacion = %s AND rol IN ('PRESIDENTE', 'COORDINADOR') 
                            LIMIT 1
                        """, (target_organization,))
                        
                        user_row = cursor.fetchone()
                        logger.info("Found target user", user_found=user_row is not None, target_org=target_organization)
                        
                        if user_row:
                            target_user_id = user_row[0]
                            
                            donations_text = "\n".join([
                                f"• {d.get('description', 'Donación')} ({d.get('quantity', '1')})"
                                for d in donations
                            ])
                            
                            cursor.execute("""
                                INSERT INTO notificaciones 
                                (usuario_id, tipo, titulo, mensaje, datos_adicionales, leida, fecha_creacion)
                                VALUES (%s, %s, %s, %s, %s, false, NOW())
                            """, (
                                target_user_id,
                                'transferencia_recibida',
                                '🎁 ¡Nueva donación recibida!',
                                f'Has recibido una donación de {settings.organization_id}:\n\n{donations_text}\n\nLas donaciones ya están disponibles en tu inventario.',
                                json.dumps({
                                    'organizacion_origen': settings.organization_id,
                                    'request_id': request_id,
                                    'cantidad_items': len(donations),
                                    'transfer_id': transfer_id
                                })
                            ))
                            
                            notification_id = cursor.lastrowid
                            logger.info("Notification created", notification_id=notification_id, user_id=target_user_id)
                        
                    except Exception as e:
                        logger.error("Error creating transfer reception", error=str(e))
                        import traceback
                        logger.error("Traceback", traceback=traceback.format_exc())
                        # No hacer rollback del transfer principal
                    
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
            
            logger.info("About to publish to Kafka", transfer_data=transfer_data, target_org=target_organization)
            success = self.producer.publish_donation_transfer(target_organization, transfer_data)
            logger.info("Kafka publish result", success=success)
            
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
            
            logger.info("Getting transfer history", organization_id=organization_id, limit=limit)
            
            with get_database_connection() as conn:
                cursor = conn.cursor()
                
                # Query using the actual table structure
                query = """
                    SELECT 
                        id,
                        tipo,
                        organizacion_contraparte,
                        solicitud_id,
                        donaciones,
                        estado,
                        fecha_transferencia,
                        usuario_registro,
                        notas,
                        organizacion_propietaria
                    FROM transferencias_donaciones 
                    WHERE organizacion_propietaria = %s
                    ORDER BY fecha_transferencia DESC
                    LIMIT %s
                """
                
                logger.info("Executing query", query=query, params=(organization_id, limit))
                cursor.execute(query, (organization_id, limit))
                
                rows = cursor.fetchall()
                logger.info("Query executed", rows_found=len(rows))
                
                transfers = []
                for row in rows:
                    logger.info("Processing row", row=row)
                    
                    # Parse donations JSON
                    donations_str = row[4]
                    try:
                        if isinstance(donations_str, str):
                            import json
                            donations = json.loads(donations_str)
                        else:
                            donations = donations_str
                    except Exception as json_error:
                        logger.error("Error parsing donations JSON", error=str(json_error), donations_str=donations_str)
                        donations = []
                    
                    # Determine source and target based on type
                    if row[1] == 'ENVIADA':  # tipo = 'ENVIADA'
                        source_org = organization_id
                        target_org = row[2]  # organizacion_contraparte
                    else:  # tipo = 'RECIBIDA'
                        source_org = row[2]  # organizacion_contraparte
                        target_org = organization_id
                    
                    transfer_record = {
                        'id': row[0],
                        'transfer_id': f"transfer-{row[0]}",
                        'tipo': row[1],
                        'source_organization': source_org,
                        'target_organization': target_org,
                        'organizacion_contraparte': row[2],
                        'request_id': row[3],
                        'donations': donations,
                        'estado': row[5],
                        'timestamp': row[6].isoformat() if row[6] else None,
                        'fecha_transferencia': row[6].isoformat() if row[6] else None,
                        'user_id': row[7],
                        'notas': row[8],
                        'organizacion_propietaria': row[9]
                    }
                    
                    logger.info("Created transfer record", transfer=transfer_record)
                    transfers.append(transfer_record)
                
                logger.info(
                    "Retrieved transfer history",
                    count=len(transfers),
                    organization_id=organization_id
                )
                
                return transfers
                
        except Exception as e:
            logger.error("Error getting transfer history", error=str(e), organization_id=organization_id)
            return []