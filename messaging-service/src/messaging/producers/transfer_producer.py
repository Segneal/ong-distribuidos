"""
Donation Transfer Producer for ONG Network Messaging System
Handles publishing donation transfer messages to target organizations
"""
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import structlog

from .base_producer import BaseProducer
from ..models.transfer import DonationTransfer, DonationTransferItem
from ..config import Topics, settings

logger = structlog.get_logger(__name__)


class DonationTransferProducer(BaseProducer):
    """Producer for donation transfer messages"""
    
    def __init__(self):
        super().__init__()
    
    def publish_transfer(self, target_org: str, request_id: str, donations: List[Dict[str, Any]]) -> bool:
        """
        Publish donation transfer message to target organization
        
        Args:
            target_org: Target organization ID
            request_id: Original request ID being fulfilled
            donations: List of donation items with category, description, and quantity
            
        Returns:
            bool: True if message was published successfully
        """
        try:
            logger.info(
                "Publishing donation transfer",
                target_org=target_org,
                request_id=request_id,
                donations_count=len(donations)
            )
            
            # Validate inputs
            if not target_org or not request_id or not donations:
                logger.error("Invalid transfer parameters", 
                           target_org=target_org, request_id=request_id, donations=donations)
                return False
            
            # Convert donations to transfer items
            transfer_items = []
            for donation in donations:
                if not all(key in donation for key in ['category', 'description', 'quantity']):
                    logger.error("Invalid donation item format", donation=donation)
                    return False
                
                transfer_item = DonationTransferItem(
                    category=donation['category'],
                    description=donation['description'],
                    quantity=str(donation['quantity'])
                )
                transfer_items.append(transfer_item)
            
            # Create transfer message
            transfer = DonationTransfer(
                request_id=request_id,
                donor_organization=self.organization_id,
                donations=transfer_items,
                timestamp=datetime.utcnow().isoformat()
            )
            
            # Get target topic
            topic = Topics.get_transfer_topic(target_org)
            
            # Publish message
            message = transfer.to_dict()
            message['type'] = 'donation_transfer'
            
            success = self._publish_message(topic, message, key=self.organization_id)
            
            if success:
                logger.info(
                    "Donation transfer published successfully",
                    target_org=target_org,
                    request_id=request_id,
                    topic=topic
                )
            else:
                logger.error(
                    "Failed to publish donation transfer",
                    target_org=target_org,
                    request_id=request_id,
                    topic=topic
                )
            
            return success
            
        except Exception as e:
            logger.error(
                "Error publishing donation transfer",
                error=str(e),
                error_type=type(e).__name__,
                target_org=target_org,
                request_id=request_id
            )
            return False
    
    def validate_transfer_data(self, donations: List[Dict[str, Any]]) -> bool:
        """
        Validate transfer data format
        
        Args:
            donations: List of donation items to validate
            
        Returns:
            bool: True if all items are valid
        """
        try:
            for donation in donations:
                # Check required fields
                required_fields = ['category', 'description', 'quantity']
                if not all(field in donation for field in required_fields):
                    logger.error("Missing required fields in donation", 
                               donation=donation, required_fields=required_fields)
                    return False
                
                # Validate category
                valid_categories = ['ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES']
                if donation['category'] not in valid_categories:
                    logger.error("Invalid donation category", 
                               category=donation['category'], valid_categories=valid_categories)
                    return False
                
                # Validate quantity is positive
                try:
                    quantity = int(donation['quantity']) if isinstance(donation['quantity'], str) else donation['quantity']
                    if quantity <= 0:
                        logger.error("Invalid quantity", quantity=quantity)
                        return False
                except (ValueError, TypeError):
                    logger.error("Invalid quantity format", quantity=donation['quantity'])
                    return False
            
            return True
            
        except Exception as e:
            logger.error("Error validating transfer data", error=str(e))
            return False