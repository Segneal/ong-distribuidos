"""
Simple validation script to check model imports and basic functionality
"""
import sys
import traceback

def test_imports():
    """Test that all modules can be imported successfully"""
    try:
        print("Testing imports...")
        
        # Test model imports
        from models import (
            DonationItem, DonationTransferItem, DonationOfferItem, VolunteerInfo,
            DonationRequest, DonationTransfer, DonationOffer, RequestCancellation,
            ExternalEvent, EventCancellation, EventAdhesion, DonationCategory
        )
        print("✓ Models imported successfully")
        
        # Test schema imports
        from schemas import MessageValidator, SCHEMAS
        print("✓ Schemas imported successfully")
        
        # Test serializer imports
        from serializers import MessageSerializer, KafkaMessageHelper
        print("✓ Serializers imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic model functionality"""
    try:
        print("\nTesting basic functionality...")
        
        from models import DonationItem, DonationRequest
        from serializers import MessageSerializer
        
        # Test creating a donation item
        item = DonationItem(category="ALIMENTOS", description="Puré de tomates")
        item_dict = item.to_dict()
        assert item_dict['category'] == 'ALIMENTOS'
        assert item_dict['description'] == 'Puré de tomates'
        print("✓ DonationItem creation and serialization works")
        
        # Test creating a donation request
        request = DonationRequest(
            organization_id="empuje-comunitario",
            request_id="REQ-2024-001",
            donations=[item],
            timestamp="2024-01-15T10:30:00Z"
        )
        request_dict = request.to_dict()
        assert request_dict['organization_id'] == 'empuje-comunitario'
        assert len(request_dict['donations']) == 1
        print("✓ DonationRequest creation and serialization works")
        
        # Test timestamp creation
        timestamp = MessageSerializer.create_timestamp()
        assert timestamp.endswith('Z')
        print("✓ Timestamp creation works")
        
        return True
        
    except Exception as e:
        print(f"✗ Functionality error: {e}")
        traceback.print_exc()
        return False

def test_schema_validation():
    """Test schema validation"""
    try:
        print("\nTesting schema validation...")
        
        from schemas import MessageValidator
        
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
        print("✓ Schema validation works for valid data")
        
        # Test getting schema
        schema = MessageValidator.get_schema('donation_request')
        assert 'properties' in schema
        print("✓ Schema retrieval works")
        
        return True
        
    except Exception as e:
        print(f"✗ Schema validation error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all validation tests"""
    print("=== Messaging Models Validation ===\n")
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test basic functionality
    if not test_basic_functionality():
        success = False
    
    # Test schema validation
    if not test_schema_validation():
        success = False
    
    print("\n" + "="*40)
    if success:
        print("🎉 All validation tests passed!")
        return 0
    else:
        print("❌ Some validation tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())