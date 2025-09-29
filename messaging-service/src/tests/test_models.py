"""
Tests for messaging models, schemas, and serializers
"""
import json
import pytest
from datetime import datetime
from typing import Dict, Any

from models import (
    DonationItem, DonationTransferItem, DonationOfferItem, VolunteerInfo,
    DonationRequest, DonationTransfer, DonationOffer, RequestCancellation,
    ExternalEvent, EventCancellation, EventAdhesion
)
from schemas import MessageValidator, ValidationError
from serializers import MessageSerializer, KafkaMessageHelper, SerializationError, DeserializationError

class TestModels:
    """Test message model classes"""
    
    def test_donation_item(self):
        """Test DonationItem model"""
        item = DonationItem(category="ALIMENTOS", description="Puré de tomates")
        
        # Test to_dict
        item_dict = item.to_dict()
        assert item_dict == {
            'category': 'ALIMENTOS',
            'description': 'Puré de tomates'
        }
        
        # Test from_dict
        item_from_dict = DonationItem.from_dict(item_dict)
        assert item_from_dict.category == item.category
        assert item_from_dict.description == item.description
    
    def test_donation_transfer_item(self):
        """Test DonationTransferItem model"""
        item = DonationTransferItem(
            category="ALIMENTOS", 
            description="Puré de tomates", 
            quantity="2kg"
        )
        
        # Test to_dict
        item_dict = item.to_dict()
        assert item_dict == {
            'category': 'ALIMENTOS',
            'description': 'Puré de tomates',
            'quantity': '2kg'
        }
        
        # Test from_dict
        item_from_dict = DonationTransferItem.from_dict(item_dict)
        assert item_from_dict.category == item.category
        assert item_from_dict.description == item.description
        assert item_from_dict.quantity == item.quantity
    
    def test_volunteer_info(self):
        """Test VolunteerInfo model"""
        volunteer = VolunteerInfo(
            organization_id="empuje-comunitario",
            volunteer_id=123,
            name="Juan",
            last_name="Pérez",
            phone="555-1234",
            email="juan@example.com"
        )
        
        # Test to_dict
        volunteer_dict = volunteer.to_dict()
        expected = {
            'organization_id': 'empuje-comunitario',
            'volunteer_id': 123,
            'name': 'Juan',
            'last_name': 'Pérez',
            'phone': '555-1234',
            'email': 'juan@example.com'
        }
        assert volunteer_dict == expected
        
        # Test from_dict
        volunteer_from_dict = VolunteerInfo.from_dict(volunteer_dict)
        assert volunteer_from_dict.organization_id == volunteer.organization_id
        assert volunteer_from_dict.volunteer_id == volunteer.volunteer_id
        assert volunteer_from_dict.name == volunteer.name
        assert volunteer_from_dict.last_name == volunteer.last_name
        assert volunteer_from_dict.phone == volunteer.phone
        assert volunteer_from_dict.email == volunteer.email
    
    def test_donation_request(self):
        """Test DonationRequest model"""
        donations = [
            DonationItem(category="ALIMENTOS", description="Puré de tomates"),
            DonationItem(category="ROPA", description="Camisetas")
        ]
        
        request = DonationRequest(
            organization_id="empuje-comunitario",
            request_id="REQ-2024-001",
            donations=donations,
            timestamp="2024-01-15T10:30:00Z"
        )
        
        # Test to_dict
        request_dict = request.to_dict()
        assert request_dict['organization_id'] == 'empuje-comunitario'
        assert request_dict['request_id'] == 'REQ-2024-001'
        assert len(request_dict['donations']) == 2
        assert request_dict['timestamp'] == '2024-01-15T10:30:00Z'
        
        # Test from_dict
        request_from_dict = DonationRequest.from_dict(request_dict)
        assert request_from_dict.organization_id == request.organization_id
        assert request_from_dict.request_id == request.request_id
        assert len(request_from_dict.donations) == len(request.donations)
        assert request_from_dict.timestamp == request.timestamp

