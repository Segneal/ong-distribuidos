"""
HTTP API Server for Messaging Service
Provides REST endpoints for donation request operations
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import structlog
import traceback

from ..producers.donation_producer import DonationRequestProducer
from ..services.transfer_service import TransferService
from ..services.offer_service import OfferService
from ..database.connection import test_database_connection
from ..config import settings

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

# Initialize services
donation_producer = DonationRequestProducer()
transfer_service = TransferService()
offer_service = OfferService()


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
        user_organization = data.get('userOrganization')
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
        result = donation_producer.create_donation_request(donations, user_id, user_organization)
        
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
        
        from ..consumers.donation_consumer import DonationRequestConsumer
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


@app.route('/api/transferDonations', methods=['POST'])
def transfer_donations():
    """Transfer donations to another organization"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        target_org = data.get('targetOrganization')
        request_id = data.get('requestId')
        donations = data.get('donations', [])
        user_id = data.get('userId')
        
        # Validate required fields
        if not target_org:
            return jsonify({
                "success": False,
                "error": "Target organization is required"
            }), 400
        
        if not request_id:
            return jsonify({
                "success": False,
                "error": "Request ID is required"
            }), 400
        
        if not donations or not isinstance(donations, list):
            return jsonify({
                "success": False,
                "error": "Donations list is required"
            }), 400
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "User ID is required"
            }), 400
        
        logger.info(
            "Processing donation transfer via API",
            target_org=target_org,
            request_id=request_id,
            donations_count=len(donations),
            user_id=user_id
        )
        
        # Execute transfer
        success, message = transfer_service.transfer_donations(
            target_org, request_id, donations, user_id
        )
        
        if success:
            return jsonify({
                "success": True,
                "message": message
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": message
            }), 400
            
    except Exception as e:
        logger.error(
            "Error in transfer_donations API",
            error=str(e),
            traceback=traceback.format_exc()
        )
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@app.route('/api/getTransferHistory', methods=['POST'])
def get_transfer_history():
    """Get transfer history"""
    try:
        data = request.get_json() or {}
        organization_id = data.get('organizationId')
        limit = data.get('limit', 50)
        
        logger.info(
            "Getting transfer history via API",
            organization_id=organization_id,
            limit=limit
        )
        
        transfers = transfer_service.get_transfer_history(organization_id, limit)
        
        return jsonify({
            "success": True,
            "transfers": transfers
        }), 200
        
    except Exception as e:
        logger.error(
            "Error in get_transfer_history API",
            error=str(e),
            traceback=traceback.format_exc()
        )
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@app.route('/api/createDonationOffer', methods=['POST'])
def create_donation_offer():
    """Create a new donation offer"""
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
            "Creating donation offer via API",
            donations_count=len(donations),
            user_id=user_id
        )
        
        # Validate donations
        if not donations or not isinstance(donations, list):
            return jsonify({
                "success": False,
                "error": "Donations list is required"
            }), 400
        
        # Validate user_id
        if not user_id:
            return jsonify({
                "success": False,
                "error": "User ID is required"
            }), 400
        
        # Create donation offer
        success, message, offer_id = offer_service.create_donation_offer(donations, user_id, notes)
        
        if success:
            return jsonify({
                "success": True,
                "message": message,
                "offer_id": offer_id
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": message
            }), 400
            
    except Exception as e:
        logger.error(
            "Error in create_donation_offer API",
            error=str(e),
            traceback=traceback.format_exc()
        )
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@app.route('/api/getExternalOffers', methods=['POST'])
def get_external_offers():
    """Get external donation offers from other organizations"""
    try:
        data = request.get_json() or {}
        active_only = data.get('activeOnly', True)
        
        logger.info("Getting external donation offers via API", active_only=active_only)
        
        offers = offer_service.get_external_offers(active_only=active_only)
        
        return jsonify({
            "success": True,
            "offers": offers
        }), 200
        
    except Exception as e:
        logger.error(
            "Error in get_external_offers API",
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
    # Database initialization can be handled separately
    logger.info("API server created")
    
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