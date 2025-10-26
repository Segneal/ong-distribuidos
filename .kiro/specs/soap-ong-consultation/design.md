# Design Document - SOAP ONG Consultation Feature

## Overview

This document outlines the design for the SOAP consultation feature that allows President users to query information about other NGOs and their presidents from an external SOAP service. **The feature is already extensively implemented** with a complete SOAP client, REST API endpoints, GraphQL integration, and a React frontend component.

The system leverages a comprehensive SOAP client infrastructure in the reports service and provides a polished frontend interface integrated into the Reports page.

## Architecture

### Current Implementation Status

✅ **FULLY IMPLEMENTED**: The SOAP consultation feature is complete with:

```
Frontend (React + GraphQL) → API Gateway → Reports Service → External SOAP Service
```

### Component Interaction Flow

1. **Frontend Component**: ✅ `NetworkConsultation.jsx` - Complete React component with Material-UI
2. **GraphQL Integration**: ✅ Apollo Client with GraphQL queries for SOAP operations
3. **API Gateway**: ✅ Proxy routes configured for reports service
4. **Reports Service**: ✅ Complete SOAP client, service layer, and REST endpoints
5. **External SOAP Service**: ✅ Integration with https://soap-app-latest.onrender.com

### Technology Stack

- **Frontend**: ✅ React 18.2.0 with Material-UI components and Apollo GraphQL
- **API Gateway**: ✅ Node.js/Express proxy layer configured
- **Backend**: ✅ FastAPI (reports service) with complete SOAP implementation
- **SOAP Client**: ✅ Python `requests` library with custom XML parsing
- **Authentication**: ✅ JWT tokens with role-based access control

## Components and Interfaces

### 1. Frontend Components (✅ FULLY IMPLEMENTED)

#### NetworkConsultation Component
- **Location**: ✅ `frontend/src/components/reports/NetworkConsultation.jsx`
- **Status**: **FULLY IMPLEMENTED**
- **Features**:
  - ✅ Organization ID input field (comma-separated)
  - ✅ Submit button to trigger SOAP queries via GraphQL
  - ✅ Results display with accordion layout
  - ✅ Loading states and error handling
  - ✅ Input validation for numeric IDs
  - ✅ SOAP connection status indicator
  - ✅ Clear functionality
  - ✅ Separate tables for organizations and presidents
  - ✅ Summary statistics display
  - ✅ Material-UI components with responsive design
  - ✅ Error alerts and warnings display

#### GraphQL Integration
- **Status**: **FULLY IMPLEMENTED**
- **Queries**:
  - ✅ `NETWORK_CONSULTATION_QUERY` - Main consultation query
  - ✅ `SOAP_CONNECTION_TEST_QUERY` - Connection status check
- **Features**:
  - ✅ Apollo Client integration
  - ✅ Lazy query execution
  - ✅ Error handling and loading states
  - ✅ Real-time connection status

#### Integration Status
- **Location**: ✅ `frontend/src/pages/Reports.jsx`
- **Status**: **FULLY INTEGRATED**
- **Features**:
  - ✅ Integrated as "Consulta de Red" tab in Reports page
  - ✅ Role-based access control (President only)
  - ✅ Tab-based navigation with icons
  - ✅ Responsive layout with proper permissions

### 2. API Gateway Integration (✅ IMPLEMENTED)

#### Route Configuration Status
- **Endpoint**: ✅ `/api/network/*` (via reports service proxy)
- **Methods**: ✅ POST, GET
- **Purpose**: ✅ Proxy SOAP consultation requests to reports service
- **Authentication**: ✅ JWT token validation with President role requirement

#### Current Implementation
- **Status**: **FULLY IMPLEMENTED**
- **Location**: ✅ API Gateway proxies requests to reports service
- **Features**:
  - ✅ Authentication middleware
  - ✅ Role-based access control
  - ✅ Request proxying to reports service
  - ✅ Error handling and response forwarding

### 3. Reports Service Implementation (✅ FULLY IMPLEMENTED)

#### REST API Endpoints Status

