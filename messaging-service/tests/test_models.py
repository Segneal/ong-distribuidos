"""
Unit tests for messaging models
"""
import pytest
from datetime import datetime
from typing import Dict, Any

from messaging.models.donation import (
    DonationItem, DonationRequest, DonationOffer, DonationOfferItem, 
    RequestCancellation, DonationCategory
)
from messaging.models.event import ExternalEvent, EventCancellation, EventAdhesion, VolunteerInfo


class TestDonationCategory:
    """Test cases for DonationCategory enum"""
    
    def test_donation_categories(self):
        """Test donation category enum values"""
        assert DonationCategory.ROPA.value == "ROPA"
        assert DonationCategory.ALIMENTOS.value == "ALIMENTOS"
        assert DonationCategory.JUGUETES.value == "JUGUETES"
        assert DonationCategory.UTILES_ESCOLARES.value == "UTILES_ESCOLARES"


class TestDonationItem:
    """Test cases for DonationItem model"""
    
    def test_init(self):
        """Test DonationItem initialization"""
        item = DonationItem(
            category="ALIMENTOS",
            description="Puré de tomates"
        )
        
        assert item.category == "ALIMENTOS"
        assert item.description == "Puré de tomates"
    
    def test_to_dict(self):
        """Test DonationItem to_dict method"""
        item = DonationItem(
            category="ALIMENTOS",
            description="Puré de tomates"
        )
        
        result = item.to_dict()
        
        expected = {
            'category': 'ALIMENTOS',
            'description': 'Puré de tomates'
        }
        
        assert result == expected
    
    def test_from_dict(self):
        """Test DonationItem from_dict method"""
        data = {
            'category': 'ROPA',
            'description': 'Camisetas talla M'
        }
        
        item = DonationItem.from_dict(data)
        
        assert item.category == 'ROPA'
        assert item.description == 'Camisetas talla M'
    
    def test_from_dict_missing_field(self):
        """Test DonationItem from_dict with missing field"""
        data = {
            'category': 'ROPA'
            # Missing description
        }
        
        with pytest.raises(KeyError):
            DonationItem.from_dict(data)


class TestDonationRequest:
    """Test cases for DonationRequest model"""
    
    def test_init(self):
        """Test DonationRequest initialization"""
        donations = [
            DonationItem("ALIMENTOS", "Puré de tomates"),
            DonationItem("ROPA", "Camisetas")
        ]
        
        request = DonationRequest(
            organization_id="test-org",
            request_id="REQ-001",
            donations=donations,
            timestamp="2024-01-15T10:30:00Z"
        )
        
        assert request.organization_id == "test-org"
        assert request.request_id == "REQ-001"
        assert len(request.donations) == 2
        assert request.timestamp == "2024-01-15T10:30:00Z"
    
    def test_to_dict(self):
        """Test DonationRequest to_dict method"""
        donations = [
            DonationItem("ALIMENTOS", "Puré de tomates")
        ]
        
        request = DonationRequest(
            organization_id="test-org",
            request_id="REQ-001",
            donations=donations,
            timestamp="2024-01-15T10:30:00Z"
        )
        
        result = request.to_dict()
        
        expected = {
            'organization_id': 'test-org',
            'request_id': 'REQ-001',
            'donations': [
                {
                    'category': 'ALIMENTOS',
                    'description': 'Puré de tomates'
                }
            ],
            'timestamp': '2024-01-15T10:30:00Z'
        }
        
        assert result == expected
    
    def test_from_dict(self):
        """Test DonationRequest from_dict method"""
        data = {
            'organization_id': 'test-org',
            'request_id': 'REQ-001',
            'donations': [
                {
                    'category': 'ALIMENTOS',
                    'description': 'Puré de tomates'
                },
                {
                    'category': 'ROPA',
                    'description': 'Camisetas'
                }
            ],
            'timestamp': '2024-01-15T10:30:00Z'
        }
        
        request = DonationRequest.from_dict(data)
        
        assert request.organization_id == 'test-org'
        assert request.request_id == 'REQ-001'
        assert len(request.donations) == 2
        assert request.donations[0].category == 'ALIMENTOS'
        assert request.donations[1].category == 'ROPA'
        assert request.timestamp == '2024-01-15T10:30:00Z'


