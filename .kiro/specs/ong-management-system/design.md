# Documento de Diseño - Sistema de Gestión ONG "Empuje Comunitario"

## Visión General

El sistema de gestión para la ONG "Empuje Comunitario" implementa una arquitectura de microservicios distribuida que facilita la administración interna de la organización y la colaboración con otras ONGs a través de una red interconectada. La solución utiliza tecnologías modernas para garantizar escalabilidad, mantenibilidad y rendimiento.

### Objetivos del Diseño

- **Separación de responsabilidades**: Cada microservicio maneja un dominio específico
- **Comunicación eficiente**: gRPC para comunicación interna, REST para frontend
- **Integración externa**: Kafka para mensajería asíncrona entre ONGs
- **Experiencia de usuario**: Interfaz web moderna y responsiva
- **Observabilidad**: Logging, monitoreo y trazabilidad completa

## Arquitectura

### Arquitectura General del Sistema

```mermaid
graph TB
    subgraph "Frontend"
        UI[React Frontend<br/>Componentes Funcionales]
    end
    
    subgraph "API Gateway"
        GW[Express.js Gateway<br/>Puerto 3000]
    end
    
    subgraph "Microservicios gRPC"
        US[Servicio Usuarios<br/>Python - Puerto 50051]
        IS[Servicio Inventario<br/>Python - Puerto 50052]
        ES[Servicio Eventos<br/>Python - Puerto 50053]
    end
    
    subgraph "Mensajería"
        K[Apache Kafka<br/>Puerto 9092]
    end
    
    subgraph "Base de Datos"
        DB[(PostgreSQL<br/>Puerto 5432)]
    end
    
    subgraph "Servicios Externos"
        MAIL[Nodemailer<br/>SMTP]
    end
    
    UI --> GW
    GW --> US
    GW --> IS
    GW --> ES
    US --> DB
    IS --> DB
    ES --> DB
    US --> MAIL
    US --> K
    IS --> K
    ES --> K
    K --> US
    K --> IS
    K --> ES
```

### Patrones Arquitectónicos

1. **API Gateway Pattern**: Punto único de entrada para el frontend
2. **Microservicios**: Servicios independientes por dominio de negocio
3. **Event-Driven Architecture**: Comunicación asíncrona via Kafka
4. **Repository Pattern**: Abstracción de acceso a datos
5. **Service Layer Pattern**: Lógica de negocio encapsulada

## Componentes y Interfaces

### 1. Frontend (React)

**Tecnologías:**
- React 18+ con componentes funcionales
- React Router para navegación
- Axios para comunicación HTTP
- Material-UI o Tailwind CSS para estilos
- React Hook Form para formularios

**Estructura de Componentes:**
```
src/
├── components/
│   ├── common/
│   │   ├── Layout.jsx
│   │   ├── Navigation.jsx
│   │   └── ProtectedRoute.jsx
│   ├── auth/
│   │   └── LoginForm.jsx
│   ├── users/
│   │   ├── UserList.jsx
│   │   ├── UserForm.jsx
│   │   └── UserDetail.jsx
│   ├── inventory/
│   │   ├── InventoryList.jsx
│   │   ├── DonationForm.jsx
│   │   └── CategoryFilter.jsx
│   └── events/
│       ├── EventList.jsx
│       ├── EventForm.jsx
│       └── ParticipantManager.jsx
├── hooks/
│   ├── useAuth.js
│   ├── useApi.js
│   └── usePermissions.js
├── services/
│   └── api.js
└── utils/
    ├── constants.js
    └── helpers.js
```

**Interfaces de Comunicación:**
- REST API calls al API Gateway
- Manejo de estados con Context API o Zustand
- Autenticación basada en JWT tokens

### 2. API Gateway (Node.js/Express)

**Responsabilidades:**
- Enrutamiento de peticiones a microservicios
- Autenticación y autorización
- Rate limiting y validación
- Transformación de datos REST ↔ gRPC
- Manejo de CORS

