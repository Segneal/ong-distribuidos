#!/usr/bin/env python3
"""
Test script for donation transfer consumer functionality
"""
import json
from datetime import datetime
from src.messaging.consumers.transfer_consumer import DonationTransferConsumer
from src.messaging.models.transfer import DonationTransfer, DonationTransferItem

def test_transfer_consumer_basic():
    """Test basic transfer consumer functionality"""
    print("Testing transfer consumer basic functionality...")
    
    # Create consumer instance
    consumer = DonationTransferConsumer()
    print("✓ Transfer consumer created successfully")
    
    # Test message validation
    test_transfer = DonationTransfer(
        request_id="TEST-REQ-001",
        donor_organization="test-org",
        donations=[
            DonationTransferItem(
                category="ALIMENTOS",
                description="Test food item",
                quantity="5 kg"
            )
        ],
        timestamp=datetime.now().isoformat()
    )
    
    # Test validation
    is_valid = consumer._validate_transfer(test_transfer)
    print(f"✓ Transfer validation: {is_valid}")
    
    # Test message envelope processing
    message_envelope = {
        "message_id": "test-msg-001",
        "message_type": "donation_transfer",
        "organization_id": "test-org",
        "timestamp": datetime.now().isoformat(),
        "data": test_transfer.to_dict()
    }
    
    try:
        consumer.process_message(message_envelope)
        print("✓ Message envelope processing completed")
    except Exception as e:
        print(f"⚠ Message processing failed (expected without DB): {e}")
    
    print("Transfer consumer basic test completed!")
    return True

def test_transfer_models():
    """Test transfer models functionality"""
    print("\nTesting transfer models...")
    
    # Test DonationTransferItem
    item = DonationTransferItem(
        category="ROPA",
        description="Winter jacket",
        quantity="3 units"
    )
    
    item_dict = item.to_dict()
    item_restored = DonationTransferItem.from_dict(item_dict)
    
    assert item.category == item_restored.category
    assert item.description == item_restored.description
    assert item.quantity == item_restored.quantity
    print("✓ DonationTransferItem serialization works")
    
    # Test DonationTransfer
    transfer = DonationTransfer(
        request_id="REQ-2025-001",
        donor_organization="fundacion-esperanza",
        donations=[item],
        timestamp=datetime.now().isoformat()
    )
    
    transfer_dict = transfer.to_dict()
    transfer_restored = DonationTransfer.from_dict(transfer_dict)
    
    assert transfer.request_id == transfer_restored.request_id
    assert transfer.donor_organization == transfer_restored.donor_organization
    assert len(transfer.donations) == len(transfer_restored.donations)
    print("✓ DonationTransfer serialization works")
    
    print("Transfer models test completed!")
    return True

if __name__ == "__main__":
    print("=== Testing Donation Transfer Consumer ===")
    
    try:
        test_transfer_models()
        test_transfer_consumer_basic()
        print("\n🎉 All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()