class TestDonationOfferItem:
    """Test cases for DonationOfferItem model"""
    
    def test_init(self):
        """Test DonationOfferItem initialization"""
        item = DonationOfferItem(
            category="ALIMENTOS",
            description="Puré de tomates",
            quantity="2kg"
        )
        
        assert item.category == "ALIMENTOS"
        assert item.description == "Puré de tomates"
        assert item.quantity == "2kg"
    
    def test_to_dict(self):
        """Test DonationOfferItem to_dict method"""
        item = DonationOfferItem(
            category="ALIMENTOS",
            description="Puré de tomates",
            quantity="2kg"
        )
        
        result = item.to_dict()
        
        expected = {
            'category': 'ALIMENTOS',
            'description': 'Puré de tomates',
            'quantity': '2kg'
        }
        
        assert result == expected
    
    def test_from_dict(self):
        """Test DonationOfferItem from_dict method"""
        data = {
            'category': 'ROPA',
            'description': 'Camisetas talla M',
            'quantity': '10 unidades'
        }
        
        item = DonationOfferItem.from_dict(data)
        
        assert item.category == 'ROPA'
        assert item.description == 'Camisetas talla M'
        assert item.quantity == '10 unidades'


class TestDonationOffer:
    """Test cases for DonationOffer model"""
    
    def test_init(self):
        """Test DonationOffer initialization"""
        donations = [
            DonationOfferItem("ALIMENTOS", "Puré de tomates", "2kg")
        ]
        
        offer = DonationOffer(
            offer_id="OFFER-001",
            donor_organization="test-org",
            donations=donations,
            timestamp="2024-01-15T11:00:00Z"
        )
        
        assert offer.offer_id == "OFFER-001"
        assert offer.donor_organization == "test-org"
        assert len(offer.donations) == 1
        assert offer.timestamp == "2024-01-15T11:00:00Z"
    
    def test_to_dict(self):
        """Test DonationOffer to_dict method"""
        donations = [
            DonationOfferItem("ALIMENTOS", "Puré de tomates", "2kg")
        ]
        
        offer = DonationOffer(
            offer_id="OFFER-001",
            donor_organization="test-org",
            donations=donations,
            timestamp="2024-01-15T11:00:00Z"
        )
        
        result = offer.to_dict()
        
        expected = {
            'offer_id': 'OFFER-001',
            'donor_organization': 'test-org',
            'donations': [
                {
                    'category': 'ALIMENTOS',
                    'description': 'Puré de tomates',
                    'quantity': '2kg'
                }
            ],
            'timestamp': '2024-01-15T11:00:00Z'
        }
        
        assert result == expected
    
    def test_from_dict(self):
        """Test DonationOffer from_dict method"""
        data = {
            'offer_id': 'OFFER-001',
            'donor_organization': 'test-org',
            'donations': [
                {
                    'category': 'ALIMENTOS',
                    'description': 'Puré de tomates',
                    'quantity': '2kg'
                }
            ],
            'timestamp': '2024-01-15T11:00:00Z'
        }
        
        offer = DonationOffer.from_dict(data)
        
        assert offer.offer_id == 'OFFER-001'
        assert offer.donor_organization == 'test-org'
        assert len(offer.donations) == 1
        assert offer.donations[0].quantity == '2kg'
        assert offer.timestamp == '2024-01-15T11:00:00Z'


class TestRequestCancellation:
    """Test cases for RequestCancellation model"""
    
    def test_init(self):
        """Test RequestCancellation initialization"""
        cancellation = RequestCancellation(
            organization_id="test-org",
            request_id="REQ-001",
            timestamp="2024-01-15T12:00:00Z"
        )
        
        assert cancellation.organization_id == "test-org"
        assert cancellation.request_id == "REQ-001"
        assert cancellation.timestamp == "2024-01-15T12:00:00Z"
    
    def test_to_dict(self):
        """Test RequestCancellation to_dict method"""
        cancellation = RequestCancellation(
            organization_id="test-org",
            request_id="REQ-001",
            timestamp="2024-01-15T12:00:00Z"
        )
        
        result = cancellation.to_dict()
        
        expected = {
            'organization_id': 'test-org',
            'request_id': 'REQ-001',
            'timestamp': '2024-01-15T12:00:00Z'
        }
        
        assert result == expected
    
    def test_from_dict(self):
        """Test RequestCancellation from_dict method"""
        data = {
            'organization_id': 'test-org',
            'request_id': 'REQ-001',
            'timestamp': '2024-01-15T12:00:00Z'
        }
        
        cancellation = RequestCancellation.from_dict(data)
        
        assert cancellation.organization_id == 'test-org'
        assert cancellation.request_id == 'REQ-001'
        assert cancellation.timestamp == '2024-01-15T12:00:00Z'


