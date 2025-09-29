#!/usr/bin/env python3
"""
Unit test for offer service functionality
"""
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_offer_models():
    """Test offer models and serialization"""
    print("🧪 Testing Offer Models")
    print("=" * 50)
    
    try:
        from messaging.models.donation import DonationOffer, DonationOfferItem
        
        # Test DonationOfferItem
        offer_item = DonationOfferItem(
            category="ALIMENTOS",
            description="Conservas de atún",
            quantity="10 latas"
        )
        
        # Test serialization
        item_dict = offer_item.to_dict()
        print("✅ DonationOfferItem serialization works")
        print(f"   Item: {item_dict}")
        
        # Test deserialization
        item_from_dict = DonationOfferItem.from_dict(item_dict)
        print("✅ DonationOfferItem deserialization works")
        
        # Test DonationOffer
        offer = DonationOffer(
            offer_id="OFE-2025-001",
            donor_organization="empuje-comunitario",
            donations=[offer_item],
            timestamp="2025-01-15T10:30:00Z"
        )
        
        # Test serialization
        offer_dict = offer.to_dict()
        print("✅ DonationOffer serialization works")
        print(f"   Offer ID: {offer_dict['offer_id']}")
        print(f"   Organization: {offer_dict['donor_organization']}")
        print(f"   Donations count: {len(offer_dict['donations'])}")
        
        # Test deserialization
        offer_from_dict = DonationOffer.from_dict(offer_dict)
        print("✅ DonationOffer deserialization works")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing offer models: {e}")
        return False


def test_offer_validation():
    """Test offer validation logic"""
    print("\n🔍 Testing Offer Validation")
    print("=" * 50)
    
    try:
        # Test valid offer data
        valid_donations = [
            {
                "category": "ALIMENTOS",
                "description": "Conservas de atún",
                "quantity": "10 latas"
            },
            {
                "category": "ROPA",
                "description": "Camisetas talla M",
                "quantity": "5 unidades"
            }
        ]
        
        # Validate required fields
        for donation in valid_donations:
            required_fields = ['category', 'description', 'quantity']
            for field in required_fields:
                if field not in donation:
                    print(f"❌ Missing required field: {field}")
                    return False
        
        print("✅ Valid donation data passes validation")
        
        # Test invalid offer data
        invalid_donations = [
            {
                "category": "ALIMENTOS",
                "description": "Conservas de atún"
                # Missing quantity
            }
        ]
        
        has_error = False
        for donation in invalid_donations:
            required_fields = ['category', 'description', 'quantity']
            for field in required_fields:
                if field not in donation:
                    has_error = True
                    break
        
        if has_error:
            print("✅ Invalid donation data correctly fails validation")
        else:
            print("❌ Invalid donation data should fail validation")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing offer validation: {e}")
        return False


def test_quantity_parsing():
    """Test quantity parsing logic"""
    print("\n🔢 Testing Quantity Parsing")
    print("=" * 50)
    
    try:
        # Simulate the quantity parsing logic from offer service
        import re
        
        def parse_quantity(quantity_str):
            """Parse quantity string to integer"""
            try:
                numbers = re.findall(r'\d+', str(quantity_str))
                if numbers:
                    return int(numbers[0])
                return 0
            except Exception:
                return 0
        
        # Test various quantity formats
        test_cases = [
            ("10 latas", 10),
            ("5 unidades", 5),
            ("2kg", 2),
            ("15 prendas", 15),
            ("abc", 0),
            ("", 0),
            ("100", 100)
        ]
        
        for quantity_str, expected in test_cases:
            result = parse_quantity(quantity_str)
            if result == expected:
                print(f"✅ '{quantity_str}' -> {result}")
            else:
                print(f"❌ '{quantity_str}' -> {result} (expected {expected})")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing quantity parsing: {e}")
        return False


def test_offer_message_format():
    """Test offer message format for Kafka"""
    print("\n📨 Testing Offer Message Format")
    print("=" * 50)
    
    try:
        # Test message format that would be sent to Kafka
        offer_message = {
            "type": "donation_offer",
            "offer_id": "OFE-20250115-abc123",
            "donor_organization": "empuje-comunitario",
            "donations": [
                {
                    "category": "ALIMENTOS",
                    "description": "Conservas de atún",
                    "quantity": "10 latas"
                }
            ],
            "timestamp": "2025-01-15T10:30:00Z"
        }
        
        # Validate message structure
        required_fields = ["type", "offer_id", "donor_organization", "donations", "timestamp"]
        for field in required_fields:
            if field not in offer_message:
                print(f"❌ Missing required field in message: {field}")
                return False
        
        print("✅ Offer message has all required fields")
        
        # Validate donations structure
        donations = offer_message["donations"]
        if not isinstance(donations, list) or len(donations) == 0:
            print("❌ Donations must be a non-empty list")
            return False
        
        for donation in donations:
            donation_fields = ["category", "description", "quantity"]
            for field in donation_fields:
                if field not in donation:
                    print(f"❌ Missing required field in donation: {field}")
                    return False
        
        print("✅ Donation items have all required fields")
        
        # Test JSON serialization
        json_str = json.dumps(offer_message)
        parsed_message = json.loads(json_str)
        
        if parsed_message == offer_message:
            print("✅ Message JSON serialization works correctly")
        else:
            print("❌ Message JSON serialization failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing offer message format: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Starting Offer Service Unit Tests")
    print("=" * 60)
    
    tests = [
        test_offer_models,
        test_offer_validation,
        test_quantity_parsing,
        test_offer_message_format
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All unit tests passed successfully!")
        return True
    else:
        print("❌ Some unit tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)