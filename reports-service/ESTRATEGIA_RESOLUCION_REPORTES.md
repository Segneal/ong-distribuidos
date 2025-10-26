# Estrategia de Resolución - Sistema de Reportes RED-ONGs

## a. Tecnologías utilizadas:

### Backend - Servicio de Reportes:
• **Framework Principal**: Python - FastAPI/Strawberry GraphQL
• **API GraphQL**: Strawberry GraphQL para consultas complejas y flexibles
• **API REST**: FastAPI para exportación de archivos y endpoints específicos
• **Protocolo SOAP**: Cliente SOAP personalizado para integración con servicios externos
• **Base de datos**: MySQL con SQLAlchemy ORM
• **Autenticación**: JWT (JSON Web Tokens)
• **Exportación**: OpenPyXL para generación de archivos Excel


### Integración:
• **API Gateway**: Node.js/Express para routing y autenticación centralizada
• **Proxy Configuration**: Servicio de reportes accesible vía proxy desde API Gateway
• **Comunicación Interna**: gRPC + REST híbrido
• **Mensajería**: Kafka para eventos asíncronos (futuro)

## b. Descripción de la resolución:

El **Sistema de Reportes RED-ONGs** implementa una arquitectura híbrida que combina múltiples protocolos de comunicación para satisfacer diferentes necesidades de reporting y consulta de datos entre organizaciones.

### Arquitectura Multi-Protocolo:

**1. GraphQL API (Puerto 8002)**
- Consultas flexibles y eficientes para reportes complejos
- Filtros dinámicos y guardado de configuraciones
- Resolvers especializados por dominio (donaciones, eventos, transferencias)
- Introspección automática del schema

**2. REST API (Puerto 8002)**
- Exportación de archivos Excel con streaming
- Gestión de archivos temporales
- Endpoints de salud y configuración
- Integración con API Gateway para autenticación

**3. SOAP Client**
- Integración con servicios externos de red de ONGs
- Consulta de datos de presidentes y organizaciones
- Manejo robusto de errores y timeouts
- Transformación de datos XML a GraphQL types

### Características Principales:

**Multi-Organización**
- Filtros por organización en todos los reportes
- Aislamiento de datos por contexto organizacional
- Configuraciones específicas por entidad

**Persistencia de Filtros**
- Guardado de configuraciones de filtros por usuario
- Reutilización de consultas complejas
- Gestión de filtros por tipo de reporte

**Exportación Avanzada**
- Generación asíncrona de archivos Excel
- Almacenamiento temporal con limpieza automática
- Descarga directa con gestión de archivos

## c. Diagramas:

### Diagrama de Arquitectura General del Sistema

```mermaid
graph TB
    subgraph "Cliente Web"
        WebUI[Interfaz Web<br/>React + Vite]
    end
    
    subgraph "API Gateway"
        Gateway[Node.js + Express<br/>Puerto: 3001]
        AuthMW[Middleware Autenticación<br/>JWT Validation]
        ValidMW[Middleware Validación<br/>Request Validation]
        CORSMW[Middleware CORS<br/>Cross-Origin]
    end
    
    subgraph "Microservicios"
        Reports[Servicio Reportes<br/>Python + FastAPI<br/>Puerto: 8002]
        Users[Servicio Usuarios<br/>Python + gRPC]
        Events[Servicio Eventos<br/>Python + gRPC]
    end
    
    subgraph "Red de ONGs"
        SOAP[Servicios SOAP<br/>Red Externa ONGs]
    end
    
    subgraph "Base de Datos"
        MySQL[(MySQL<br/>Reportes & Filtros)]
    end
    
    WebUI --> Gateway
    Gateway --> AuthMW
    AuthMW --> ValidMW
    ValidMW --> CORSMW
    
    CORSMW --> Reports
    CORSMW --> Users
    CORSMW --> Events
    
    Reports --> MySQL
    Reports --> SOAP
    Users --> MySQL
    Events --> MySQL
    
    style WebUI fill:#e3f2fd
    style Gateway fill:#f3e5f5
    style Reports fill:#e8f5e8
    style Users fill:#e8f5e8
    style Events fill:#e8f5e8
    style MySQL fill:#fff3e0
    style SOAP fill:#fce4ec
```