class TestVolunteerInfo:
    """Test cases for VolunteerInfo model"""
    
    def test_volunteer_info_creation(self):
        """Test VolunteerInfo model creation"""
        volunteer = VolunteerInfo(
            organization_id="test-org",
            volunteer_id=1,
            name="Juan",
            last_name="Pérez",
            phone="+1234567890",
            email="juan.perez@example.com"
        )
        
        assert volunteer.organization_id == "test-org"
        assert volunteer.volunteer_id == 1
        assert volunteer.name == "Juan"
        assert volunteer.last_name == "Pérez"
        assert volunteer.phone == "+1234567890"
        assert volunteer.email == "juan.perez@example.com"


class TestExternalEvent:
    """Test cases for ExternalEvent model"""
    
    def test_external_event_creation(self):
        """Test ExternalEvent model creation"""
        event = ExternalEvent(
            organization_id="test-org",
            event_id="EVENT-001",
            name="Campaña de Donación",
            description="Recolección de alimentos",
            event_date="2024-02-15T09:00:00Z",
            timestamp="2024-01-15T12:00:00Z"
        )
        
        assert event.organization_id == "test-org"
        assert event.event_id == "EVENT-001"
        assert event.name == "Campaña de Donación"
        assert event.description == "Recolección de alimentos"
        assert event.event_date == "2024-02-15T09:00:00Z"
        assert event.timestamp == "2024-01-15T12:00:00Z"


class TestEventCancellation:
    """Test cases for EventCancellation model"""
    
    def test_event_cancellation_creation(self):
        """Test EventCancellation model creation"""
        cancellation = EventCancellation(
            organization_id="test-org",
            event_id="EVENT-001",
            timestamp="2024-01-15T12:00:00Z"
        )
        
        assert cancellation.organization_id == "test-org"
        assert cancellation.event_id == "EVENT-001"
        assert cancellation.timestamp == "2024-01-15T12:00:00Z"


class TestEventAdhesion:
    """Test cases for EventAdhesion model"""
    
    def test_event_adhesion_creation(self):
        """Test EventAdhesion model creation"""
        volunteer_info = VolunteerInfo(
            organization_id="test-org",
            volunteer_id=1,
            name="Juan",
            last_name="Pérez",
            phone="+1234567890",
            email="juan.perez@example.com"
        )
        
        adhesion = EventAdhesion(
            event_id="EVENT-001",
            volunteer=volunteer_info,
            timestamp="2024-01-15T12:00:00Z"
        )
        
        assert adhesion.event_id == "EVENT-001"
        assert adhesion.volunteer == volunteer_info
        assert adhesion.timestamp == "2024-01-15T12:00:00Z"





class TestModelValidation:
    """Test cases for model validation"""
    
    def test_donation_item_empty_fields(self):
        """Test DonationItem with empty fields"""
        # Test with empty category
        item = DonationItem("", "Description")
        assert item.category == ""
        assert item.description == "Description"
        
        # Test with empty description
        item = DonationItem("ALIMENTOS", "")
        assert item.category == "ALIMENTOS"
        assert item.description == ""
    
    def test_donation_request_empty_donations(self):
        """Test DonationRequest with empty donations list"""
        request = DonationRequest(
            organization_id="test-org",
            request_id="REQ-001",
            donations=[],
            timestamp="2024-01-15T10:30:00Z"
        )
        
        assert len(request.donations) == 0
    
    def test_model_serialization_roundtrip(self):
        """Test model serialization and deserialization roundtrip"""
        # Test DonationItem
        original_item = DonationItem("ALIMENTOS", "Puré de tomates")
        item_dict = original_item.to_dict()
        restored_item = DonationItem.from_dict(item_dict)
        
        assert original_item.category == restored_item.category
        assert original_item.description == restored_item.description
        
        # Test DonationRequest
        original_request = DonationRequest(
            organization_id="test-org",
            request_id="REQ-001",
            donations=[original_item],
            timestamp="2024-01-15T10:30:00Z"
        )
        
        request_dict = original_request.to_dict()
        restored_request = DonationRequest.from_dict(request_dict)
        
        assert original_request.organization_id == restored_request.organization_id
        assert original_request.request_id == restored_request.request_id
        assert len(original_request.donations) == len(restored_request.donations)
        assert original_request.timestamp == restored_request.timestamp