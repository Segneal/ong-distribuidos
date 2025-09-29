#!/usr/bin/env python3
"""
Test script for donation transfer functionality
"""
import sys
import os
import json
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.dirname(__file__))

from transfer_service import TransferService
from donation_transfer_producer import DonationTransferProducer
from donation_transfer_consumer import DonationTransferConsumer
from models import DonationTransfer, DonationTransferItem
from database import test_database_connection


def test_transfer_service():
    """Test the transfer service functionality"""
    print("=== Testing Transfer Service ===")
    
    # Test database connection
    print("1. Testing database connection...")
    if test_database_connection():
        print("   ✓ Database connection successful")
    else:
        print("   ✗ Database connection failed")
        return False
    
    # Initialize transfer service
    print("2. Initializing transfer service...")
    transfer_service = TransferService()
    print("   ✓ Transfer service initialized")
    
    # Test validation
    print("3. Testing transfer validation...")
    
    # Valid transfer data
    valid_donations = [
        {"donation_id": 1, "quantity": 5},
        {"donation_id": 2, "quantity": 3}
    ]
    
    # Invalid transfer data (missing fields)
    invalid_donations = [
        {"donation_id": 1},  # Missing quantity
        {"quantity": 3}      # Missing donation_id
    ]
    
    # Test with invalid data
    success, message = transfer_service.transfer_donations(
        "test-org", "REQ-001", invalid_donations, 1
    )
    
    if not success and "donation_id y quantity" in message:
        print("   ✓ Validation correctly rejected invalid data")
    else:
        print(f"   ✗ Validation failed: {message}")
    
    print("   Transfer service tests completed")
    return True


def test_transfer_producer():
    """Test the transfer producer"""
    print("\n=== Testing Transfer Producer ===")
    
    producer = DonationTransferProducer()
    
    # Test validation
    print("1. Testing producer validation...")
    
    valid_donations = [
        {"category": "ALIMENTOS", "description": "Conservas", "quantity": "5 latas"},
        {"category": "ROPA", "description": "Camisetas", "quantity": "10 unidades"}
    ]
    
    if producer.validate_transfer_data(valid_donations):
        print("   ✓ Valid data accepted")
    else:
        print("   ✗ Valid data rejected")
    
    invalid_donations = [
        {"category": "INVALID", "description": "Test", "quantity": "5"},
        {"category": "ALIMENTOS", "description": "Test", "quantity": "-1"}
    ]
    
    if not producer.validate_transfer_data(invalid_donations):
        print("   ✓ Invalid data correctly rejected")
    else:
        print("   ✗ Invalid data accepted")
    
    print("   Producer tests completed")
    return True


def test_transfer_consumer():
    """Test the transfer consumer"""
    print("\n=== Testing Transfer Consumer ===")
    
    consumer = DonationTransferConsumer()
    
    # Test message validation
    print("1. Testing consumer validation...")
    
    # Valid transfer message
    valid_transfer = DonationTransfer(
        request_id="REQ-001",
        donor_organization="test-org",
        donations=[
            DonationTransferItem(
                category="ALIMENTOS",
                description="Conservas variadas",
                quantity="5 latas"
            )
        ],
        timestamp=datetime.utcnow().isoformat()
    )
    
    if consumer._validate_transfer(valid_transfer):
        print("   ✓ Valid transfer accepted")
    else:
        print("   ✗ Valid transfer rejected")
    
    # Invalid transfer (from own organization)
    invalid_transfer = DonationTransfer(
        request_id="REQ-002",
        donor_organization="empuje-comunitario",  # Our own org
        donations=[
            DonationTransferItem(
                category="ALIMENTOS",
                description="Test",
                quantity="1 unidad"
            )
        ],
        timestamp=datetime.utcnow().isoformat()
    )
    
    if not consumer._validate_transfer(invalid_transfer):
        print("   ✓ Own organization transfer correctly rejected")
    else:
        print("   ✗ Own organization transfer accepted")
    
    print("   Consumer tests completed")
    return True


def test_models():
    """Test the transfer models"""
    print("\n=== Testing Transfer Models ===")
    
    # Test DonationTransferItem
    print("1. Testing DonationTransferItem...")
    
    item = DonationTransferItem(
        category="ALIMENTOS",
        description="Conservas de tomate",
        quantity="10 latas"
    )
    
    item_dict = item.to_dict()
    item_restored = DonationTransferItem.from_dict(item_dict)
    
    if (item.category == item_restored.category and 
        item.description == item_restored.description and 
        item.quantity == item_restored.quantity):
        print("   ✓ DonationTransferItem serialization works")
    else:
        print("   ✗ DonationTransferItem serialization failed")
    
    # Test DonationTransfer
    print("2. Testing DonationTransfer...")
    
    transfer = DonationTransfer(
        request_id="REQ-001",
        donor_organization="test-org",
        donations=[item],
        timestamp=datetime.utcnow().isoformat()
    )
    
    transfer_dict = transfer.to_dict()
    transfer_restored = DonationTransfer.from_dict(transfer_dict)
    
    if (transfer.request_id == transfer_restored.request_id and
        transfer.donor_organization == transfer_restored.donor_organization and
        len(transfer.donations) == len(transfer_restored.donations)):
        print("   ✓ DonationTransfer serialization works")
    else:
        print("   ✗ DonationTransfer serialization failed")
    
    print("   Model tests completed")
    return True


def main():
    """Run all tests"""
    print("Starting donation transfer functionality tests...\n")
    
    tests = [
        test_models,
        test_transfer_producer,
        test_transfer_consumer,
        test_transfer_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ✗ Test failed with exception: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)