### Diagrama de Arquitectura Detallada - Servicio de Reportes

```mermaid
graph TB
    subgraph "Cliente"
        Client[Cliente Web/Postman]
    end
    
    subgraph "API Gateway Layer"
        Gateway[API Gateway<br/>Node.js + Express]
        JWTAuth[JWT Authentication]
        RequestVal[Request Validation]
    end
    
    subgraph "Reports Service - Puerto 8002"
        subgraph "API Layer"
            GraphQLAPI[GraphQL API<br/>Strawberry]
            RESTAPI[REST API<br/>FastAPI]
            SOAPClient[SOAP Client<br/>Custom Implementation]
        end
        
        subgraph "Business Logic Layer"
            DonationResolver[Donation Resolvers]
            EventResolver[Event Resolvers]
            TransferResolver[Transfer Resolvers]
            SOAPResolver[SOAP Resolvers]
            FilterResolver[Filter Resolvers]
        end
        
        subgraph "Service Layer"
            DonationSvc[Donation Service]
            EventSvc[Event Service]
            TransferSvc[Transfer Service]
            ExcelSvc[Excel Export Service]
            SOAPSvc[SOAP Integration Service]
            FilterSvc[Filter Management Service]
        end
        
        subgraph "Data Access Layer"
            Models[SQLAlchemy Models]
            DBUtils[Database Utils]
        end
        
        subgraph "Storage"
            TempFiles[Temporary Excel Files<br/>Local Storage]
        end
    end
    
    subgraph "External Systems"
        MySQL[(MySQL Database<br/>Reports Data)]
        ExternalSOAP[External SOAP Services<br/>ONGs Network]
    end
    
    Client --> Gateway
    Gateway --> JWTAuth
    JWTAuth --> RequestVal
    RequestVal --> GraphQLAPI
    RequestVal --> RESTAPI
    
    GraphQLAPI --> DonationResolver
    GraphQLAPI --> EventResolver
    GraphQLAPI --> TransferResolver
    GraphQLAPI --> SOAPResolver
    GraphQLAPI --> FilterResolver
    
    RESTAPI --> ExcelSvc
    SOAPClient --> SOAPSvc
    
    DonationResolver --> DonationSvc
    EventResolver --> EventSvc
    TransferResolver --> TransferSvc
    SOAPResolver --> SOAPSvc
    FilterResolver --> FilterSvc
    
    DonationSvc --> Models
    EventSvc --> Models
    TransferSvc --> Models
    ExcelSvc --> Models
    ExcelSvc --> TempFiles
    FilterSvc --> Models
    SOAPSvc --> SOAPClient
    
    Models --> DBUtils
    DBUtils --> MySQL
    SOAPClient --> ExternalSOAP
    
    style Client fill:#e3f2fd
    style Gateway fill:#f3e5f5
    style GraphQLAPI fill:#e8f5e8
    style RESTAPI fill:#fff3e0
    style SOAPClient fill:#fce4ec
    style MySQL fill:#fff8e1
    style ExternalSOAP fill:#fce4ec
```

### Diagrama de Flujo de Datos por Protocolo

```mermaid
flowchart TD
    subgraph "Request Flow"
        Start[Client Request] --> AuthCheck{Authentication<br/>Valid?}
        AuthCheck -->|No| AuthError[401 Unauthorized]
        AuthCheck -->|Yes| ProtocolRoute{Protocol<br/>Type?}
        
        ProtocolRoute -->|GraphQL| GraphQLFlow[GraphQL Endpoint<br/>Port 8002]
        ProtocolRoute -->|REST Export| RESTFlow[REST Endpoint<br/>via Gateway]
        ProtocolRoute -->|SOAP Query| SOAPFlow[SOAP Integration<br/>Port 8002]
    end
    
    subgraph "GraphQL Processing"
        GraphQLFlow --> QueryParse[Query Parsing<br/>& Validation]
        QueryParse --> ResolverExec[Resolver Execution]
        ResolverExec --> DataFetch[Database Query<br/>MySQL]
        DataFetch --> GraphQLResp[GraphQL Response<br/>JSON]
    end
    
    subgraph "REST Processing"
        RESTFlow --> ExcelGen[Excel Generation<br/>OpenPyXL]
        ExcelGen --> FileStore[Temporary File<br/>Storage]
        FileStore --> FileDownload[File Download<br/>Response]
    end
    
    subgraph "SOAP Processing"
        SOAPFlow --> SOAPReq[SOAP Request<br/>XML Generation]
        SOAPReq --> ExtService[External SOAP<br/>Service Call]
        ExtService --> XMLParse[XML Response<br/>Parsing]
        XMLParse --> DataTransform[Data Transformation<br/>to GraphQL Types]
        DataTransform --> SOAPResp[SOAP Response<br/>JSON]
    end
    
    GraphQLResp --> ClientResp[Client Response]
    FileDownload --> ClientResp
    SOAPResp --> ClientResp
    
    style Start fill:#e3f2fd
    style AuthCheck fill:#f3e5f5
    style GraphQLFlow fill:#e8f5e8
    style RESTFlow fill:#fff3e0
    style SOAPFlow fill:#fce4ec
    style ClientResp fill:#e8f5e8
```

