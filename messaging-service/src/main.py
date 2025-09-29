#!/usr/bin/env python3
"""
Main entry point for the ONG Network Messaging Service
"""
import asyncio
import signal
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import structlog
import uvicorn

from messaging.config import settings, Topics
from messaging.kafka.connection import kafka_manager
from messaging.producers.base_producer import BaseProducer
from messaging.consumers.base_consumer import NetworkConsumer, OrganizationConsumer
from messaging.services.offer_service import OfferService

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

# Global instances
producer = BaseProducer()
network_consumer = NetworkConsumer()
org_consumer = OrganizationConsumer()
offer_service = OfferService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting messaging service", organization_id=settings.organization_id)
    
    try:
        # Initialize Kafka topics
        all_topics = [
            Topics.DONATION_REQUESTS,
            Topics.DONATION_OFFERS,
            Topics.REQUEST_CANCELLATIONS,
            Topics.SOLIDARITY_EVENTS,
            Topics.EVENT_CANCELLATIONS,
            Topics.get_transfer_topic(settings.organization_id),
            Topics.get_adhesion_topic(settings.organization_id)
        ]
        
        kafka_manager.create_topics_if_not_exist(all_topics)
        
        # Start consumers
        network_consumer.start()
        org_consumer.start()
        
        logger.info("Messaging service started successfully")
        
        yield
        
    except Exception as e:
        logger.error("Failed to start messaging service", error=str(e))
        raise
    finally:
        # Cleanup
        logger.info("Shutting down messaging service")
        network_consumer.stop()
        org_consumer.stop()
        kafka_manager.close_connections()
        logger.info("Messaging service shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="ONG Network Messaging Service",
    description="Kafka-based messaging service for ONG network collaboration",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    kafka_health = kafka_manager.health_check()
    
    return {
        "status": "healthy" if kafka_health["status"] == "healthy" else "unhealthy",
        "service": "messaging-service",
        "organization_id": settings.organization_id,
        "kafka": kafka_health,
        "consumers": {
            "network_consumer": network_consumer.is_running(),
            "organization_consumer": org_consumer.is_running()
        }
    }


@app.get("/status")
async def get_status():
    """Get detailed service status"""
    return {
        "service": "messaging-service",
        "organization_id": settings.organization_id,
        "kafka_connection": kafka_manager.connection_status,
        "kafka_brokers": settings.kafka_bootstrap_servers,
        "consumers": {
            "network_consumer": {
                "running": network_consumer.is_running(),
                "topics": network_consumer.topics
            },
            "organization_consumer": {
                "running": org_consumer.is_running(),
                "topics": org_consumer.topics
            }
        },
        "topics": {
            "donation_requests": Topics.DONATION_REQUESTS,
            "donation_offers": Topics.DONATION_OFFERS,
            "request_cancellations": Topics.REQUEST_CANCELLATIONS,
            "solidarity_events": Topics.SOLIDARITY_EVENTS,
            "event_cancellations": Topics.EVENT_CANCELLATIONS,
            "donation_transfers": Topics.get_transfer_topic(settings.organization_id),
            "event_adhesions": Topics.get_adhesion_topic(settings.organization_id)
        }
    }


@app.post("/test/publish")
async def test_publish(message_type: str, data: dict):
    """Test endpoint for publishing messages"""
    try:
        if message_type == "donation_request":
            success = producer.publish_donation_request(
                request_id=data.get("request_id", "test-req-001"),
                donations=data.get("donations", [])
            )
        elif message_type == "donation_offer":
            success = producer.publish_donation_offer(
                offer_id=data.get("offer_id", "test-offer-001"),
                donations=data.get("donations", [])
            )
        elif message_type == "solidarity_event":
            success = producer.publish_event(
                event_id=data.get("event_id", "test-event-001"),
                event_data=data
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown message type: {message_type}")
        
        if success:
            return {"status": "success", "message": "Message published successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to publish message")
    
    except Exception as e:
        logger.error("Error in test publish", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/createDonationOffer")
async def create_donation_offer(data: dict):
    """Create a new donation offer"""
    try:
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
            raise HTTPException(status_code=400, detail="Donations list is required")
        
        # Validate user_id
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        # Create donation offer
        success, message, offer_id = offer_service.create_donation_offer(donations, user_id, notes)
        
        if success:
            return {
                "success": True,
                "message": message,
                "offer_id": offer_id
            }
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in create_donation_offer API", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/getExternalOffers")
async def get_external_offers(data: dict = None):
    """Get external donation offers from other organizations"""
    try:
        if data is None:
            data = {}
        
        active_only = data.get('activeOnly', True)
        
        logger.info("Getting external donation offers via API", active_only=active_only)
        
        offers = offer_service.get_external_offers(active_only=active_only)
        
        return {
            "success": True,
            "offers": offers
        }
        
    except Exception as e:
        logger.error("Error in get_external_offers API", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/publishEvent")
async def publish_event(data: dict):
    """Publish a solidarity event to the network"""
    try:
        from messaging.services.event_service import EventService
        
        event_id = data.get('eventId')
        name = data.get('name')
        description = data.get('description', '')
        event_date = data.get('eventDate')
        user_id = data.get('userId')
        
        logger.info(
            "Publishing solidarity event via API",
            event_id=event_id,
            name=name,
            event_date=event_date,
            user_id=user_id
        )
        
        # Validate required fields
        if not event_id:
            raise HTTPException(status_code=400, detail="Event ID is required")
        
        if not name:
            raise HTTPException(status_code=400, detail="Event name is required")
        
        if not event_date:
            raise HTTPException(status_code=400, detail="Event date is required")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        # Create event service and publish event
        event_service = EventService()
        success, message = event_service.publish_event(event_id, name, description, event_date, user_id)
        
        if success:
            return {
                "success": True,
                "message": message
            }
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in publish_event API", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/getExternalEvents")
async def get_external_events(data: dict = None):
    """Get external solidarity events from other organizations"""
    try:
        from messaging.services.event_service import EventService
        
        if data is None:
            data = {}
        
        active_only = data.get('activeOnly', True)
        
        logger.info("Getting external solidarity events via API", active_only=active_only)
        
        event_service = EventService()
        events = event_service.get_external_events(active_only=active_only)
        
        return {
            "success": True,
            "events": events
        }
        
    except Exception as e:
        logger.error("Error in get_external_events API", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/cancelEvent")
async def cancel_event(data: dict):
    """Cancel a solidarity event"""
    try:
        from messaging.services.event_service import EventService
        
        event_id = data.get('eventId')
        user_id = data.get('userId')
        
        logger.info(
            "Canceling solidarity event via API",
            event_id=event_id,
            user_id=user_id
        )
        
        # Validate required fields
        if not event_id:
            raise HTTPException(status_code=400, detail="Event ID is required")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        # Create event service and cancel event
        event_service = EventService()
        success, message = event_service.cancel_event(event_id, user_id)
        
        if success:
            return {
                "success": True,
                "message": message
            }
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in cancel_event API", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/createEventAdhesion")
async def create_event_adhesion(data: dict):
    """Create an adhesion to an external event"""
    try:
        from messaging.services.adhesion_service import AdhesionService
        
        event_id = data.get('eventId')
        volunteer_id = data.get('volunteerId')
        target_organization = data.get('targetOrganization')
        
        logger.info(
            "Creating event adhesion via API",
            event_id=event_id,
            volunteer_id=volunteer_id,
            target_organization=target_organization
        )
        
        # Validate required fields
        if not event_id:
            raise HTTPException(status_code=400, detail="Event ID is required")
        
        if not volunteer_id:
            raise HTTPException(status_code=400, detail="Volunteer ID is required")
        
        if not target_organization:
            raise HTTPException(status_code=400, detail="Target organization is required")
        
        # Create adhesion service and create adhesion
        adhesion_service = AdhesionService()
        success, message = adhesion_service.create_event_adhesion(
            event_id, volunteer_id, target_organization
        )
        
        if success:
            return {
                "success": True,
                "message": message
            }
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in create_event_adhesion API", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/getVolunteerAdhesions")
async def get_volunteer_adhesions(data: dict):
    """Get adhesions for a specific volunteer"""
    try:
        from messaging.services.adhesion_service import AdhesionService
        
        volunteer_id = data.get('volunteerId')
        
        logger.info(
            "Getting volunteer adhesions via API",
            volunteer_id=volunteer_id
        )
        
        # Validate required fields
        if not volunteer_id:
            raise HTTPException(status_code=400, detail="Volunteer ID is required")
        
        # Create adhesion service and get adhesions
        adhesion_service = AdhesionService()
        adhesions = adhesion_service.get_volunteer_adhesions(volunteer_id)
        
        return {
            "success": True,
            "adhesions": adhesions
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in get_volunteer_adhesions API", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/getEventAdhesions")
async def get_event_adhesions(data: dict):
    """Get adhesions for a specific event (for administrators)"""
    try:
        from messaging.services.adhesion_service import AdhesionService
        
        event_id = data.get('eventId')
        
        logger.info(
            "Getting event adhesions via API",
            event_id=event_id
        )
        
        # Validate required fields
        if not event_id:
            raise HTTPException(status_code=400, detail="Event ID is required")
        
        # Create adhesion service and get adhesions
        adhesion_service = AdhesionService()
        adhesions = adhesion_service.get_event_adhesions(event_id)
        
        return {
            "success": True,
            "adhesions": adhesions
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in get_event_adhesions API", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal", signal=signum)
    sys.exit(0)


def main():
    """Main entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Configure logging level
    logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
    
    logger.info(
        "Starting messaging service",
        organization_id=settings.organization_id,
        kafka_brokers=settings.kafka_bootstrap_servers,
        port=settings.service_port
    )
    
    # Run the service
    http_port = int(os.getenv("HTTP_PORT", "8000"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=http_port,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()