**Estructura del Proyecto:**
```
api-gateway/
├── src/
│   ├── controllers/
│   │   ├── authController.js
│   │   ├── usersController.js
│   │   ├── inventoryController.js
│   │   └── eventsController.js
│   ├── middleware/
│   │   ├── auth.js
│   │   ├── validation.js
│   │   └── errorHandler.js
│   ├── services/
│   │   ├── grpcClients.js
│   │   └── authService.js
│   ├── routes/
│   │   ├── auth.js
│   │   ├── users.js
│   │   ├── inventory.js
│   │   └── events.js
│   └── utils/
│       ├── grpcMapper.js
│       └── logger.js
├── proto/
│   ├── users.proto
│   ├── inventory.proto
│   └── events.proto
└── package.json
```

**Endpoints REST:**
```
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/users
POST   /api/users
PUT    /api/users/:id
DELETE /api/users/:id
GET    /api/inventory
POST   /api/inventory
PUT    /api/inventory/:id
DELETE /api/inventory/:id
GET    /api/events
POST   /api/events
PUT    /api/events/:id
DELETE /api/events/:id
POST   /api/events/:id/participants
DELETE /api/events/:id/participants/:userId
GET    /api/external/events
GET    /api/external/donations/requests
POST   /api/external/donations/transfer
```

### 3. Microservicio de Usuarios (Python/gRPC)

**Responsabilidades:**
- Gestión de usuarios (CRUD)
- Autenticación y autorización
- Generación y envío de contraseñas
- Manejo de roles y permisos

**Estructura del Proyecto:**
```
user-service/
├── src/
│   ├── services/
│   │   ├── user_service.py
│   │   └── auth_service.py
│   ├── repositories/
│   │   └── user_repository.py
│   ├── models/
│   │   └── user.py
│   ├── utils/
│   │   ├── password_generator.py
│   │   ├── email_sender.py
│   │   └── crypto.py
│   └── server.py
├── proto/
│   └── users.proto
├── tests/
└── requirements.txt
```

**Definición gRPC (users.proto):**
```protobuf
syntax = "proto3";

package users;

service UserService {
  rpc CreateUser(CreateUserRequest) returns (UserResponse);
  rpc GetUser(GetUserRequest) returns (UserResponse);
  rpc UpdateUser(UpdateUserRequest) returns (UserResponse);
  rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
  rpc AuthenticateUser(AuthRequest) returns (AuthResponse);
}

message User {
  int32 id = 1;
  string username = 2;
  string first_name = 3;
  string last_name = 4;
  string email = 5;
  string phone = 6;
  Role role = 7;
  bool is_active = 8;
  string created_at = 9;
  string updated_at = 10;
}

enum Role {
  PRESIDENTE = 0;
  VOCAL = 1;
  COORDINADOR = 2;
  VOLUNTARIO = 3;
}
```

### 4. Microservicio de Inventario (Python/gRPC)

**Responsabilidades:**
- Gestión de donaciones (CRUD)
- Control de categorías y cantidades
- Auditoría de cambios
- Integración con Kafka para transferencias

**Estructura del Proyecto:**
```
inventory-service/
├── src/
│   ├── services/
│   │   ├── inventory_service.py
│   │   └── kafka_service.py
│   ├── repositories/
│   │   └── inventory_repository.py
│   ├── models/
│   │   └── donation.py
│   ├── utils/
│   │   └── audit.py
│   └── server.py
├── proto/
│   └── inventory.proto
├── tests/
└── requirements.txt
```

**Definición gRPC (inventory.proto):**
```protobuf
syntax = "proto3";

package inventory;

service InventoryService {
  rpc CreateDonation(CreateDonationRequest) returns (DonationResponse);
  rpc GetDonation(GetDonationRequest) returns (DonationResponse);
  rpc UpdateDonation(UpdateDonationRequest) returns (DonationResponse);
  rpc DeleteDonation(DeleteDonationRequest) returns (DeleteDonationResponse);
  rpc ListDonations(ListDonationsRequest) returns (ListDonationsResponse);
  rpc TransferDonations(TransferDonationsRequest) returns (TransferDonationsResponse);
}

message Donation {
  int32 id = 1;
  Category category = 2;
  string description = 3;
  int32 quantity = 4;
  bool deleted = 5;
  string created_at = 6;
  string updated_at = 7;
  int32 created_by = 8;
  int32 updated_by = 9;
}

enum Category {
  ROPA = 0;
  ALIMENTOS = 1;
  JUGUETES = 2;
  UTILES_ESCOLARES = 3;
}
```

