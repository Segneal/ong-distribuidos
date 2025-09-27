import asyncio
import signal
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import structlog
import uvicorn

from .config import settings, Topics
from .kafka_connection import kafka_manager
from .base_producer import BaseProducer
from .base_consumer import NetworkConsumer, OrganizationConsumer

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
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.service_port,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()