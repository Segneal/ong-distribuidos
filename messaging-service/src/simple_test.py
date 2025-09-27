"""
Simple tests for messaging models without pytest dependency
"""
import json
from datetime import datetime

from models import (
    DonationItem, DonationTransferItem, DonationOfferItem, VolunteerInfo,
    DonationRequest, DonationTransfer, DonationOffer, RequestCancellation,
    ExternalEvent, EventCancellation, EventAdhesion
)
from schemas import MessageValidator, ValidationError
from serializers import MessageSerializer, KafkaMessageHelper, SerializationError, DeserializationError

def test_donation_item():
    """Test DonationItem model"""
    print("Testing DonationItem...")
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
    print("✓ DonationItem tests passed")

def test_donation_request():
    """Test DonationRequest model"""
    print("Testing DonationRequest...")
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
    print("✓ DonationRequest tests passed")

def test_volunteer_info():
    """Test VolunteerInfo model"""
    print("Testing VolunteerInfo...")
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
    print("✓ VolunteerInfo tests passed")

def test_schema_validation():
    """Test schema validation"""
    print("Testing schema validation...")
    
    # Test valid donation request
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
    
    result = MessageValidator.validate_message('donation_request', valid_data)
    assert result == True
    
    # Test invalid data (should raise exception)
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
    
    try:
        MessageValidator.validate_message('donation_request', invalid_data)
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass  # Expected
    
    print("✓ Schema validation tests passed")

def test_serialization():
    """Test message serialization"""
    print("Testing serialization...")
    
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
    
    print("✓ Serialization tests passed")

def test_deserialization():
    """Test message deserialization"""
    print("Testing deserialization...")
    
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
    
    print("✓ Deserialization tests passed")

def test_roundtrip():
    """Test serialization/deserialization roundtrip"""
    print("Testing roundtrip...")
    
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
    
    print("✓ Roundtrip tests passed")

def test_kafka_helpers():
    """Test Kafka message helper functions"""
    print("Testing Kafka helpers...")
    
    # Test creating donation request
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
    
    # Test creating event adhesion
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
    
    print("✓ Kafka helper tests passed")

def test_all_message_types():
    """Test all message types can be created and serialized"""
    print("Testing all message types...")
    
    # Test all message types
    messages = []
    
    # DonationRequest
    donations = [DonationItem(category="ALIMENTOS", description="Puré de tomates")]
    messages.append(DonationRequest(
        organization_id="empuje-comunitario",
        request_id="REQ-2024-001",
        donations=donations,
        timestamp="2024-01-15T10:30:00Z"
    ))
    
    # DonationTransfer
    transfer_donations = [DonationTransferItem(category="ALIMENTOS", description="Puré de tomates", quantity="2kg")]
    messages.append(DonationTransfer(
        request_id="REQ-2024-001",
        donor_organization="empuje-comunitario",
        donations=transfer_donations,
        timestamp="2024-01-15T11:00:00Z"
    ))
    
    # DonationOffer
    offer_donations = [DonationOfferItem(category="ALIMENTOS", description="Puré de tomates", quantity="2kg")]
    messages.append(DonationOffer(
        offer_id="OFF-2024-001",
        donor_organization="empuje-comunitario",
        donations=offer_donations,
        timestamp="2024-01-15T12:00:00Z"
    ))
    
    # RequestCancellation
    messages.append(RequestCancellation(
        organization_id="empuje-comunitario",
        request_id="REQ-2024-001",
        timestamp="2024-01-15T13:00:00Z"
    ))
    
    # ExternalEvent
    messages.append(ExternalEvent(
        organization_id="empuje-comunitario",
        event_id="EVT-2024-001",
        name="Evento Solidario",
        description="Distribución de alimentos",
        event_date="2024-02-15T10:00:00Z",
        timestamp="2024-01-15T14:00:00Z"
    ))
    
    # EventCancellation
    messages.append(EventCancellation(
        organization_id="empuje-comunitario",
        event_id="EVT-2024-001",
        timestamp="2024-01-15T15:00:00Z"
    ))
    
    # EventAdhesion
    volunteer = VolunteerInfo(
        organization_id="empuje-comunitario",
        volunteer_id=123,
        name="Juan",
        last_name="Pérez",
        phone="555-1234",
        email="juan@example.com"
    )
    messages.append(EventAdhesion(
        event_id="EVT-2024-001",
        volunteer=volunteer,
        timestamp="2024-01-15T16:00:00Z"
    ))
    
    # Test serialization for all messages
    for message in messages:
        serialized = MessageSerializer.serialize_message(message)
        assert isinstance(serialized, bytes)
        assert len(serialized) > 0
    
    print("✓ All message types tests passed")

def main():
    """Run all tests"""
    print("=== Comprehensive Messaging Models Tests ===\n")
    
    try:
        test_donation_item()
        test_donation_request()
        test_volunteer_info()
        test_schema_validation()
        test_serialization()
        test_deserialization()
        test_roundtrip()
        test_kafka_helpers()
        test_all_message_types()
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
        print("✅ Task 2 implementation is complete and working!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())