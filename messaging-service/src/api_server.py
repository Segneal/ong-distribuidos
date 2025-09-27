"""
HTTP API Server for Messaging Service
Provides REST endpoints for donation request operations
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import structlog
import traceback

from .donation_request_producer import DonationRequestProducer
from .database import test_database_connection, initialize_database_tables
from .config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize producer
donation_producer = DonationRequestProducer()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_healthy = test_database_connection()
        
        # Test Kafka connection (basic check)
        kafka_healthy = True  # TODO: Add Kafka health check
        
        status = "healthy" if db_healthy and kafka_healthy else "unhealthy"
        
        return jsonify({
            "status": status,
            "database": "healthy" if db_healthy else "unhealthy",
            "kafka": "healthy" if kafka_healthy else "unhealthy",
            "organization_id": settings.organization_id
        }), 200 if status == "healthy" else 503
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503


@app.route('/api/createDonationRequest', methods=['POST'])
def create_donation_request():
    """Create a new donation request"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        donations = data.get('donations', [])
        user_id = data.get('userId')
        notes = data.get('notes')
        
        logger.info(
            "Creating donation request via API",
            donations_count=len(donations),
            user_id=user_id
        )
        
        # Validate donations
        if not donations or not isinstance(donations, list):
            return jsonify({
                "success": False,
                "error": "Donations list is required"
            }), 400
        
        # Create donation request
        result = donation_producer.create_donation_request(donations, user_id)
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(
            "Error in create_donation_request API",
            error=str(e),
            traceback=traceback.format_exc()
        )
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@app.route('/api/getActiveRequests', methods=['POST'])
def get_active_requests():
    """Get all active donation requests"""
    try:
        logger.info("Getting active donation requests via API")
        
        requests = donation_producer.get_active_requests()
        
        return jsonify({
            "success": True,
            "requests": requests
        }), 200
        
    except Exception as e:
        logger.error(
            "Error in get_active_requests API",
            error=str(e),
            traceback=traceback.format_exc()
        )
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@app.route('/api/cancelDonationRequest', methods=['POST'])
def cancel_donation_request():
    """Cancel a donation request"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        request_id = data.get('requestId')
        user_id = data.get('userId')
        
        if not request_id:
            return jsonify({
                "success": False,
                "error": "Request ID is required"
            }), 400
        
        logger.info(
            "Canceling donation request via API",
            request_id=request_id,
            user_id=user_id
        )
        
        result = donation_producer.cancel_donation_request(request_id, user_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(
            "Error in cancel_donation_request API",
            error=str(e),
            traceback=traceback.format_exc()
        )
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@app.route('/api/getExternalRequests', methods=['POST'])
def get_external_requests():
    """Get external donation requests from other organizations"""
    try:
        data = request.get_json() or {}
        active_only = data.get('activeOnly', True)
        
        logger.info("Getting external donation requests via API", active_only=active_only)
        
        from .donation_request_consumer import DonationRequestConsumer
        consumer = DonationRequestConsumer()
        
        requests = consumer.get_external_requests(active_only=active_only)
        
        return jsonify({
            "success": True,
            "requests": requests
        }), 200
        
    except Exception as e:
        logger.error(
            "Error in get_external_requests API",
            error=str(e),
            traceback=traceback.format_exc()
        )
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error("Internal server error", error=str(error))
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


def create_app():
    """Application factory"""
    try:
        # Initialize database tables
        initialize_database_tables()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        # Don't fail startup, but log the error
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = 8000  # Fixed port for HTTP API
    
    logger.info(
        "Starting messaging service HTTP API",
        port=port,
        organization_id=settings.organization_id
    )
    
    app.run(host='0.0.0.0', port=port, debug=False)