##### ✅ POST /api/network/consultation
- **Status**: **FULLY IMPLEMENTED**
- **Location**: `reports-service/src/rest/routes/network_consultation.py`
- **Features**:
  - ✅ Complete request/response handling
  - ✅ Input validation (max 50 organizations)
  - ✅ Role-based authentication (President only)
  - ✅ Error handling with detailed messages
  - ✅ Comprehensive logging
  - ✅ Pydantic model validation

##### ✅ GET /api/network/presidents/{organization_id}
- **Status**: **FULLY IMPLEMENTED**
- **Purpose**: Query individual president data
- **Features**: ✅ Single organization president lookup

##### ✅ GET /api/network/organizations/{organization_id}
- **Status**: **FULLY IMPLEMENTED**
- **Purpose**: Query individual organization data
- **Features**: ✅ Single organization data lookup

##### ✅ GET /api/network/test-connection
- **Status**: **FULLY IMPLEMENTED**
- **Purpose**: Test SOAP service connectivity
- **Features**: ✅ Connection health check

#### SOAP Client Implementation (✅ COMPLETE)
**Location**: `reports-service/src/soap/client.py`
- ✅ `SOAPClient` class with full functionality
- ✅ `get_president_data()` method for list_presidents SOAP operation
- ✅ `get_organization_data()` method for list_associations SOAP operation
- ✅ `get_combined_data()` method for parallel queries
- ✅ Proper XML parsing with namespace handling
- ✅ Authentication header management (GrupoA-TM/clave-tm-a)
- ✅ Error handling and logging
- ✅ Connection testing capabilities
- ✅ Request timeout handling

#### Service Layer (✅ COMPLETE)
**Location**: `reports-service/src/services/soap_service.py`
- ✅ `SOAPService` class with business logic
- ✅ Data validation and transformation
- ✅ Error handling and recovery
- ✅ Pydantic model integration
- ✅ Async operation support

#### Data Models (✅ COMPLETE)
**Location**: `reports-service/src/soap/schemas.py`
- ✅ `PresidentData` - President information model
- ✅ `OrganizationData` - Organization information model
- ✅ `NetworkConsultationRequest` - Request validation model
- ✅ `NetworkConsultationResponse` - Response structure model
- ✅ `SOAPErrorResponse` - Error handling model

## Data Models

### Frontend Data Models (✅ IMPLEMENTED)

#### GraphQL Query Variables
```typescript
interface NetworkConsultationVariables {
  organizationIds: number[];
}
```

#### GraphQL Response Types
```typescript
interface NetworkConsultationData {
  networkConsultation: {
    presidents: PresidentData[];
    organizations: OrganizationData[];
    queryIds: number[];
    totalPresidents: number;
    totalOrganizations: number;
    errors: string[];
  };
}
```

### Backend Data Models (✅ IMPLEMENTED)
The Pydantic models in `reports-service/src/soap/schemas.py` provide:
- ✅ `PresidentData` with all required fields
- ✅ `OrganizationData` with comprehensive organization info
- ✅ `NetworkConsultationRequest` with validation
- ✅ `NetworkConsultationResponse` with complete response structure

## Error Handling

### Frontend Error Handling (✅ IMPLEMENTED)
1. **Input Validation Errors**:
   - ✅ Empty input validation with user alerts
   - ✅ Non-numeric ID validation with real-time feedback
   - ✅ Inline error messages display

2. **API Errors**:
   - ✅ Network connectivity issues handling
   - ✅ SOAP service unavailable notifications
   - ✅ Authentication/authorization error display
   - ✅ User-friendly error messages with Material-UI alerts

3. **Data Processing Errors**:
   - ✅ Partial data scenarios handling
   - ✅ Missing president or organization data warnings
   - ✅ Error list display in consultation results

### Backend Error Handling (✅ IMPLEMENTED)
1. **SOAP Service Errors**:
   - ✅ Connection timeouts with retry logic
   - ✅ Authentication failures with detailed messages
   - ✅ Invalid response format handling
   - ✅ Appropriate HTTP status codes (503, 500, 400)

2. **Data Validation Errors**:
   - ✅ Invalid organization IDs validation
   - ✅ Malformed request handling
   - ✅ 400 Bad Request responses with details