### Diagrama Entidad-Relación (DER)

```mermaid
erDiagram
    USUARIOS {
        int id PK
        string nombre_usuario UK
        string nombre
        string apellido
        string telefono
        string email UK
        string password_hash
        enum rol
        boolean activo
        datetime fecha_creacion
        datetime fecha_actualizacion
    }
    
    DONACIONES {
        int id PK
        enum categoria
        text descripcion
        int cantidad
        boolean eliminado
        datetime fecha_alta
        int usuario_alta FK
        datetime fecha_modificacion
        int usuario_modificacion FK
    }
    
    EVENTOS {
        int id PK
        string nombre
        text descripcion
        datetime fecha_evento
        datetime fecha_creacion
        datetime fecha_actualizacion
    }
    
    PARTICIPANTES_EVENTO {
        int evento_id PK,FK
        int usuario_id PK,FK
        datetime fecha_adhesion
    }
    
    DONACIONES_REPARTIDAS {
        int id PK
        int evento_id FK
        int donacion_id FK
        int cantidad_repartida
        int usuario_registro FK
        datetime fecha_registro
    }
    
    FILTROS_GUARDADOS {
        int id PK
        int usuario_id FK
        string nombre
        enum tipo
        json configuracion
        datetime fecha_creacion
        datetime fecha_actualizacion
    }
    
    ARCHIVOS_EXCEL {
        string id PK
        int usuario_id FK
        string nombre_archivo
        string ruta_archivo
        datetime fecha_creacion
        datetime fecha_expiracion
    }
    
    TRANSFERENCIAS_DONACIONES {
        int id PK
        enum tipo
        string organizacion_contraparte
        string organizacion_propietaria
        string solicitud_id
        json donaciones
        enum estado
        datetime fecha_transferencia
        int usuario_registro FK
        text notas
    }
    
    %% Relaciones principales
    USUARIOS ||--o{ DONACIONES : "crea/modifica"
    USUARIOS ||--o{ EVENTOS : "participa"
    USUARIOS ||--o{ FILTROS_GUARDADOS : "guarda"
    USUARIOS ||--o{ ARCHIVOS_EXCEL : "genera"
    USUARIOS ||--o{ TRANSFERENCIAS_DONACIONES : "registra"
    USUARIOS ||--o{ DONACIONES_REPARTIDAS : "registra"
    
    %% Relaciones de eventos
    EVENTOS ||--o{ PARTICIPANTES_EVENTO : "tiene"
    USUARIOS ||--o{ PARTICIPANTES_EVENTO : "participa_en"
    EVENTOS ||--o{ DONACIONES_REPARTIDAS : "distribuye"
    DONACIONES ||--o{ DONACIONES_REPARTIDAS : "se_reparte_en"
    
    %% Relaciones específicas de donaciones
    DONACIONES ||--|| USUARIOS : "usuario_creador"
    DONACIONES ||--|| USUARIOS : "usuario_modificador"
```

## d. Problemas Resueltos:

### 1. **Problema de Múltiples Protocolos de Comunicación**

**Situación Inicial:**
- Confusión entre cuándo usar GraphQL vs REST vs SOAP
- Routing inconsistente entre protocolos
- Manejo de errores diferente por protocolo

