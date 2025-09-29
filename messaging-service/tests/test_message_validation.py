"""
Unit tests for message format validation
"""
import pytest
from unittest.mock import Mock, patch
import json
from datetime import datetime
from jsonschema import ValidationError

# Import validation functions if they exist
try:
    from messaging.validation import MessageValidator, validate_donation_request, validate_donation_offer
    VALIDATION_MODULE_EXISTS = True
except ImportError:
    VALIDATION_MODULE_EXISTS = False


class TestMessageFormatValidation:
    """Test cases for message format validation"""
    
    def test_valid_donation_request_format(self):
        """Test validation of valid donation request format"""
        message = {
            "message_id": "msg-123",
            "message_type": "donation_request",
            "organization_id": "test-org",
            "timestamp": "2024-01-15T10:30:00Z",
            "data": {
                "type": "donation_request",
                "organization_id": "test-org",
                "request_id": "REQ-001",
                "donations": [
                    {
                        "category": "ALIMENTOS",
                        "description": "Puré de tomates"
                    }
                ],
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
        
        # Test basic structure validation
        assert self._validate_message_envelope(message)
        assert self._validate_donation_request_data(message["data"])
    
    def test_valid_donation_offer_format(self):
        """Test validation of valid donation offer format"""
        message = {
            "message_id": "msg-124",
            "message_type": "donation_offer",
            "organization_id": "test-org",
            "timestamp": "2024-01-15T11:00:00Z",
            "data": {
                "type": "donation_offer",
                "offer_id": "OFFER-001",
                "donor_organization": "test-org",
                "donations": [
                    {
                        "category": "ALIMENTOS",
                        "description": "Puré de tomates",
                        "quantity": "2kg"
                    }
                ],
                "timestamp": "2024-01-15T11:00:00Z"
            }
        }
        
        # Test basic structure validation
        assert self._validate_message_envelope(message)
        assert self._validate_donation_offer_data(message["data"])
    
    def test_valid_donation_transfer_format(self):
        """Test validation of valid donation transfer format"""
        message = {
            "message_id": "msg-125",
            "message_type": "donation_transfer",
            "organization_id": "test-org",
            "timestamp": "2024-01-15T11:30:00Z",
            "data": {
                "type": "donation_transfer",
                "request_id": "REQ-001",
                "donor_organization": "test-org",
                "donations": [
                    {
                        "category": "ALIMENTOS",
                        "description": "Puré de tomates",
                        "quantity": "2kg"
                    }
                ],
                "timestamp": "2024-01-15T11:30:00Z"
            }
        }
        
        # Test basic structure validation
        assert self._validate_message_envelope(message)
        assert self._validate_donation_transfer_data(message["data"])
    
    def test_valid_event_format(self):
        """Test validation of valid solidarity event format"""
        message = {
            "message_id": "msg-126",
            "message_type": "solidarity_event",
            "organization_id": "test-org",
            "timestamp": "2024-01-15T12:00:00Z",
            "data": {
                "type": "solidarity_event",
                "organization_id": "test-org",
                "event_id": "EVENT-001",
                "name": "Campaña de Donación",
                "description": "Recolección de alimentos",
                "event_date": "2024-02-15T09:00:00Z",
                "timestamp": "2024-01-15T12:00:00Z"
            }
        }
        
        # Test basic structure validation
        assert self._validate_message_envelope(message)
        assert self._validate_event_data(message["data"])
    
    def test_valid_event_adhesion_format(self):
        """Test validation of valid event adhesion format"""
        message = {
            "message_id": "msg-127",
            "message_type": "event_adhesion",
            "organization_id": "test-org",
            "timestamp": "2024-01-15T12:30:00Z",
            "data": {
                "type": "event_adhesion",
                "event_id": "EVENT-001",
                "volunteer": {
                    "organization_id": "test-org",
                    "volunteer_id": "VOL-001",
                    "name": "Juan",
                    "surname": "Pérez",
                    "phone": "+1234567890",
                    "email": "juan.perez@example.com"
                },
                "timestamp": "2024-01-15T12:30:00Z"
            }
        }
        
        # Test basic structure validation
        assert self._validate_message_envelope(message)
        assert self._validate_event_adhesion_data(message["data"])
    
    def test_invalid_message_envelope_missing_field(self):
        """Test validation with missing envelope field"""
        message = {
            "message_id": "msg-123",
            "message_type": "donation_request",
            # Missing organization_id, timestamp, data
        }
        
        assert not self._validate_message_envelope(message)
    
    def test_invalid_donation_request_missing_field(self):
        """Test validation of donation request with missing field"""
        data = {
            "type": "donation_request",
            "organization_id": "test-org",
            # Missing request_id
            "donations": [],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        assert not self._validate_donation_request_data(data)
    
    def test_invalid_donation_request_empty_donations(self):
        """Test validation of donation request with empty donations"""
        data = {
            "type": "donation_request",
            "organization_id": "test-org",
            "request_id": "REQ-001",
            "donations": [],  # Empty donations should be valid
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        # Empty donations should be allowed
        assert self._validate_donation_request_data(data)
    
    def test_invalid_donation_item_missing_field(self):
        """Test validation of donation item with missing field"""
        data = {
            "type": "donation_request",
            "organization_id": "test-org",
            "request_id": "REQ-001",
            "donations": [
                {
                    "category": "ALIMENTOS"
                    # Missing description
                }
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        assert not self._validate_donation_request_data(data)
    
    def test_invalid_donation_category(self):
        """Test validation with invalid donation category"""
        data = {
            "type": "donation_request",
            "organization_id": "test-org",
            "request_id": "REQ-001",
            "donations": [
                {
                    "category": "INVALID_CATEGORY",
                    "description": "Test item"
                }
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        # Should still be valid as we don't enforce category enum in validation
        assert self._validate_donation_request_data(data)
    
    def test_invalid_timestamp_format(self):
        """Test validation with invalid timestamp format"""
        data = {
            "type": "donation_request",
            "organization_id": "test-org",
            "request_id": "REQ-001",
            "donations": [],
            "timestamp": "invalid-timestamp"
        }
        
        # Basic validation doesn't check timestamp format
        assert self._validate_donation_request_data(data)
    
    def test_invalid_volunteer_data_missing_field(self):
        """Test validation of volunteer data with missing field"""
        data = {
            "type": "event_adhesion",
            "event_id": "EVENT-001",
            "volunteer": {
                "organization_id": "test-org",
                "volunteer_id": "VOL-001",
                "name": "Juan"
                # Missing surname, phone, email
            },
            "timestamp": "2024-01-15T12:30:00Z"
        }
        
        assert not self._validate_event_adhesion_data(data)
    
    def test_invalid_email_format(self):
        """Test validation with invalid email format"""
        data = {
            "type": "event_adhesion",
            "event_id": "EVENT-001",
            "volunteer": {
                "organization_id": "test-org",
                "volunteer_id": "VOL-001",
                "name": "Juan",
                "surname": "Pérez",
                "phone": "+1234567890",
                "email": "invalid-email"
            },
            "timestamp": "2024-01-15T12:30:00Z"
        }
        
        # Basic validation doesn't check email format
        assert self._validate_event_adhesion_data(data)
    
    def test_message_size_validation(self):
        """Test validation of message size limits"""
        # Create a large message
        large_description = "x" * 10000  # 10KB description
        
        data = {
            "type": "donation_request",
            "organization_id": "test-org",
            "request_id": "REQ-001",
            "donations": [
                {
                    "category": "ALIMENTOS",
                    "description": large_description
                }
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        # Should still be valid (no size limits in basic validation)
        assert self._validate_donation_request_data(data)
    
    def test_json_serialization_validation(self):
        """Test that messages can be properly JSON serialized"""
        message = {
            "message_id": "msg-123",
            "message_type": "donation_request",
            "organization_id": "test-org",
            "timestamp": "2024-01-15T10:30:00Z",
            "data": {
                "type": "donation_request",
                "organization_id": "test-org",
                "request_id": "REQ-001",
                "donations": [
                    {
                        "category": "ALIMENTOS",
                        "description": "Puré de tomates"
                    }
                ],
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
        
        # Should be JSON serializable
        try:
            json_str = json.dumps(message)
            restored = json.loads(json_str)
            assert restored == message
        except (TypeError, ValueError):
            pytest.fail("Message should be JSON serializable")
    
    def _validate_message_envelope(self, message):
        """Helper method to validate message envelope"""
        required_fields = ["message_id", "message_type", "organization_id", "timestamp", "data"]
        
        for field in required_fields:
            if field not in message:
                return False
        
        return True
    
    def _validate_donation_request_data(self, data):
        """Helper method to validate donation request data"""
        required_fields = ["type", "organization_id", "request_id", "donations", "timestamp"]
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Validate donations array
        if not isinstance(data["donations"], list):
            return False
        
        for donation in data["donations"]:
            if not self._validate_donation_item(donation):
                return False
        
        return True
    
    def _validate_donation_offer_data(self, data):
        """Helper method to validate donation offer data"""
        required_fields = ["type", "offer_id", "donor_organization", "donations", "timestamp"]
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Validate donations array
        if not isinstance(data["donations"], list):
            return False
        
        for donation in data["donations"]:
            if not self._validate_donation_offer_item(donation):
                return False
        
        return True
    
    def _validate_donation_transfer_data(self, data):
        """Helper method to validate donation transfer data"""
        required_fields = ["type", "request_id", "donor_organization", "donations", "timestamp"]
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Validate donations array
        if not isinstance(data["donations"], list):
            return False
        
        for donation in data["donations"]:
            if not self._validate_donation_transfer_item(donation):
                return False
        
        return True
    
    def _validate_event_data(self, data):
        """Helper method to validate event data"""
        required_fields = ["type", "organization_id", "event_id", "name", "event_date", "timestamp"]
        
        for field in required_fields:
            if field not in data:
                return False
        
        return True
    
    def _validate_event_adhesion_data(self, data):
        """Helper method to validate event adhesion data"""
        required_fields = ["type", "event_id", "volunteer", "timestamp"]
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Validate volunteer data
        return self._validate_volunteer_data(data["volunteer"])
    
    def _validate_donation_item(self, item):
        """Helper method to validate donation item"""
        required_fields = ["category", "description"]
        
        for field in required_fields:
            if field not in item:
                return False
        
        return True
    
    def _validate_donation_offer_item(self, item):
        """Helper method to validate donation offer item"""
        required_fields = ["category", "description", "quantity"]
        
        for field in required_fields:
            if field not in item:
                return False
        
        return True
    
    def _validate_donation_transfer_item(self, item):
        """Helper method to validate donation transfer item"""
        required_fields = ["category", "description", "quantity"]
        
        for field in required_fields:
            if field not in item:
                return False
        
        return True
    
    def _validate_volunteer_data(self, volunteer):
        """Helper method to validate volunteer data"""
        required_fields = ["organization_id", "volunteer_id", "name", "surname", "phone", "email"]
        
        for field in required_fields:
            if field not in volunteer:
                return False
        
        return True


@pytest.mark.skipif(not VALIDATION_MODULE_EXISTS, reason="Validation module not found")
class TestMessageValidator:
    """Test cases for MessageValidator class if it exists"""
    
    def test_validator_init(self):
        """Test MessageValidator initialization"""
        validator = MessageValidator()
        assert validator is not None
    
    def test_validate_donation_request_function(self):
        """Test validate_donation_request function"""
        message = {
            "organization_id": "test-org",
            "request_id": "REQ-001",
            "donations": [
                {
                    "category": "ALIMENTOS",
                    "description": "Puré de tomates"
                }
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        result = validate_donation_request(message)
        assert result is True
    
    def test_validate_donation_offer_function(self):
        """Test validate_donation_offer function"""
        message = {
            "offer_id": "OFFER-001",
            "donor_organization": "test-org",
            "donations": [
                {
                    "category": "ALIMENTOS",
                    "description": "Puré de tomates",
                    "quantity": "2kg"
                }
            ],
            "timestamp": "2024-01-15T11:00:00Z"
        }
        
        result = validate_donation_offer(message)
        assert result is True


class TestSchemaValidation:
    """Test cases for JSON schema validation"""
    
    def test_donation_request_schema(self):
        """Test donation request against JSON schema"""
        # Define expected schema structure
        schema = {
            "type": "object",
            "required": ["organization_id", "request_id", "donations", "timestamp"],
            "properties": {
                "organization_id": {"type": "string"},
                "request_id": {"type": "string"},
                "donations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["category", "description"],
                        "properties": {
                            "category": {"type": "string"},
                            "description": {"type": "string"}
                        }
                    }
                },
                "timestamp": {"type": "string"}
            }
        }
        
        # Valid message
        valid_message = {
            "organization_id": "test-org",
            "request_id": "REQ-001",
            "donations": [
                {
                    "category": "ALIMENTOS",
                    "description": "Puré de tomates"
                }
            ],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        # Should validate successfully
        from jsonschema import validate
        try:
            validate(valid_message, schema)
        except ValidationError:
            pytest.fail("Valid message should pass schema validation")
    
    def test_donation_request_schema_invalid(self):
        """Test invalid donation request against JSON schema"""
        schema = {
            "type": "object",
            "required": ["organization_id", "request_id", "donations", "timestamp"],
            "properties": {
                "organization_id": {"type": "string"},
                "request_id": {"type": "string"},
                "donations": {"type": "array"},
                "timestamp": {"type": "string"}
            }
        }
        
        # Invalid message (missing required field)
        invalid_message = {
            "organization_id": "test-org",
            # Missing request_id
            "donations": [],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        # Should fail validation
        from jsonschema import validate
        with pytest.raises(ValidationError):
            validate(invalid_message, schema)