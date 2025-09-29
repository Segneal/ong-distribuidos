#!/usr/bin/env python3
"""
Simple test script to verify messaging service structure without external dependencies
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_imports():
    """Test that basic modules can be imported"""
    try:
        print("Testing basic imports...")
        
        # Test config (basic structure)
        from messaging.config import Settings, Topics
        print("✓ Config classes imported successfully")
        
        # Test models
        from messaging.models.donation import DonationRequest, DonationItem
        from messaging.models.transfer import DonationTransfer, DonationTransferItem
        print("✓ Models imported successfully")
        
        print("\n🎉 Basic imports successful! Core structure is correct.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_model_functionality():
    """Test model functionality"""
    try:
        print("\nTesting model functionality...")
        
        # Test donation models
        from messaging.models.donation import DonationItem, DonationRequest
        
        donation_item = DonationItem(category="ROPA", description="Camisetas")
        donation_request = DonationRequest(
            organization_id="test-org",
            request_id="test-req-001",
            donations=[donation_item],
            timestamp="2024-01-01T00:00:00Z"
        )
        
        # Test serialization
        request_dict = donation_request.to_dict()
        restored_request = DonationRequest.from_dict(request_dict)
        
        assert restored_request.organization_id == donation_request.organization_id
        assert restored_request.request_id == donation_request.request_id
        assert len(restored_request.donations) == 1
        assert restored_request.donations[0].category == "ROPA"
        
        print("✓ Donation model serialization works")
        
        # Test transfer models
        from messaging.models.transfer import DonationTransferItem, DonationTransfer
        
        transfer_item = DonationTransferItem(
            category="ALIMENTOS",
            description="Arroz",
            quantity="10 kg"
        )
        
        transfer = DonationTransfer(
            request_id="test-req-001",
            donor_organization="donor-org",
            donations=[transfer_item],
            timestamp="2024-01-01T00:00:00Z"
        )
        
        transfer_dict = transfer.to_dict()
        restored_transfer = DonationTransfer.from_dict(transfer_dict)
        
        assert restored_transfer.request_id == transfer.request_id
        assert restored_transfer.donor_organization == transfer.donor_organization
        assert len(restored_transfer.donations) == 1
        assert restored_transfer.donations[0].quantity == "10 kg"
        
        print("✓ Transfer model serialization works")
        
        print("\n🎉 Model functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Model functionality test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_functionality():
    """Test config functionality"""
    try:
        print("\nTesting config functionality...")
        
        from messaging.config import Settings, Topics
        
        # Test Settings class
        settings = Settings()
        print(f"✓ Settings instance created")
        print(f"✓ Organization ID: {settings.organization_id}")
        print(f"✓ Kafka brokers: {settings.kafka_brokers}")
        
        # Test Topics class
        transfer_topic = Topics.get_transfer_topic("test-org")
        adhesion_topic = Topics.get_adhesion_topic("test-org")
        
        assert transfer_topic == f"{Topics.DONATION_TRANSFERS}-test-org"
        assert adhesion_topic == f"{Topics.EVENT_ADHESIONS}-test-org"
        
        print(f"✓ Transfer topic: {transfer_topic}")
        print(f"✓ Adhesion topic: {adhesion_topic}")
        
        print("\n🎉 Config functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Config functionality test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_file_structure():
    """Check that all expected files exist"""
    print("\nChecking file structure...")
    
    expected_files = [
        "src/messaging/__init__.py",
        "src/messaging/config.py",
        "src/messaging/models/__init__.py",
        "src/messaging/models/donation.py",
        "src/messaging/models/transfer.py",
        "src/messaging/models/event.py",
        "src/messaging/database/__init__.py",
        "src/messaging/database/connection.py",
        "src/messaging/database/manager.py",
        "src/messaging/kafka/__init__.py",
        "src/messaging/kafka/connection.py",
        "src/messaging/producers/__init__.py",
        "src/messaging/producers/base_producer.py",
        "src/messaging/producers/donation_producer.py",
        "src/messaging/producers/transfer_producer.py",
        "src/messaging/consumers/__init__.py",
        "src/messaging/consumers/base_consumer.py",
        "src/messaging/consumers/donation_consumer.py",
        "src/messaging/consumers/transfer_consumer.py",
        "src/messaging/services/__init__.py",
        "src/messaging/services/transfer_service.py",
        "src/messaging/api/__init__.py",
        "src/messaging/api/server.py",
        "src/main.py"
    ]
    
    missing_files = []
    for file_path in expected_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print(f"\n✅ All {len(expected_files)} expected files exist!")
        return True

if __name__ == "__main__":
    print("=== Messaging Service Simple Structure Test ===\n")
    
    structure_ok = check_file_structure()
    if not structure_ok:
        print("\n❌ File structure check failed.")
        sys.exit(1)
    
    import_success = test_basic_imports()
    if not import_success:
        print("\n❌ Import tests failed.")
        sys.exit(1)
    
    config_success = test_config_functionality()
    if not config_success:
        print("\n❌ Config tests failed.")
        sys.exit(1)
    
    model_success = test_model_functionality()
    if not model_success:
        print("\n❌ Model tests failed.")
        sys.exit(1)
    
    print("\n✅ All tests passed! Messaging service structure is correct and functional.")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Set up environment variables")
    print("3. Start the service: python src/main.py")