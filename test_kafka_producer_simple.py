#!/usr/bin/env python3
"""
Test simple del producer de Kafka
"""
import sys
sys.path.append('messaging-service/src')

from messaging.producers.base_producer import BaseProducer
from messaging.config import Topics

def test_simple_producer():
    """Test simple del producer"""
    try:
        producer = BaseProducer()
        
        # Test simple message
        test_data = {
            "transfer_id": "test-123",
            "request_id": "req-123", 
            "source_organization": "empuje-comunitario",
            "target_organization": "esperanza-social",
            "donations": [{"test": "data"}],
            "timestamp": "2025-10-12T15:00:00",
            "user_id": 1
        }
        
        print("Testing producer...")
        success = producer.publish_donation_transfer("esperanza-social", test_data)
        
        print(f"Producer result: {success}")
        
        if success:
            print("✅ Producer funcionando")
        else:
            print("❌ Producer fallando")
        
        return success
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple_producer()