# Donation Requests Implementation

This document describes the implementation of donation request functionality for the ONG Network Messaging System.

## Overview

The donation request system allows organizations in the network to:
- Create and publish donation requests to other organizations
- Receive and process external donation requests
- Cancel their own requests and handle cancellations from others
- Maintain audit logs of all messaging activities

## Architecture

### Components

1. **DonationRequestProducer** (`src/donation_request_producer.py`)
   - Creates and publishes donation requests to Kafka topic `/solicitud-donaciones`
   - Validates donation items and integrates with local database
   - Handles request cancellations via `/baja-solicitud-donaciones` topic

2. **DonationRequestConsumer** (`src/donation_request_consumer.py`)
   - Processes external donation requests from other organizations
   - Filters out own organization's messages
   - Stores external requests in `solicitudes_externas` table

3. **RequestCancellationConsumer** (`src/request_cancellation_consumer.py`)
   - Handles cancellation messages from other organizations
   - Updates external request status to inactive
   - Maintains audit trail of cancellations

4. **HTTP API Server** (`src/api_server.py`)
   - Provides REST endpoints for API Gateway integration
   - Runs on port 8000 alongside main messaging service (port 50054)

### Database Schema

#### Own Donation Requests
```sql
CREATE TABLE solicitudes_donaciones (
    id SERIAL PRIMARY KEY,
    solicitud_id VARCHAR(100) UNIQUE NOT NULL,
    donaciones JSONB NOT NULL,
    estado VARCHAR(20) DEFAULT 'ACTIVA',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER REFERENCES usuarios(id)
);
```

#### External Donation Requests
```sql
CREATE TABLE solicitudes_externas (
    id SERIAL PRIMARY KEY,
    organizacion_solicitante VARCHAR(100) NOT NULL,
    solicitud_id VARCHAR(100) NOT NULL,
    donaciones JSONB NOT NULL,
    activa BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### API Gateway Routes (`/api/donation-requests`)

- `POST /` - Create new donation request
- `GET /` - List own active donation requests  
- `DELETE /:requestId` - Cancel donation request
- `GET /external` - List external donation requests

### Messaging Service HTTP API (port 8000)

- `POST /api/createDonationRequest` - Create donation request
- `POST /api/getActiveRequests` - Get active requests
- `POST /api/cancelDonationRequest` - Cancel request
- `POST /api/getExternalRequests` - Get external requests
- `GET /health` - Health check

## Message Formats

### Donation Request Message
```json
{
  "organization_id": "empuje-comunitario",
  "request_id": "REQ-20250926-ABC123",
  "donations": [
    {
      "category": "ALIMENTOS",
      "description": "Conservas de atún"
    },
    {
      "category": "ROPA", 
      "description": "Ropa de abrigo para niños"
    }
  ],
  "timestamp": "2025-09-26T10:30:00Z"
}
```

### Request Cancellation Message
```json
{
  "organization_id": "empuje-comunitario",
  "request_id": "REQ-20250926-ABC123",
  "timestamp": "2025-09-26T11:00:00Z"
}
```

## Kafka Topics

- `/solicitud-donaciones` - Network-wide donation requests
- `/baja-solicitud-donaciones` - Network-wide request cancellations

## Usage Examples

### Creating a Donation Request (API Gateway)
```bash
curl -X POST http://localhost:3000/api/donation-requests \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "donations": [
      {
        "category": "ALIMENTOS",
        "description": "Conservas variadas"
      }
    ],
    "notes": "Urgente para evento del fin de semana"
  }'
```

### Getting External Requests
```bash
curl -X GET http://localhost:3000/api/donation-requests/external \
  -H "Authorization: Bearer <token>"
```

### Canceling a Request
```bash
curl -X DELETE http://localhost:3000/api/donation-requests/REQ-20250926-ABC123 \
  -H "Authorization: Bearer <token>"
```

## Validation

### Donation Categories
- `ROPA` - Clothing items
- `ALIMENTOS` - Food items  
- `JUGUETES` - Toys
- `UTILES_ESCOLARES` - School supplies

### Required Fields
- `category` - Must be one of the valid categories
- `description` - Non-empty string, max 255 characters

## Error Handling

- Invalid donation categories are rejected
- Missing required fields cause validation errors
- Database connection failures are logged and handled gracefully
- Kafka publishing failures trigger rollback of database changes
- All errors are logged with structured logging for debugging

## Security

- All API endpoints require authentication via JWT tokens
- Only PRESIDENTE and VOCAL roles can create/cancel donation requests
- Message validation prevents malformed data from being processed
- Database operations use parameterized queries to prevent SQL injection

## Monitoring

- Health check endpoint at `/health` reports system status
- All message processing is logged to `historial_mensajes` table
- Structured logging provides detailed operation traces
- Kafka consumer status is monitored and reported

## Testing

Run structure verification:
```bash
cd messaging-service
python verify_structure.py
```

Run unit tests (requires dependencies):
```bash
cd messaging-service
python src/test_donation_requests.py
```

## Deployment

The system is deployed via Docker Compose:

```bash
docker-compose up messaging-service
```

The messaging service will:
1. Wait for Kafka and PostgreSQL to be ready
2. Initialize database tables if needed
3. Start HTTP API server on port 8000
4. Start main messaging service on port 50054
5. Begin consuming messages from network topics

## Requirements Compliance

This implementation satisfies the following requirements:

- **1.1**: ✅ Donation request creation and publishing
- **1.2**: ✅ Integration with inventory service for validation  
- **1.3**: ✅ External request processing and storage
- **1.4**: ✅ Message filtering and format validation
- **4.1**: ✅ Request cancellation publishing
- **4.2**: ✅ External cancellation processing
- **4.3**: ✅ Database status updates
- **4.4**: ✅ Complete audit trail maintenance