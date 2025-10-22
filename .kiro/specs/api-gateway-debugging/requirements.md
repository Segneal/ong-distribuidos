# Requirements Document

## Introduction

El sistema de gestión ONG tiene problemas en los módulos de eventos e inventario. Los servicios gRPC funcionan correctamente de forma aislada, pero el API Gateway devuelve errores 501 (UNIMPLEMENTED) cuando se accede a través de HTTP. Se requiere diagnosticar y corregir estos problemas para restaurar la funcionalidad completa del sistema.

## Glossary

- **API Gateway**: Servicio Node.js que actúa como punto de entrada HTTP y se comunica con los microservicios gRPC
- **Inventory Service**: Microservicio Python que maneja las donaciones del inventario
- **Events Service**: Microservicio Python que maneja los eventos de la organización
- **gRPC Client**: Cliente que se conecta a los servicios gRPC desde el API Gateway

## Requirements

### Requirement 1

**User Story:** Como desarrollador del sistema, quiero que el API Gateway se comunique correctamente con los servicios gRPC, para que los usuarios puedan acceder a las funcionalidades de inventario y eventos.

#### Acceptance Criteria

1. WHEN se realiza una petición GET a /api/inventory con autenticación válida, THE API Gateway SHALL devolver una respuesta exitosa con la lista de donaciones
2. WHEN se realiza una petición POST a /api/inventory con datos válidos, THE API Gateway SHALL crear una nueva donación exitosamente
3. WHEN se realiza una petición GET a /api/events con autenticación válida, THE API Gateway SHALL devolver una respuesta exitosa con la lista de eventos
4. WHEN se realiza una petición POST a /api/events con datos válidos, THE API Gateway SHALL crear un nuevo evento exitosamente

### Requirement 2

**User Story:** Como administrador del sistema, quiero que los errores de comunicación gRPC sean manejados apropiadamente, para que pueda diagnosticar problemas de conectividad.

#### Acceptance Criteria

1. WHEN un servicio gRPC no está disponible, THE API Gateway SHALL devolver un error HTTP 503 con un mensaje descriptivo
2. WHEN hay un error de comunicación gRPC, THE API Gateway SHALL registrar el error en los logs con detalles suficientes para debugging
3. WHEN se consulta el endpoint /health, THE API Gateway SHALL mostrar el estado real de conectividad con cada servicio gRPC

### Requirement 3

**User Story:** Como usuario del sistema, quiero que las operaciones de inventario y eventos funcionen correctamente desde el frontend, para que pueda gestionar las donaciones y eventos de la organización.

#### Acceptance Criteria

1. WHEN accedo al módulo de inventario desde el frontend, THE system SHALL mostrar la lista de donaciones sin errores
2. WHEN creo una nueva donación desde el frontend, THE system SHALL guardar la donación y actualizar la lista
3. WHEN accedo al módulo de eventos desde el frontend, THE system SHALL mostrar la lista de eventos sin errores
4. WHEN creo un nuevo evento desde el frontend, THE system SHALL guardar el evento y actualizar la lista