### 5. Microservicio de Eventos (Python/gRPC)

**Responsabilidades:**
- Gestión de eventos solidarios (CRUD)
- Manejo de participantes
- Registro de donaciones repartidas
- Publicación de eventos en Kafka

**Estructura del Proyecto:**
```
events-service/
├── src/
│   ├── services/
│   │   ├── events_service.py
│   │   └── kafka_service.py
│   ├── repositories/
│   │   ├── events_repository.py
│   │   └── participants_repository.py
│   ├── models/
│   │   ├── event.py
│   │   └── participant.py
│   └── server.py
├── proto/
│   └── events.proto
├── tests/
└── requirements.txt
```

### 6. Sistema de Mensajería (Apache Kafka)

**Tópicos Kafka:**
```
/solicitud-donaciones
/transferencia-donaciones/{org-id}
/oferta-donaciones
/baja-solicitud-donaciones
/eventossolidarios
/baja-evento-solidario
/adhesion-evento/{org-id}
```

**Estructura de Mensajes:**
```json
// Solicitud de donaciones
{
  "organizacion_id": "string",
  "solicitud_id": "string",
  "donaciones": [
    {
      "categoria": "ALIMENTOS",
      "descripcion": "Puré de tomates"
    }
  ]
}

// Transferencia de donaciones
{
  "solicitud_id": "string",
  "organizacion_donante": "string",
  "donaciones": [
    {
      "categoria": "ALIMENTOS",
      "descripcion": "Puré de tomates",
      "cantidad": "2kg"
    }
  ]
}
```

## Modelos de Datos

### Base de Datos PostgreSQL

**Esquema de Usuarios:**
```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('PRESIDENTE', 'VOCAL', 'COORDINADOR', 'VOLUNTARIO')),
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Esquema de Inventario:**
```sql
CREATE TABLE donaciones (
    id SERIAL PRIMARY KEY,
    categoria VARCHAR(20) NOT NULL CHECK (categoria IN ('ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES')),
    descripcion TEXT,
    cantidad INTEGER NOT NULL CHECK (cantidad >= 0),
    eliminado BOOLEAN DEFAULT false,
    fecha_alta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_alta INTEGER REFERENCES usuarios(id),
    fecha_modificacion TIMESTAMP,
    usuario_modificacion INTEGER REFERENCES usuarios(id)
);
```

**Esquema de Eventos:**
```sql
CREATE TABLE eventos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_evento TIMESTAMP NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE participantes_evento (
    evento_id INTEGER REFERENCES eventos(id),
    usuario_id INTEGER REFERENCES usuarios(id),
    fecha_adhesion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (evento_id, usuario_id)
);

