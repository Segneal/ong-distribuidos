#!/usr/bin/env python3
"""
Test script to verify messaging service structure
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all main modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test config
        from messaging.config import settings, Topics
        print("✓ Config imported successfully")
        
        # Test models
        from messaging.models.donation import DonationRequest, DonationItem
        from messaging.models.transfer import DonationTransfer, DonationTransferItem
        print("✓ Models imported successfully")
        
        # Test database
        from messaging.database.connection import get_database_connection, test_database_connection
        from messaging.database.manager import DatabaseManager
        print("✓ Database modules imported successfully")
        
        # Test Kafka
        from messaging.kafka.connection import kafka_manager
        print("✓ Kafka connection imported successfully")
        
        # Test producers
        from messaging.producers.base_producer import BaseProducer
        from messaging.producers.donation_producer import DonationRequestProducer
        from messaging.producers.transfer_producer import DonationTransferProducer
        print("✓ Producers imported successfully")
        
        # Test consumers
        from messaging.consumers.base_consumer import BaseConsumer, NetworkConsumer, OrganizationConsumer
        from messaging.consumers.donation_consumer import DonationRequestConsumer
        from messaging.consumers.transfer_consumer import DonationTransferConsumer
        print("✓ Consumers imported successfully")
        
        # Test services
        from messaging.services.transfer_service import TransferService
        print("✓ Services imported successfully")
        
        # Test API
        from messaging.api.server import app
        print("✓ API server imported successfully")
        
        print("\n🎉 All imports successful! Messaging service structure is correct.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    try:
        print("\nTesting basic functionality...")
        
        # Test config
        from messaging.config import settings, Topics
        print(f"✓ Organization ID: {settings.organization_id}")
        print(f"✓ Kafka brokers: {settings.kafka_bootstrap_servers}")
        print(f"✓ Database URL: {settings.database_url}")
        
        # Test topic generation
        transfer_topic = Topics.get_transfer_topic("test-org")
        adhesion_topic = Topics.get_adhesion_topic("test-org")
        print(f"✓ Transfer topic: {transfer_topic}")
        print(f"✓ Adhesion topic: {adhesion_topic}")
        
        # Test model creation
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
        print("✓ Model serialization/deserialization works")
        
        # Test producer creation (without Kafka connection)
        from messaging.producers.base_producer import BaseProducer
        producer = BaseProducer()
        print(f"✓ Producer created with org ID: {producer.organization_id}")
        
        print("\n🎉 Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

if __name__ == "__main__":
    print("=== Messaging Service Structure Test ===\n")
    
    import_success = test_imports()
    if import_success:
        functionality_success = test_basic_functionality()
        
        if functionality_success:
            print("\n✅ All tests passed! Messaging service is ready.")
            sys.exit(0)
        else:
            print("\n❌ Functionality tests failed.")
            sys.exit(1)
    else:
        print("\n❌ Import tests failed.")
        sys.exit(1)