3. **System Errors**:
   - ✅ Internal server error handling
   - ✅ Comprehensive logging for debugging
   - ✅ 500 Internal Server Error responses

## Security Considerations

### Authentication and Authorization (✅ IMPLEMENTED)
- ✅ **Role-based Access**: Only President users can access SOAP consultation
- ✅ **JWT Token Validation**: All requests require valid JWT tokens
- ✅ **Session Management**: Leverages existing authentication system
- ✅ **GraphQL Security**: Proper query validation and authorization

### Data Security (✅ IMPLEMENTED)
- ✅ **SOAP Credentials**: Authentication credentials properly configured
- ✅ **Request Logging**: Comprehensive logging for audit purposes
- ✅ **Rate Limiting**: Request size limits (max 50 organizations per request)

### Input Validation (✅ IMPLEMENTED)
- ✅ **Organization ID Validation**: Only numeric IDs accepted
- ✅ **Request Size Limits**: Maximum 50 organization IDs per request
- ✅ **Pydantic Validation**: Server-side request validation

## Performance Considerations

### Current Implementation (✅ OPTIMIZED)
- ✅ **Parallel Processing**: President and organization SOAP calls made in parallel
- ✅ **Request Deduplication**: Duplicate organization IDs automatically removed
- ✅ **Async Processing**: FastAPI async endpoints for non-blocking operations
- ✅ **Connection Reuse**: HTTP connection pooling for SOAP requests

### Monitoring and Logging (✅ IMPLEMENTED)
- ✅ **Response Time Monitoring**: Comprehensive logging of SOAP response times
- ✅ **Error Rate Monitoring**: SOAP service availability tracking
- ✅ **Usage Analytics**: Request logging for usage pattern analysis

## Testing Strategy

### Current Testing Capabilities

#### Frontend Testing (Available)
- **Component Testing**: React Testing Library setup available
- **GraphQL Testing**: Apollo Client MockedProvider for testing
- **User Interaction Testing**: Material-UI component testing

#### Backend Testing (Available)
- **SOAP Client Testing**: Existing test infrastructure with pytest
- **API Endpoint Testing**: FastAPI TestClient available
- **Data Transformation Testing**: Pydantic model validation testing

#### Integration Testing (Available)
- **End-to-End Flow**: Complete flow testing capability
- **Authentication Testing**: Role-based access control testing
- **SOAP Service Integration**: Live service testing capability

## Deployment Considerations

### Environment Configuration (✅ CONFIGURED)
- ✅ **SOAP Service URL**: External SOAP service endpoint configured
- ✅ **Authentication Credentials**: SOAP authentication details properly set
- ✅ **Service Discovery**: API Gateway routing to reports service configured

### Monitoring and Alerting (✅ AVAILABLE)
- ✅ **Health Checks**: SOAP connectivity health check endpoints
- ✅ **Error Logging**: Comprehensive error logging and tracking
- ✅ **Performance Monitoring**: Response time and success rate monitoring

## Current Status Summary

### ✅ FULLY IMPLEMENTED FEATURES
1. **Complete SOAP Client** - Full XML parsing and SOAP operations
2. **REST API Endpoints** - All required endpoints with validation
3. **GraphQL Integration** - Frontend GraphQL queries and mutations
4. **React Frontend Component** - Polished UI with Material-UI
5. **Authentication & Authorization** - Role-based access control
6. **Error Handling** - Comprehensive error management
7. **Data Models** - Complete Pydantic and TypeScript models
8. **Integration** - Fully integrated into Reports page

### 🔧 POTENTIAL IMPROVEMENTS
1. **Caching**: Could implement Redis-based caching for SOAP responses
2. **Export Functionality**: Could add Excel/PDF export of consultation results
3. **Advanced Filtering**: Could add filtering by organization type or region
4. **Bulk Operations**: Could support larger organization ID lists with background processing

### 🚀 READY FOR USE
The SOAP consultation feature is **fully functional and ready for production use**. All requirements from the specification have been implemented with a comprehensive, user-friendly interface and robust backend infrastructure.