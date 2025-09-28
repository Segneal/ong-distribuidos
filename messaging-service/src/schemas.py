"""
JSON Schema validators for messaging models
"""
from typing import Dict, Any
import jsonschema
from jsonschema import validate, ValidationError

# Base schemas for reusable components
DONATION_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "enum": ["ROPA", "ALIMENTOS", "JUGUETES", "UTILES_ESCOLARES"]
        },
        "description": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
        }
    },
    "required": ["category", "description"],
    "additionalProperties": False
}

DONATION_TRANSFER_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "enum": ["ROPA", "ALIMENTOS", "JUGUETES", "UTILES_ESCOLARES"]
        },
        "description": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
        },
        "quantity": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        }
    },
    "required": ["category", "description", "quantity"],
    "additionalProperties": False
}

DONATION_OFFER_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "enum": ["ROPA", "ALIMENTOS", "JUGUETES", "UTILES_ESCOLARES"]
        },
        "description": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
        },
        "quantity": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        }
    },
    "required": ["category", "description", "quantity"],
    "additionalProperties": False
}

VOLUNTEER_INFO_SCHEMA = {
    "type": "object",
    "properties": {
        "organization_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "volunteer_id": {
            "type": "integer",
            "minimum": 1
        },
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "last_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "phone": {
            "type": ["string", "null"],
            "maxLength": 20
        },
        "email": {
            "type": "string",
            "format": "email",
            "maxLength": 255
        }
    },
    "required": ["organization_id", "volunteer_id", "name", "last_name", "email"],
    "additionalProperties": False
}

# Message schemas
DONATION_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "organization_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "request_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "donations": {
            "type": "array",
            "items": DONATION_ITEM_SCHEMA,
            "minItems": 1,
            "maxItems": 100
        },
        "timestamp": {
            "type": "string",
            "format": "date-time"
        }
    },
    "required": ["organization_id", "request_id", "donations", "timestamp"],
    "additionalProperties": False
}

DONATION_TRANSFER_SCHEMA = {
    "type": "object",
    "properties": {
        "request_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "donor_organization": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "donations": {
            "type": "array",
            "items": DONATION_TRANSFER_ITEM_SCHEMA,
            "minItems": 1,
            "maxItems": 100
        },
        "timestamp": {
            "type": "string",
            "format": "date-time"
        }
    },
    "required": ["request_id", "donor_organization", "donations", "timestamp"],
    "additionalProperties": False
}

DONATION_OFFER_SCHEMA = {
    "type": "object",
    "properties": {
        "offer_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "donor_organization": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "donations": {
            "type": "array",
            "items": DONATION_OFFER_ITEM_SCHEMA,
            "minItems": 1,
            "maxItems": 100
        },
        "timestamp": {
            "type": "string",
            "format": "date-time"
        }
    },
    "required": ["offer_id", "donor_organization", "donations", "timestamp"],
    "additionalProperties": False
}

REQUEST_CANCELLATION_SCHEMA = {
    "type": "object",
    "properties": {
        "organization_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "request_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "timestamp": {
            "type": "string",
            "format": "date-time"
        }
    },
    "required": ["organization_id", "request_id", "timestamp"],
    "additionalProperties": False
}

EXTERNAL_EVENT_SCHEMA = {
    "type": "object",
    "properties": {
        "organization_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "event_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255
        },
        "description": {
            "type": "string",
            "maxLength": 1000
        },
        "event_date": {
            "type": "string",
            "format": "date-time"
        },
        "timestamp": {
            "type": "string",
            "format": "date-time"
        }
    },
    "required": ["organization_id", "event_id", "name", "description", "event_date", "timestamp"],
    "additionalProperties": False
}

EVENT_CANCELLATION_SCHEMA = {
    "type": "object",
    "properties": {
        "organization_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "event_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "timestamp": {
            "type": "string",
            "format": "date-time"
        }
    },
    "required": ["organization_id", "event_id", "timestamp"],
    "additionalProperties": False
}

EVENT_ADHESION_SCHEMA = {
    "type": "object",
    "properties": {
        "event_id": {
            "type": "string",
            "minLength": 1,
            "maxLength": 100
        },
        "volunteer": VOLUNTEER_INFO_SCHEMA,
        "timestamp": {
            "type": "string",
            "format": "date-time"
        }
    },
    "required": ["event_id", "volunteer", "timestamp"],
    "additionalProperties": False
}

# Schema registry for easy access
SCHEMAS = {
    'donation_request': DONATION_REQUEST_SCHEMA,
    'donation_transfer': DONATION_TRANSFER_SCHEMA,
    'donation_offer': DONATION_OFFER_SCHEMA,
    'request_cancellation': REQUEST_CANCELLATION_SCHEMA,
    'external_event': EXTERNAL_EVENT_SCHEMA,
    'event_cancellation': EVENT_CANCELLATION_SCHEMA,
    'event_adhesion': EVENT_ADHESION_SCHEMA
}

class MessageValidator:
    """Message validator class for validating Kafka messages"""
    
    @staticmethod
    def validate_message(message_type: str, data: Dict[str, Any]) -> bool:
        """
        Validate message data against its schema
        
        Args:
            message_type: Type of message to validate
            data: Message data to validate
            
        Returns:
            True if valid, raises ValidationError if invalid
        """
        if message_type not in SCHEMAS:
            raise ValueError(f"Unknown message type: {message_type}")
        
        schema = SCHEMAS[message_type]
        
        try:
            validate(instance=data, schema=schema)
            return True
        except ValidationError as e:
            raise ValidationError(f"Message validation failed for {message_type}: {e.message}")
    
    @staticmethod
    def get_schema(message_type: str) -> Dict[str, Any]:
        """Get schema for a specific message type"""
        if message_type not in SCHEMAS:
            raise ValueError(f"Unknown message type: {message_type}")
        return SCHEMAS[message_type]
    
    @staticmethod
    def get_all_schemas() -> Dict[str, Dict[str, Any]]:
        """Get all available schemas"""
        return SCHEMAS.copy()