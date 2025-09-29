"""
Transfer Service for ONG Network Messaging System
Handles donation transfer operations with inventory validation
"""
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import structlog

from ..producers.transfer_producer import DonationTransferProducer
from ..database.manager import DatabaseManager
from ..config import settings

logger = structlog.get_logger(__name__)


class TransferService:
    """Service for handling donation transfers with inventory validation"""
    
    def __init__(self):
        self.producer = DonationTransferProducer()
        self.db_manager = DatabaseManager()
    
    def transfer_donations(
        self, 
        target_org: str, 
        request_id: str, 
        donations: List[Dict[str, Any]], 
        transferred_by: int
    ) -> Tuple[bool, str]:
        """
        Transfer donations to target organization with inventory validation
        
        Args:
            target_org: Target organization ID
            request_id: Original request ID being fulfilled
            donations: List of donation items with donation_id and quantity
            transferred_by: User ID performing the transfer
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            logger.info(
                "Starting donation transfer",
                target_org=target_org,
                request_id=request_id,
                donations_count=len(donations),
                transferred_by=transferred_by
            )
            
            # Validate inputs
            if not target_org or not request_id or not donations:
                return False, "Parámetros de transferencia inválidos"
            
            # Validate and prepare transfer data
            transfer_items, validation_error = self._validate_and_prepare_transfer(donations)
            if validation_error:
                return False, validation_error
            
            # Check inventory availability
            availability_check, availability_error = self._check_inventory_availability(donations)
            if not availability_check:
                return False, availability_error
            
            # Execute transfer (reduce inventory and publish message)
            success, error_msg = self._execute_transfer(
                target_org, request_id, donations, transfer_items, transferred_by
            )
            
            if success:
                logger.info(
                    "Donation transfer completed successfully",
                    target_org=target_org,
                    request_id=request_id
                )
                return True, "Transferencia completada exitosamente"
            else:
                return False, error_msg
            
        except Exception as e:
            logger.error(
                "Error in donation transfer",
                error=str(e),
                error_type=type(e).__name__,
                target_org=target_org,
                request_id=request_id
            )
            return False, f"Error interno: {str(e)}"
    
    def _validate_and_prepare_transfer(
        self, donations: List[Dict[str, Any]]
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        """
        Validate donation transfer data and prepare transfer items
        
        Args:
            donations: List of donation items with donation_id and quantity
            
        Returns:
            Tuple[Optional[List], Optional[str]]: (transfer_items, error_message)
        """
        try:
            transfer_items = []
            
            for donation in donations:
                # Validate required fields
                if 'donation_id' not in donation or 'quantity' not in donation:
                    return None, "Cada donación debe tener donation_id y quantity"
                
                # Validate quantity is positive
                try:
                    quantity = int(donation['quantity'])
                    if quantity <= 0:
                        return None, f"La cantidad debe ser positiva: {quantity}"
                except (ValueError, TypeError):
                    return None, f"Cantidad inválida: {donation['quantity']}"
                
                # Get donation details from database
                donation_details = self._get_donation_details(donation['donation_id'])
                if not donation_details:
                    return None, f"Donación no encontrada: {donation['donation_id']}"
                
                # Prepare transfer item
                transfer_item = {
                    'category': donation_details['categoria'],
                    'description': donation_details['descripcion'],
                    'quantity': f"{quantity} unidades"
                }
                transfer_items.append(transfer_item)
            
            return transfer_items, None
            
        except Exception as e:
            logger.error("Error validating transfer data", error=str(e))
            return None, f"Error validando datos: {str(e)}"
    
    def _check_inventory_availability(
        self, donations: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if all donations have sufficient inventory
        
        Args:
            donations: List of donation items with donation_id and quantity
            
        Returns:
            Tuple[bool, Optional[str]]: (available, error_message)
        """
        try:
            conn = self.db_manager.get_connection()
            if not conn:
                return False, "Error de conexión a base de datos"
            
            cursor = conn.cursor()
            
            try:
                for donation in donations:
                    donation_id = donation['donation_id']
                    requested_quantity = int(donation['quantity'])
                    
                    # Check current inventory
                    query = """
                        SELECT cantidad, descripcion 
                        FROM donaciones 
                        WHERE id = %s AND eliminado = FALSE
                    """
                    cursor.execute(query, (donation_id,))
                    result = cursor.fetchone()
                    
                    if not result:
                        return False, f"Donación no encontrada: {donation_id}"
                    
                    current_quantity, description = result
                    
                    if current_quantity < requested_quantity:
                        return False, (
                            f"Inventario insuficiente para '{description}': "
                            f"disponible {current_quantity}, solicitado {requested_quantity}"
                        )
                
                return True, None
                
            finally:
                cursor.close()
                conn.close()
            
        except Exception as e:
            logger.error("Error checking inventory availability", error=str(e))
            return False, f"Error verificando inventario: {str(e)}"
    
    def _get_donation_details(self, donation_id: int) -> Optional[Dict[str, Any]]:
        """Get donation details from database"""
        try:
            conn = self.db_manager.get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor()
            
            try:
                query = """
                    SELECT categoria, descripcion, cantidad 
                    FROM donaciones 
                    WHERE id = %s AND eliminado = FALSE
                """
                cursor.execute(query, (donation_id,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        'categoria': result[0],
                        'descripcion': result[1],
                        'cantidad': result[2]
                    }
                return None
                
            finally:
                cursor.close()
                conn.close()
            
        except Exception as e:
            logger.error("Error getting donation details", error=str(e))
            return None
    
    def _execute_transfer(
        self,
        target_org: str,
        request_id: str,
        donations: List[Dict[str, Any]],
        transfer_items: List[Dict[str, Any]],
        transferred_by: int
    ) -> Tuple[bool, str]:
        """
        Execute the transfer by reducing inventory and publishing message
        
        Args:
            target_org: Target organization ID
            request_id: Original request ID
            donations: Original donation items with IDs
            transfer_items: Prepared transfer items for message
            transferred_by: User performing transfer
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        try:
            conn = self.db_manager.get_connection()
            if not conn:
                return False, "Error de conexión a base de datos"
            
            cursor = conn.cursor()
            
            try:
                # Start transaction
                conn.autocommit = False
                
                # Reduce inventory quantities
                for donation in donations:
                    donation_id = donation['donation_id']
                    quantity_to_transfer = int(donation['quantity'])
                    
                    # Update donation quantity
                    update_query = """
                        UPDATE donaciones 
                        SET cantidad = cantidad - %s,
                            fecha_modificacion = CURRENT_TIMESTAMP,
                            usuario_modificacion = %s
                        WHERE id = %s AND eliminado = FALSE
                    """
                    cursor.execute(update_query, (quantity_to_transfer, transferred_by, donation_id))
                    
                    if cursor.rowcount == 0:
                        raise Exception(f"No se pudo actualizar la donación {donation_id}")
                
                # Record transfer history
                self._record_outgoing_transfer_history(
                    cursor, target_org, request_id, transfer_items, transferred_by
                )
                
                # Commit database changes
                conn.commit()
                
                # Publish transfer message to Kafka
                publish_success = self.producer.publish_transfer(
                    target_org, request_id, transfer_items
                )
                
                if not publish_success:
                    logger.error("Failed to publish transfer message, but inventory was updated")
                    return False, "Error publicando mensaje de transferencia"
                
                logger.info("Transfer executed successfully")
                return True, "Transferencia ejecutada exitosamente"
                
            except Exception as e:
                conn.rollback()
                logger.error("Error executing transfer, rolled back", error=str(e))
                return False, f"Error ejecutando transferencia: {str(e)}"
            
        except Exception as e:
            logger.error("Error in transfer execution", error=str(e))
            return False, f"Error en ejecución: {str(e)}"
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()
    
    def _record_outgoing_transfer_history(
        self,
        cursor,
        target_org: str,
        request_id: str,
        transfer_items: List[Dict[str, Any]],
        transferred_by: int
    ):
        """Record outgoing transfer in history table"""
        try:
            query = """
                INSERT INTO transferencias_donaciones 
                (tipo, organizacion_contraparte, solicitud_id, donaciones, usuario_registro, notas)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            notas = f"Transferencia enviada a {target_org}"
            
            cursor.execute(query, (
                'ENVIADA',
                target_org,
                request_id,
                json.dumps(transfer_items),
                transferred_by,
                notas
            ))
            
        except Exception as e:
            logger.error("Error recording outgoing transfer history", error=str(e))
            raise
    
    def get_transfer_history(
        self, 
        organization_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get transfer history
        
        Args:
            organization_id: Filter by organization (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of transfer records
        """
        try:
            conn = self.db_manager.get_connection()
            if not conn:
                return []
            
            cursor = conn.cursor()
            
            try:
                query = """
                    SELECT id, tipo, organizacion_contraparte, solicitud_id, 
                           donaciones, estado, fecha_transferencia, notas
                    FROM transferencias_donaciones
                """
                params = []
                
                if organization_id:
                    query += " WHERE organizacion_contraparte = %s"
                    params.append(organization_id)
                
                query += " ORDER BY fecha_transferencia DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, tuple(params))
                results = cursor.fetchall()
                
                transfers = []
                for row in results:
                    transfer = {
                        'id': row[0],
                        'tipo': row[1],
                        'organizacion_contraparte': row[2],
                        'solicitud_id': row[3],
                        'donaciones': json.loads(row[4]) if row[4] else [],
                        'estado': row[5],
                        'fecha_transferencia': row[6].isoformat() if row[6] else None,
                        'notas': row[7]
                    }
                    transfers.append(transfer)
                
                return transfers
                
            finally:
                cursor.close()
                conn.close()
            
        except Exception as e:
            logger.error("Error getting transfer history", error=str(e))
            return []