**Solución Implementada:**
- **GraphQL**: Para consultas complejas y flexibles de reportes
- **REST**: Para operaciones de archivos y endpoints simples
- **SOAP**: Exclusivamente para integración con servicios externos
- **Patrón de Routing Claro**: 
  - Auth + Excel exports → API Gateway (proxy)
  - GraphQL + SOAP → Directo al servicio (puerto 8002)
- **Configuración de Proxy**: API Gateway redirige requests específicos al servicio de reportes

### 2. **Problema de Gestión de Filtros Complejos**

**Situación Inicial:**
- Pérdida de configuraciones de filtros entre sesiones
- Consultas repetitivas complejas
- Falta de reutilización de filtros

**Solución Implementada:**
- Sistema de filtros guardados por usuario y tipo
- Persistencia en base de datos con metadata
- API GraphQL para CRUD de filtros
- Validación de esquemas de filtros

### 3. **Problema de Exportación de Grandes Volúmenes**

**Situación Inicial:**
- Timeouts en exportaciones grandes
- Memoria insuficiente para datasets extensos
- Falta de gestión de archivos temporales

**Solución Implementada:**
- Generación asíncrona con OpenPyXL
- Almacenamiento temporal con limpieza automática
- API REST dedicada para descarga de archivos
- Gestión de memoria optimizada

### 4. **Problema de Integración SOAP Compleja**

**Situación Inicial:**
- Manejo manual de XML y namespaces
- Errores de conexión sin retry logic
- Transformación inconsistente de datos

**Solución Implementada:**
- Cliente SOAP robusto con manejo de errores
- Transformadores automáticos XML → GraphQL Types
- Sistema de retry y timeout configurables
- Validación de respuestas SOAP

### 5. **Problema de Autenticación Multi-Servicio**

**Situación Inicial:**
- Duplicación de lógica de autenticación
- Tokens JWT inconsistentes entre servicios
- Falta de middleware centralizado

**Solución Implementada:**
- Autenticación centralizada en API Gateway
- Middleware JWT reutilizable
- Propagación de contexto de usuario
- Validación consistente de permisos
- **Configuración de Proxy**: Routing inteligente basado en tipo de endpoint

### 6. **Problema de Acceso Directo vs Proxy**

**Situación Inicial:**
- Confusión sobre cuándo acceder directamente al servicio vs vía Gateway
- Inconsistencia en URLs entre desarrollo y producción
- Problemas de CORS en acceso directo desde frontend

**Solución Implementada:**
- **Proxy Configuration en API Gateway**:
  ```javascript
  // Rutas que van por proxy
  app.use('/api/reports', proxy('http://localhost:8002/api/reports'));
  app.use('/api/filters', proxy('http://localhost:8002/api/filters'));
  ```
- **Acceso Directo para GraphQL**: Frontend accede directamente al puerto 8002 para GraphQL
- **Documentación Clara**: Especificación de qué endpoints usan proxy vs acceso directo

## e. Patrones de Diseño Implementados:

### 1. **Repository Pattern**
- Separación clara entre lógica de negocio y acceso a datos
- Servicios especializados por dominio

### 2. **Resolver Pattern (GraphQL)**
- Resolvers modulares por tipo de entidad
- Lazy loading y optimización de consultas

### 3. **Factory Pattern**
- Creación de servicios SOAP configurables
- Instanciación de clientes por entorno

### 4. **Middleware Pattern**
- Autenticación JWT como middleware
- Logging y manejo de errores centralizado

### 5. **Proxy Pattern**
- API Gateway como proxy para endpoints específicos
- Routing inteligente basado en tipo de operación
- Centralización de autenticación y CORS

## f. Métricas de Rendimiento:

### Optimizaciones Implementadas:
- **Consultas GraphQL**: Resolución eficiente con N+1 prevention
- **Exportación Excel**: Optimización de memoria con OpenPyXL
- **Cache SOAP**: Resultados temporales para consultas repetitivas
- **Conexiones DB**: Pool de conexiones optimizado

### Benchmarks:
- **GraphQL Queries**: < 500ms para reportes estándar
- **Excel Export**: ~2MB/segundo para archivos grandes
- **SOAP Integration**: < 3s timeout con retry automático