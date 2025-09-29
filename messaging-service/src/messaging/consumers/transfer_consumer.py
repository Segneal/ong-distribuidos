"""
Donation Transfer Consumer for ONG Network Messaging System
Handles processing incoming donation transfer messages
"""
import json
from datetime import datetime
from typing import Dict, Any, List
import structlog

from .base_consumer import BaseConsumer
from ..models.transfer import DonationTransfer, DonationTransferItem
from ..database.manager import DatabaseManager
from ..config import Topics, settings

logger = structlog.get_logger(__name__)


class DonationTransferConsumer(BaseConsumer):
    """Consumer for donation transfer messages directed to our organization"""
    
    def __init__(self):
        # Subscribe to our organization's transfer topic
        topics = [Topics.get_transfer_topic(settings.organization_id)]
        super().__init__(topics)
        self.db_manager = DatabaseManager()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup message handlers for transfer messages"""
        self.register_message_handler("donation_transfer", self._handle_donation_transfer)
    
    def _handle_donation_transfer(self, message_data: Dict[str, Any]):
        """
        Handle incoming donation transfer message
        
        Args:
            message_data: Transfer message data
        """
        try:
            logger.info("Processing incoming donation transfer", data=message_data)
            
            # Parse transfer message
            transfer = DonationTransfer.from_dict(message_data)
            
            # Validate transfer
            if not self._validate_transfer(transfer):
                logger.error("Invalid transfer message", transfer=transfer.to_dict())
                return
            
            # Process transfer - add to inventory and record history
            success = self._process_incoming_transfer(transfer)
            
            if success:
                logger.info(
                    "Donation transfer processed successfully",
                    request_id=transfer.request_id,
                    donor_org=transfer.donor_organization,
                    donations_count=len(transfer.donations)
                )
            else:
                logger.error(
                    "Failed to process donation transfer",
                    request_id=transfer.request_id,
                    donor_org=transfer.donor_organization
                )
            
        except Exception as e:
            logger.error(
                "Error handling donation transfer",
                error=str(e),
                error_type=type(e).__name__,
                message_data=message_data
            )
    
    def _validate_transfer(self, transfer: DonationTransfer) -> bool:
        """
        Validate incoming transfer message
        
        Args:
            transfer: Transfer object to validate
            
        Returns:
            bool: True if transfer is valid
        """
        try:
            # Check required fields
            if not transfer.request_id or not transfer.donor_organization or not transfer.donations:
                logger.error("Missing required transfer fields")
                return False
            
            # Don't process transfers from our own organization
            if transfer.donor_organization == settings.organization_id:
                logger.debug("Skipping transfer from own organization")
                return False
            
            # Validate donation items
            for donation in transfer.donations:
                if not donation.category or not donation.description or not donation.quantity:
                    logger.error("Invalid donation item in transfer", donation=donation.to_dict())
                    return False
                
                # Validate quantity is positive
                try:
                    quantity_num = float(donation.quantity.split()[0]) if ' ' in donation.quantity else float(donation.quantity)
                    if quantity_num <= 0:
                        logger.error("Invalid quantity in donation", quantity=donation.quantity)
                        return False
                except (ValueError, IndexError):
                    logger.error("Cannot parse quantity", quantity=donation.quantity)
                    return False
            
            return True
            
        except Exception as e:
            logger.error("Error validating transfer", error=str(e))
            return False
    
    def _process_incoming_transfer(self, transfer: DonationTransfer) -> bool:
        """
        Process incoming transfer by adding to inventory and recording history
        
        Args:
            transfer: Transfer object to process
            
        Returns:
            bool: True if processing was successful
        """
        try:
            conn = self.db_manager.get_connection()
            if not conn:
                logger.error("Failed to get database connection")
                return False
            
            cursor = conn.cursor()
            
            try:
                # Start transaction
                conn.autocommit = False
                
                # Add donations to inventory
                for donation_item in transfer.donations:
                    # Check if similar donation already exists
                    existing_donation = self._find_existing_donation(
                        cursor, donation_item.category, donation_item.description
                    )
                    
                    if existing_donation:
                        # Update existing donation quantity
                        self._update_donation_quantity(
                            cursor, existing_donation['id'], donation_item.quantity
                        )
                        logger.info(
                            "Updated existing donation",
                            donation_id=existing_donation['id'],
                            category=donation_item.category,
                            description=donation_item.description,
                            added_quantity=donation_item.quantity
                        )
                    else:
                        # Create new donation
                        new_donation_id = self._create_new_donation(
                            cursor, donation_item
                        )
                        logger.info(
                            "Created new donation from transfer",
                            donation_id=new_donation_id,
                            category=donation_item.category,
                            description=donation_item.description,
                            quantity=donation_item.quantity
                        )
                
                # Record transfer history
                self._record_transfer_history(cursor, transfer, 'RECIBIDA')
                
                # Commit transaction
                conn.commit()
                logger.info("Transfer processing committed successfully")
                return True
                
            except Exception as e:
                conn.rollback()
                logger.error("Error processing transfer, rolled back", error=str(e))
                return False
            
        except Exception as e:
            logger.error("Error in transfer processing", error=str(e))
            return False
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()
    
    def _find_existing_donation(self, cursor, category: str, description: str) -> Dict[str, Any]:
        """Find existing donation with same category and description"""
        try:
            query = """
                SELECT id, cantidad 
                FROM donaciones 
                WHERE categoria = %s AND descripcion = %s AND eliminado = FALSE
                LIMIT 1
            """
            cursor.execute(query, (category, description))
            result = cursor.fetchone()
            
            if result:
                return {'id': result[0], 'cantidad': result[1]}
            return None
            
        except Exception as e:
            logger.error("Error finding existing donation", error=str(e))
            return None
    
    def _update_donation_quantity(self, cursor, donation_id: int, quantity_to_add: str):
        """Update existing donation quantity"""
        try:
            # Parse quantity to add
            quantity_num = self._parse_quantity(quantity_to_add)
            
            query = """
                UPDATE donaciones 
                SET cantidad = cantidad + %s, 
                    fecha_modificacion = CURRENT_TIMESTAMP,
                    usuario_modificacion = 1
                WHERE id = %s
            """
            cursor.execute(query, (quantity_num, donation_id))
            
        except Exception as e:
            logger.error("Error updating donation quantity", error=str(e))
            raise
    
    def _create_new_donation(self, cursor, donation_item: DonationTransferItem) -> int:
        """Create new donation from transfer item"""
        try:
            # Parse quantity
            quantity_num = self._parse_quantity(donation_item.quantity)
            
            query = """
                INSERT INTO donaciones (categoria, descripcion, cantidad, usuario_alta)
                VALUES (%s, %s, %s, 1)
                RETURNING id
            """
            cursor.execute(query, (
                donation_item.category,
                donation_item.description,
                quantity_num
            ))
            
            result = cursor.fetchone()
            return result[0] if result else None
            
        except Exception as e:
            logger.error("Error creating new donation", error=str(e))
            raise
    
    def _parse_quantity(self, quantity_str: str) -> int:
        """Parse quantity string to integer"""
        try:
            # Handle quantities like "5 kg", "10 unidades", etc.
            if ' ' in quantity_str:
                return int(float(quantity_str.split()[0]))
            else:
                return int(float(quantity_str))
        except (ValueError, IndexError):
            logger.warning("Could not parse quantity, using 1", quantity=quantity_str)
            return 1
    
    def _record_transfer_history(self, cursor, transfer: DonationTransfer, tipo: str):
        """Record transfer in history table"""
        try:
            # Prepare donations data for JSON storage
            donations_data = [item.to_dict() for item in transfer.donations]
            
            query = """
                INSERT INTO transferencias_donaciones 
                (tipo, organizacion_contraparte, solicitud_id, donaciones, usuario_registro, notas)
                VALUES (%s, %s, %s, %s, 1, %s)
            """
            
            notas = f"Transferencia {tipo.lower()} procesada automáticamente"
            
            cursor.execute(query, (
                tipo,
                transfer.donor_organization,
                transfer.request_id,
                json.dumps(donations_data),
                notas
            ))
            
        except Exception as e:
            logger.error("Error recording transfer history", error=str(e))
            raise
    
    def process_message(self, message_envelope: Dict[str, Any]):
        """Process message envelope (for compatibility with existing code)"""
        try:
            if not self._validate_message_envelope(message_envelope):
                return
            
            if not self._should_process_message(message_envelope):
                return
            
            message_data = message_envelope.get('data', {})
            self._handle_donation_transfer(message_data)
            
        except Exception as e:
            logger.error("Error processing message envelope", error=str(e))