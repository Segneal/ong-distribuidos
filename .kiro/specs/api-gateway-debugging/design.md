# Design Document

## Overview

El problema identificado es que el API Gateway devuelve errores 501 (UNIMPLEMENTED) cuando se accede a los endpoints de inventario y eventos, a pesar de que los servicios gRPC funcionan correctamente de forma aislada. El diseño de la solución se enfoca en diagnosticar y corregir los problemas de comunicación entre el API Gateway y los servicios gRPC.

## Architecture

### Current Architecture
```
Frontend (React) → API Gateway (Node.js) → gRPC Services (Python)
                      ↓ (Error 501)
                   Inventory Service (Port 50052)
                   Events Service (Port 50053)
```

### Problem Analysis
1. **gRPC Services**: Funcionan correctamente (verificado con pruebas directas)
2. **API Gateway gRPC Clients**: Funcionan correctamente (verificado con simulación)
3. **HTTP Server**: Devuelve error 501 cuando se ejecuta como servidor

## Components and Interfaces

### 1. gRPC Client Configuration
- **Location**: `api-gateway/src/services/grpcClients.js`
- **Issue**: Posible problema con la configuración de métodos o conexiones
- **Solution**: Verificar y corregir la configuración de clientes gRPC

### 2. Route Handlers
- **Location**: `api-gateway/src/routes/inventory.js`, `api-gateway/src/routes/events.js`
- **Issue**: Posible problema en el manejo de rutas o middleware
- **Solution**: Verificar que las rutas estén correctamente configuradas

### 3. Error Handling
- **Location**: `api-gateway/src/middleware/errorHandler.js`
- **Issue**: Error 501 sugiere que el método no está implementado
- **Solution**: Revisar el mapeo de errores gRPC a HTTP

### 4. Server Configuration
- **Location**: `api-gateway/src/server.js`
- **Issue**: Posible problema en la configuración del servidor Express
- **Solution**: Verificar que las rutas estén correctamente montadas

## Data Models

### gRPC Request/Response Flow
```
HTTP Request → Route Handler → gRPC Transformer → gRPC Client → gRPC Service
HTTP Response ← Route Handler ← gRPC Transformer ← gRPC Client ← gRPC Service
```

### Error Mapping
- gRPC Code 12 (UNIMPLEMENTED) → HTTP 501
- gRPC Code 14 (UNAVAILABLE) → HTTP 503
- gRPC Code 5 (NOT_FOUND) → HTTP 404

## Error Handling

### Diagnostic Strategy
1. **Step 1**: Verificar que el API Gateway esté usando la versión correcta del código
2. **Step 2**: Revisar los logs del API Gateway durante las peticiones HTTP
3. **Step 3**: Verificar la configuración de rutas y middleware
4. **Step 4**: Comprobar la configuración de clientes gRPC en tiempo de ejecución

### Error Recovery
1. **Service Restart**: Reiniciar el API Gateway para cargar la configuración actualizada
2. **Configuration Validation**: Validar que las URLs y puertos de servicios sean correctos
3. **Connection Testing**: Implementar health checks reales para los servicios gRPC

## Testing Strategy

### Unit Tests
- Probar transformadores gRPC de forma aislada
- Probar clientes gRPC de forma aislada
- Probar route handlers con mocks

### Integration Tests
- Probar flujo completo HTTP → gRPC → HTTP
- Probar manejo de errores en cada capa
- Probar autenticación y autorización

### Manual Testing
- Probar endpoints con herramientas como curl o Postman
- Verificar logs del servidor durante las pruebas
- Probar desde el frontend para validar la experiencia del usuario

## Implementation Plan

### Phase 1: Diagnosis
1. Revisar logs del API Gateway en tiempo real
2. Verificar configuración de rutas y middleware
3. Comprobar que los clientes gRPC estén correctamente inicializados

### Phase 2: Fix Implementation
1. Corregir problemas identificados en la configuración
2. Actualizar manejo de errores si es necesario
3. Reiniciar servicios con configuración corregida

### Phase 3: Validation
1. Probar todos los endpoints de inventario y eventos
2. Verificar funcionalidad desde el frontend
3. Implementar health checks mejorados