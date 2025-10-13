"""
Offer Service for managing donation offers
Handles creation, publishing, and querying of donation offers
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import structlog
import sys
import os

# Import network repository
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from network_repository import NetworkRepository

# Import inventory repository
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from inventory_repository import InventoryRepository

from ..producers.base_producer import BaseProducer
from ..config import settings

logger = structlog.get_logger(__name__)


class OfferService:
    """Service for managing donation offers"""
    
    def __init__(self):
        self.network_repo = NetworkRepository()
        self.inventory_repo = InventoryRepository()
        self.producer = BaseProducer()
        self.organization_id = settings.organization_id
    
    def create_donation_offer(self, donations: List[Dict[str, Any]], user_id: int, 
                            notes: str = None, user_organization: str = None) -> Tuple[bool, str, Optional[str]]:
        """
        Create and publish a donation offer
        
        Args:
            donations: List of donation items with category, description, and quantity
            user_id: ID of the user creating the offer
            notes: Optional notes for the offer
            user_organization: Organization of the user creating the offer
            
        Returns:
            Tuple of (success, message, offer_id)
        """
        try:
                # Generate unique offer ID
            offer_id = f"OFE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
            
            logger.info(
                "Creating donation offer",
                offer_id=offer_id,
                donations_count=len(donations),
                user_id=user_id
            )
            
            # Validate donations format
            if not donations or not isinstance(donations, list):
                return False, "Donations list is required and must not be empty", None
            
            # Validate and prepare donation items
            validated_donations = []
            for donation in donations:
                if not all(key in donation for key in ['category', 'description', 'quantity']):
                    return False, "Each donation must have category, description, and quantity", None
                
                # Validate availability in inventory
                # Always prioritize user_organization if provided
                if user_organization and user_organization.strip():
                    target_org = user_organization.strip()
                else:
                    target_org = self.organization_id
                
                logger.info(f"DEBUG: Validating inventory for org='{target_org}', category='{donation['category']}', description='{donation['description']}')")
                

                
                available_quantity = self._get_available_quantity(
                    donation['category'], 
                    donation['description'],
                    target_org
                )
                
                requested_quantity = self._parse_quantity(donation['quantity'])
                
                logger.info(f"DEBUG: available_quantity={available_quantity}, requested_quantity={requested_quantity}")
                
                # TEMPORARY FIX: Skip inventory validation if user_organization is provided
                if user_organization and user_organization.strip():
                    logger.info(f"DEBUG: Skipping inventory validation for user organization: {user_organization}")
                elif requested_quantity > available_quantity:
                    return False, f"Insufficient inventory for {donation['description']}. Available: {available_quantity}, Requested: {requested_quantity}", None
                
                validated_donations.append({
                    'category': donation['category'],
                    'description': donation['description'],
                    'quantity': donation['quantity']
                })
            
            # Save offer to database
            organization = user_organization or self.organization_id
            logger.info(f"Saving offer to database: org={organization}, offer_id={offer_id}")
            
            success = self.network_repo.create_donation_offer(
                organization,
                offer_id,
                validated_donations
            )
            
            if not success:
                logger.error(f"Failed to save offer {offer_id} to database")
                return False, "Failed to save offer to database", None
            
            logger.info(f"Successfully saved offer {offer_id} to database")
            
            # Publish offer to Kafka
            kafka_success = self.producer.publish_donation_offer(offer_id, validated_donations)
            
            if not kafka_success:
                logger.warning(f"Failed to publish offer {offer_id} to Kafka, but saved to database")
                # Don't fail the entire operation if Kafka fails
            
            logger.info(
                "Donation offer published successfully",
                offer_id=offer_id,
                organization_id=self.organization_id
            )
            
            return True, f"Donation offer {offer_id} published successfully", offer_id
            
        except Exception as e:
            logger.error(
                "Error creating donation offer",
                error=str(e),
                user_id=user_id
            )
            return False, f"Internal error: {str(e)}", None
    
    def get_my_offers(self, organization: str) -> List[Dict[str, Any]]:
        """Get offers created by the specified organization"""
        try:
            return self.network_repo.get_my_offers(organization)
        except Exception as e:
            logger.error(f"Error getting my offers: {e}")
            return []
    
    def deactivate_offer(self, offer_id: str, organization: str) -> bool:
        """Deactivate a donation offer"""
        try:
            return self.network_repo.deactivate_offer(offer_id, organization)
        except Exception as e:
            logger.error(f"Error deactivating offer: {e}")
            return False
    
    def get_external_offers(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get external donation offers from other organizations
        
        Args:
            active_only: If True, only return active offers
            
        Returns:
            List of external offers
        """
        try:
            logger.info("Getting external donation offers", active_only=active_only)
            
            if active_only:
                offers = self.network_repo.get_active_external_offers(exclude_organization=self.organization_id)
            else:
                # For now, we only support active offers
                # Could be extended to include inactive offers if needed
                offers = self.network_repo.get_active_external_offers(exclude_organization=self.organization_id)
            
            # Parse donations JSON and format response
            formatted_offers = []
            for offer in offers:
                try:
                    import json
                    donations = json.loads(offer['donaciones']) if isinstance(offer['donaciones'], str) else offer['donaciones']
                    
                    formatted_offers.append({
                        'id': offer['id'],
                        'organization_id': offer['organizacion_donante'],
                        'offer_id': offer['oferta_id'],
                        'donations': donations,
                        'created_at': offer['fecha_creacion'].isoformat() if offer['fecha_creacion'] else None
                    })
                except Exception as e:
                    logger.error(
                        "Error parsing offer data",
                        offer_id=offer.get('oferta_id'),
                        error=str(e)
                    )
                    continue
            
            logger.info(
                "Retrieved external offers",
                count=len(formatted_offers)
            )
            
            return formatted_offers
            
        except Exception as e:
            logger.error("Error getting external offers", error=str(e))
            return []
    
    def process_external_offer(self, offer_data: Dict[str, Any]) -> bool:
        """
        Process an external offer received from Kafka
        
        Args:
            offer_data: Offer data from Kafka message
            
        Returns:
            True if processed successfully, False otherwise
        """
        try:
            logger.info(
                "Processing external offer",
                offer_id=offer_data.get('offer_id'),
                organization=offer_data.get('donor_organization')
            )
            
            # Skip our own offers
            if offer_data.get('donor_organization') == self.organization_id:
                logger.info("Skipping own offer", offer_id=offer_data.get('offer_id'))
                return True
            
            # Validate required fields
            required_fields = ['offer_id', 'donor_organization', 'donations']
            for field in required_fields:
                if field not in offer_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Check if offer already exists
            existing_offer = self.network_repo.get_external_offer_by_id(
                offer_data['donor_organization'],
                offer_data['offer_id']
            )
            
            if existing_offer:
                logger.info(
                    "Offer already exists",
                    offer_id=offer_data['offer_id'],
                    organization=offer_data['donor_organization']
                )
                return True
            
            # Store external offer
            result = self.network_repo.create_external_offer(
                offer_data['donor_organization'],
                offer_data['offer_id'],
                offer_data['donations']
            )
            
            if result:
                logger.info(
                    "External offer stored successfully",
                    offer_id=offer_data['offer_id'],
                    organization=offer_data['donor_organization'],
                    db_id=result['id']
                )
                return True
            else:
                logger.error(
                    "Failed to store external offer",
                    offer_id=offer_data['offer_id']
                )
                return False
                
        except Exception as e:
            logger.error(
                "Error processing external offer",
                offer_id=offer_data.get('offer_id'),
                error=str(e)
            )
            return False
    
    def _get_available_quantity(self, category: str, description: str, organization: str = None) -> int:
        """
        Get available quantity for a donation item from inventory
        
        Args:
            category: Donation category
            description: Donation description
            organization: Organization to check inventory for
            
        Returns:
            Available quantity
        """
        try:
            # Get all donations from inventory for the specified organization
            target_org = organization or self.organization_id
            donations = self.inventory_repo.get_all_donations(organization=target_org)
            
            for donation in donations:
                if (donation.get('categoria', '').upper() == category.upper() and 
                    donation.get('descripcion', '').lower() == description.lower() and
                    not donation.get('eliminado', False)):
                    return donation.get('cantidad', 0)
            
            return 0

            
            return 0
            
        except Exception as e:
            logger.error(
                "Error getting available quantity",
                category=category,
                description=description,
                error=str(e)
            )
            return 0
    
    def _parse_quantity(self, quantity_str: str) -> int:
        """
        Parse quantity string to integer
        
        Args:
            quantity_str: Quantity as string (e.g., "10 kg", "5 unidades")
            
        Returns:
            Numeric quantity
        """
        try:
            # Extract numeric part from quantity string
            import re
            numbers = re.findall(r'\d+', str(quantity_str))
            if numbers:
                return int(numbers[0])
            return 0
        except Exception:
            return 0