CREATE TABLE donaciones_repartidas (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER REFERENCES eventos(id),
    donacion_id INTEGER REFERENCES donaciones(id),
    cantidad_repartida INTEGER NOT NULL,
    usuario_registro INTEGER REFERENCES usuarios(id),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Esquemas para Red de ONGs:**
```sql
CREATE TABLE solicitudes_externas (
    id SERIAL PRIMARY KEY,
    organizacion_solicitante VARCHAR(100) NOT NULL,
    solicitud_id VARCHAR(100) NOT NULL,
    donaciones JSONB NOT NULL,
    activa BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE eventos_externos (
    id SERIAL PRIMARY KEY,
    organizacion_id VARCHAR(100) NOT NULL,
    evento_id VARCHAR(100) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_evento TIMESTAMP NOT NULL,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Manejo de Errores

### Estrategia de Manejo de Errores

1. **Frontend (React):**
   - Manejo básico de errores con try-catch
   - Mensajes de error simples para el usuario

2. **API Gateway (Express):**
   - Middleware básico de manejo de errores
   - Códigos de estado HTTP apropiados

3. **Microservicios (Python/gRPC):**
   - Manejo básico de errores gRPC
   - Logging simple con print statements

4. **Kafka:**
   - Manejo básico de errores de conexión

### Códigos de Error Básicos

```python
# Códigos de error simples
class ErrorCodes:
    USER_NOT_FOUND = "USER_NOT_FOUND"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
```

## Estrategia de Testing

### Testing Manual con Postman

- Colecciones de Postman para cada endpoint
- Testing manual de flujos principales
- Documentación de casos de prueba

### Datos de Prueba

**Datos de Prueba:**
- Scripts SQL para poblar base de datos
- Archivo `/testing/usuarios/passlogs.txt` para credenciales de testing

**Ejemplo de datos de prueba:**
```sql
-- Usuarios de prueba
INSERT INTO usuarios (nombre_usuario, nombre, apellido, email, password_hash, rol) VALUES
('admin', 'Juan', 'Pérez', 'admin@empujecomunitario.org', '$2b$12$...', 'PRESIDENTE'),
('vocal1', 'María', 'González', 'maria@empujecomunitario.org', '$2b$12$...', 'VOCAL'),
('coord1', 'Carlos', 'López', 'carlos@empujecomunitario.org', '$2b$12$...', 'COORDINADOR'),
('vol1', 'Ana', 'Martínez', 'ana@empujecomunitario.org', '$2b$12$...', 'VOLUNTARIO');
```

## Seguridad

### Autenticación y Autorización

1. **JWT Tokens básicos:**
   - Tokens simples para autenticación
   - Almacenamiento en localStorage (para simplicidad)

2. **Encriptación de Contraseñas:**
   - bcrypt básico para hash de contraseñas
   - Generación de contraseñas aleatorias

3. **Autorización basada en Roles:**
   - Verificación simple de roles en cada endpoint

### Comunicación

1. **HTTP básico:**
   - Comunicación HTTP sin TLS para desarrollo
   - gRPC sin encriptación para simplicidad

## Logging Básico

### Logging Simple

1. **Logging básico:**
   - Console.log para frontend
   - Print statements para Python
   - Console.log para Node.js

2. **Health Checks básicos:**
   - Endpoint simple `/health` para verificar que los servicios están funcionando

## Despliegue y DevOps

### Containerización

**Dockerfile para Microservicios Python:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY proto/ ./proto/

EXPOSE 50051
CMD ["python", "src/server.py"]
```

**Docker Compose para Desarrollo:**
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ong_management
      POSTGRES_USER: ong_user
      POSTGRES_PASSWORD: ong_pass
    ports:
      - "5432:5432"
  
  kafka:
    image: confluentinc/cp-kafka:latest
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
    ports:
      - "9092:9092"
  
  user-service:
    build: ./user-service
    ports:
      - "50051:50051"
    depends_on:
      - postgres
  
  api-gateway:
    build: ./api-gateway
    ports:
      - "3000:3000"
    depends_on:
      - user-service
      - inventory-service
      - events-service
```

### Despliegue Manual

1. **Despliegue local:**
   - Docker Compose para desarrollo local
   - Scripts simples para iniciar servicios

### Configuración de Entornos

**Variables de Entorno:**
```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/ong_db

# Kafka
KAFKA_BROKERS=localhost:9092
ORGANIZATION_ID=empuje-comunitario

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@empujecomunitario.org
SMTP_PASS=app_password

# JWT
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=15m
REFRESH_TOKEN_EXPIRES_IN=7d

# Testing
NODE_ENV=development
TESTING_MODE=true
```

Este diseño proporciona una base sólida para implementar el sistema de gestión de la ONG con todas las funcionalidades requeridas, manteniendo principios de arquitectura limpia, escalabilidad y mantenibilidad.