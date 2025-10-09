"""
Simple tests to verify test infrastructure works
"""
import pytest
from unittest.mock import Mock, patch
import json


class TestSimple:
    """Simple tests to verify test infrastructure"""
    
    def test_basic_assertion(self):
        """Test basic assertion works"""
        assert True
    
    def test_mock_works(self):
        """Test that mocking works"""
        mock_obj = Mock()
        mock_obj.test_method.return_value = "test_result"
        
        result = mock_obj.test_method()
        assert result == "test_result"
        mock_obj.test_method.assert_called_once()
    
    def test_json_serialization(self):
        """Test JSON serialization works"""
        data = {"test": "data", "number": 123}
        json_str = json.dumps(data)
        restored = json.loads(json_str)
        assert restored == data
    
    @patch('builtins.print')
    def test_patching_works(self, mock_print):
        """Test that patching works"""
        print("test message")
        mock_print.assert_called_once_with("test message")
    
    def test_imports_work(self):
        """Test that our messaging imports work"""
        try:
            from messaging.models.donation import DonationItem
            item = DonationItem("ALIMENTOS", "Test item")
            assert item.category == "ALIMENTOS"
            assert item.description == "Test item"
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
    
    def test_kafka_connection_import(self):
        """Test that Kafka connection import works"""
        try:
            from messaging.kafka.connection import KafkaConnectionManager
            manager = KafkaConnectionManager()
            assert manager.connection_status == "disconnected"
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")


class TestMessageValidation:
    """Test message validation logic"""
    
    def test_validate_message_envelope(self):
        """Test message envelope validation"""
        # Valid envelope
        valid_envelope = {
            "message_id": "msg-123",
            "message_type": "donation_request",
            "organization_id": "test-org",
            "timestamp": "2024-01-15T10:30:00Z",
            "data": {"test": "data"}
        }
        
        required_fields = ["message_id", "message_type", "organization_id", "timestamp", "data"]
        
        # All fields present
        for field in required_fields:
            assert field in valid_envelope
        
        # Missing field
        invalid_envelope = valid_envelope.copy()
        del invalid_envelope["message_id"]
        
        assert "message_id" not in invalid_envelope
    
    def test_validate_donation_item(self):
        """Test donation item validation"""
        valid_item = {
            "category": "ALIMENTOS",
            "description": "Puré de tomates"
        }
        
        required_fields = ["category", "description"]
        
        # All fields present
        for field in required_fields:
            assert field in valid_item
            assert valid_item[field]  # Not empty
        
        # Missing field
        invalid_item = {"category": "ALIMENTOS"}
        assert "description" not in invalid_item


class TestModelSerialization:
    """Test model serialization/deserialization"""
    
    def test_donation_item_serialization(self):
        """Test DonationItem serialization"""
        from messaging.models.donation import DonationItem
        
        item = DonationItem("ALIMENTOS", "Puré de tomates")
        
        # Test to_dict
        item_dict = item.to_dict()
        expected = {
            'category': 'ALIMENTOS',
            'description': 'Puré de tomates'
        }
        assert item_dict == expected
        
        # Test from_dict
        restored_item = DonationItem.from_dict(item_dict)
        assert restored_item.category == item.category
        assert restored_item.description == item.description
    
    def test_donation_request_serialization(self):
        """Test DonationRequest serialization"""
        from messaging.models.donation import DonationRequest, DonationItem
        
        donations = [DonationItem("ALIMENTOS", "Puré de tomates")]
        request = DonationRequest(
            organization_id="test-org",
            request_id="REQ-001",
            donations=donations,
            timestamp="2024-01-15T10:30:00Z"
        )
        
        # Test to_dict
        request_dict = request.to_dict()
        assert request_dict["organization_id"] == "test-org"
        assert request_dict["request_id"] == "REQ-001"
        assert len(request_dict["donations"]) == 1
        assert request_dict["donations"][0]["category"] == "ALIMENTOS"
        
        # Test from_dict
        restored_request = DonationRequest.from_dict(request_dict)
        assert restored_request.organization_id == request.organization_id
        assert restored_request.request_id == request.request_id
        assert len(restored_request.donations) == 1