class TestSchemas:
    """Test JSON schema validation"""
    
    def test_valid_donation_request(self):
        """Test valid donation request validation"""
        valid_data = {
            "organization_id": "empuje-comunitario",
            "request_id": "REQ-2024-001",
            "donations": [
                {
                    "category": "ALIMENTOS",
                    "description": "Puré de tomates"
                }
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        # Should not raise exception
        assert MessageValidator.validate_message('donation_request', valid_data) == True
    
    def test_invalid_donation_request_missing_field(self):
        """Test invalid donation request - missing required field"""
        invalid_data = {
            "organization_id": "empuje-comunitario",
            # Missing request_id
            "donations": [
                {
                    "category": "ALIMENTOS",
                    "description": "Puré de tomates"
                }
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        with pytest.raises(ValidationError):
            MessageValidator.validate_message('donation_request', invalid_data)
    
    def test_invalid_donation_request_invalid_category(self):
        """Test invalid donation request - invalid category"""
        invalid_data = {
            "organization_id": "empuje-comunitario",
            "request_id": "REQ-2024-001",
            "donations": [
                {
                    "category": "INVALID_CATEGORY",  # Invalid category
                    "description": "Puré de tomates"
                }
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        with pytest.raises(ValidationError):
            MessageValidator.validate_message('donation_request', invalid_data)
    
    def test_valid_event_adhesion(self):
        """Test valid event adhesion validation"""
        valid_data = {
            "event_id": "EVT-2024-001",
            "volunteer": {
                "organization_id": "empuje-comunitario",
                "volunteer_id": 123,
                "name": "Juan",
                "last_name": "Pérez",
                "phone": "555-1234",
                "email": "juan@example.com"
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        # Should not raise exception
        assert MessageValidator.validate_message('event_adhesion', valid_data) == True
    
    def test_invalid_event_adhesion_invalid_email(self):
        """Test invalid event adhesion - invalid email format"""
        invalid_data = {
            "event_id": "EVT-2024-001",
            "volunteer": {
                "organization_id": "empuje-comunitario",
                "volunteer_id": 123,
                "name": "Juan",
                "last_name": "Pérez",
                "phone": "555-1234",
                "email": "invalid-email"  # Invalid email format
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        with pytest.raises(ValidationError):
            MessageValidator.validate_message('event_adhesion', invalid_data)

class TestSerializers:
    """Test message serialization and deserialization"""
    
    def test_serialize_donation_request(self):
        """Test donation request serialization"""
        donations = [DonationItem(category="ALIMENTOS", description="Puré de tomates")]
        request = DonationRequest(
            organization_id="empuje-comunitario",
            request_id="REQ-2024-001",
            donations=donations,
            timestamp="2024-01-15T10:30:00Z"
        )
        
        # Serialize
        serialized = MessageSerializer.serialize_message(request)
        assert isinstance(serialized, bytes)
        
        # Verify JSON structure
        json_data = json.loads(serialized.decode('utf-8'))
        assert json_data['organization_id'] == 'empuje-comunitario'
        assert json_data['request_id'] == 'REQ-2024-001'
        assert len(json_data['donations']) == 1
    
    def test_deserialize_donation_request(self):
        """Test donation request deserialization"""
        json_data = {
            "organization_id": "empuje-comunitario",
            "request_id": "REQ-2024-001",
            "donations": [
                {
                    "category": "ALIMENTOS",
                    "description": "Puré de tomates"
                }
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        json_bytes = json.dumps(json_data).encode('utf-8')
        
        # Deserialize
        request = MessageSerializer.deserialize_message(json_bytes, 'donation_request')
        
        assert isinstance(request, DonationRequest)
        assert request.organization_id == 'empuje-comunitario'
        assert request.request_id == 'REQ-2024-001'
        assert len(request.donations) == 1
        assert request.donations[0].category == 'ALIMENTOS'
    
    def test_serialize_deserialize_roundtrip(self):
        """Test serialization/deserialization roundtrip"""
        # Create original message
        donations = [
            DonationTransferItem(category="ALIMENTOS", description="Puré de tomates", quantity="2kg"),
            DonationTransferItem(category="ROPA", description="Camisetas", quantity="5 unidades")
        ]
        original = DonationTransfer(
            request_id="REQ-2024-001",
            donor_organization="empuje-comunitario",
            donations=donations,
            timestamp="2024-01-15T11:00:00Z"
        )
        
        # Serialize
        serialized = MessageSerializer.serialize_message(original)
        
        # Deserialize
        deserialized = MessageSerializer.deserialize_message(serialized, 'donation_transfer')
        
        # Verify roundtrip
        assert isinstance(deserialized, DonationTransfer)
        assert deserialized.request_id == original.request_id
        assert deserialized.donor_organization == original.donor_organization
        assert len(deserialized.donations) == len(original.donations)
        assert deserialized.donations[0].category == original.donations[0].category
        assert deserialized.donations[0].quantity == original.donations[0].quantity
    
    def test_invalid_serialization(self):
        """Test serialization with invalid data"""
        # Create invalid message (empty donations list)
        request = DonationRequest(
            organization_id="empuje-comunitario",
            request_id="REQ-2024-001",
            donations=[],  # Empty list should be invalid
            timestamp="2024-01-15T10:30:00Z"
        )
        
        with pytest.raises(SerializationError):
            MessageSerializer.serialize_message(request)
    
    def test_invalid_deserialization(self):
        """Test deserialization with invalid JSON"""
        invalid_json = b'{"invalid": "json", "missing": "required_fields"}'
        
        with pytest.raises(DeserializationError):
            MessageSerializer.deserialize_message(invalid_json, 'donation_request')

class TestKafkaMessageHelper:
    """Test Kafka message helper functions"""
    
    def test_create_donation_request(self):
        """Test creating donation request with helper"""
        donations = [
            {"category": "ALIMENTOS", "description": "Puré de tomates"},
            {"category": "ROPA", "description": "Camisetas"}
        ]
        
        request = KafkaMessageHelper.create_donation_request(
            organization_id="empuje-comunitario",
            request_id="REQ-2024-001",
            donations=donations
        )
        
        assert isinstance(request, DonationRequest)
        assert request.organization_id == "empuje-comunitario"
        assert request.request_id == "REQ-2024-001"
        assert len(request.donations) == 2
        assert request.timestamp is not None
    
    def test_create_event_adhesion(self):
        """Test creating event adhesion with helper"""
        volunteer_data = {
            "organization_id": "empuje-comunitario",
            "volunteer_id": 123,
            "name": "Juan",
            "last_name": "Pérez",
            "phone": "555-1234",
            "email": "juan@example.com"
        }
        
        adhesion = KafkaMessageHelper.create_event_adhesion(
            event_id="EVT-2024-001",
            volunteer_data=volunteer_data
        )
        
        assert isinstance(adhesion, EventAdhesion)
        assert adhesion.event_id == "EVT-2024-001"
        assert adhesion.volunteer.name == "Juan"
        assert adhesion.volunteer.email == "juan@example.com"
        assert adhesion.timestamp is not None
    
    def test_timestamp_creation(self):
        """Test timestamp creation and validation"""
        timestamp = MessageSerializer.create_timestamp()
        
        # Should be valid ISO format
        assert MessageSerializer.validate_timestamp(timestamp) == True
        
        # Should end with Z (UTC)
        assert timestamp.endswith('Z')
        
        # Should be parseable
        datetime.fromisoformat(timestamp[:-1])

if __name__ == "__main__":
    # Run basic tests
    test_models = TestModels()
    test_models.test_donation_item()
    test_models.test_donation_transfer_item()
    test_models.test_volunteer_info()
    test_models.test_donation_request()
    print("✓ Model tests passed")
    
    test_schemas = TestSchemas()
    test_schemas.test_valid_donation_request()
    test_schemas.test_valid_event_adhesion()
    print("✓ Schema validation tests passed")
    
    test_serializers = TestSerializers()
    test_serializers.test_serialize_donation_request()
    test_serializers.test_deserialize_donation_request()
    test_serializers.test_serialize_deserialize_roundtrip()
    print("✓ Serialization tests passed")
    
    test_helpers = TestKafkaMessageHelper()
    test_helpers.test_create_donation_request()
    test_helpers.test_create_event_adhesion()
    test_helpers.test_timestamp_creation()
    print("✓ Helper function tests passed")
    
    print("\n🎉 All tests passed successfully!")