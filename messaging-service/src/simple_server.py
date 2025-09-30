#!/usr/bin/env python3
"""
Simplified Messaging Service for local development (without Kafka)
"""
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="ONG Messaging Service (Simplified)", version="1.0.0")

@app.get("/health")
async def health_check():
    return {"status": "OK", "service": "Messaging Service", "mode": "simplified"}

@app.post("/api/createDonationRequest")
async def create_donation_request(request: dict):
    """Create a donation request (simplified)"""
    return {
        "success": True,
        "message": "Donation request created successfully (simplified mode)",
        "request_id": f"req_{hash(str(request)) % 10000}"
    }

@app.post("/api/createDonationOffer")
async def create_donation_offer(request: dict):
    """Create a donation offer (simplified)"""
    return {
        "success": True,
        "message": "Donation offer created successfully (simplified mode)",
        "offer_id": f"offer_{hash(str(request)) % 10000}"
    }

@app.post("/api/getActiveRequests")
async def get_active_requests():
    """Get active donation requests (simplified)"""
    return {
        "success": True,
        "requests": []
    }

@app.post("/api/getExternalRequests")
async def get_external_requests():
    """Get external donation requests (simplified)"""
    return {
        "success": True,
        "requests": []
    }

@app.post("/api/transferDonations")
async def transfer_donations(request: dict):
    """Transfer donations (simplified)"""
    return {
        "success": True,
        "message": "Donations transferred successfully (simplified mode)",
        "transfer_id": f"transfer_{hash(str(request)) % 10000}"
    }

@app.post("/api/getTransferHistory")
async def get_transfer_history():
    """Get transfer history (simplified)"""
    return {
        "success": True,
        "transfers": []
    }

@app.post("/api/publishEvent")
async def publish_event(request: dict):
    """Publish solidarity event (simplified)"""
    return {
        "success": True,
        "message": "Event published successfully (simplified mode)",
        "event_id": request.get("eventId", "unknown")
    }

@app.post("/api/createEventAdhesion")
async def create_event_adhesion(request: dict):
    """Create event adhesion (simplified)"""
    return {
        "success": True,
        "message": "Event adhesion created successfully (simplified mode)",
        "adhesion_id": f"adhesion_{hash(str(request)) % 10000}"
    }

@app.post("/api/getVolunteerAdhesions")
async def get_volunteer_adhesions(request: dict):
    """Get volunteer adhesions (simplified)"""
    return {
        "success": True,
        "adhesions": []
    }

@app.post("/api/getEventAdhesions")
async def get_event_adhesions(request: dict):
    """Get event adhesions (simplified)"""
    return {
        "success": True,
        "adhesions": []
    }

def serve():
    """Start the simplified messaging service"""
    port = int(os.getenv('HTTP_PORT', '8000'))
    
    print(f"🚀 Messaging Service (Simplified) iniciado en puerto {port}")
    print(f"📊 Escuchando en http://localhost:{port}")
    print("⚠️  Modo simplificado - Sin Kafka")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == '__main__':
    serve()