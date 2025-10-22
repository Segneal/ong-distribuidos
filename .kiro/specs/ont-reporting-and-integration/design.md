# Documento de Diseño - Sistema de Reportes e Integración

## Visión General

El Sistema de Reportes e Integración será implementado como un microservicio independiente que proporcionará funcionalidades de reportes avanzados, gestión de filtros personalizados, exportación de datos, e integración con servicios externos SOAP. El sistema utilizará múltiples protocolos (GraphQL, REST, SOAP) según los requerimientos específicos de cada funcionalidad.

### Arquitectura Propuesta

El sistema seguirá una arquitectura de microservicios independiente que se integrará con la infraestructura existente:

- **Servicio de Reportes**: Microservicio principal con soporte multi-protocolo
- **Base de Datos**: Reutilización de la base de datos MySQL existente
- **Frontend**: Nuevos componentes React integrados en la aplicación existente
- **API Gateway**: Extensión para enrutar las nuevas APIs

## Arquitectura

### Diagrama de Arquitectura

```mermaid
graph TB
    subgraph "Frontend React"
        DR[Reportes de Donaciones]
        ER[Reportes de Eventos]
        SC[Consulta SOAP]
        FM[Gestión de Filtros]
    end
    
    subgraph "API Gateway (Node.js)"
        AGW[Gateway Existente]
        NR[Nuevas Rutas]
    end
    
    subgraph "Servicio de Reportes (Python)"
        GQL[Servidor GraphQL]
        REST[Endpoints REST]
        SOAP[Cliente SOAP]
        BL[Lógica de Negocio]
    end
    
    subgraph "Almacenamiento"
        DB[(MySQL DB Existente)]
        FS[Sistema de Archivos - Excel]
    end
    
    subgraph "Servicios Externos"
        SOAPEXT[Servicio SOAP Red ONGs]
    end
    
    DR --> AGW
    ER --> AGW
    SC --> AGW
    FM --> AGW
    
    AGW --> NR
    NR --> GQL
    NR --> REST
    NR --> SOAP
    
    GQL --> BL
    REST --> BL
    SOAP --> BL
    
    BL --> DB
    REST --> FS
    SOAP --> SOAPEXT
```

### Tecnologías Seleccionadas

**Backend (Servicio de Reportes)**
- **Lenguaje**: Python 3.9+
- **Framework Web**: FastAPI (para REST y documentación Swagger)
- **GraphQL**: Strawberry GraphQL
- **SOAP Client**: Zeep
- **Base de Datos**: MySQL (existente)
- **ORM**: SQLAlchemy
- **Exportación Excel**: openpyxl
- **Contenedor**: Docker

**Frontend**
- **Framework**: React 18 (existente)
- **UI Library**: Material-UI (existente)
- **GraphQL Client**: Apollo Client
- **HTTP Client**: Axios (existente)

## Componentes e Interfaces

### 1. Servicio de Reportes (Backend)

#### Estructura del Proyecto
```
reports-service/
├── src/
│   ├── graphql/
│   │   ├── schema.py
│   │   ├── resolvers/
│   │   │   ├── donation_resolvers.py
│   │   │   ├── event_resolvers.py
│   │   │   └── filter_resolvers.py
│   │   └── types/
│   ├── rest/
│   │   ├── routes/
│   │   │   ├── excel_export.py
│   │   │   └── filter_management.py
│   │   └── middleware/
│   ├── soap/
│   │   ├── client.py
│   │   └── schemas.py
│   ├── services/
│   │   ├── donation_service.py
│   │   ├── event_service.py
│   │   ├── filter_service.py
│   │   ├── excel_service.py
│   │   └── soap_service.py
│   ├── models/
│   │   ├── database.py
│   │   ├── donation.py
│   │   ├── event.py
│   │   └── filter.py
│   └── utils/
│       ├── auth.py
│       ├── validators.py
│       └── exceptions.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

#### APIs GraphQL

**Schema de Donaciones**
```graphql
type Donation {
  id: ID!
  categoria: DonationCategory!
  descripcion: String
  cantidad: Int!
  eliminado: Boolean!
  fechaAlta: DateTime!
  usuarioAlta: User
  fechaModificacion: DateTime
  usuarioModificacion: User
}

type DonationReport {
  categoria: DonationCategory!
  eliminado: Boolean!
  totalCantidad: Int!
  registros: [Donation!]!
}

type Query {
  donationReport(
    categoria: DonationCategory
    fechaDesde: DateTime
    fechaHasta: DateTime
    eliminado: Boolean
  ): [DonationReport!]!
  
  eventParticipationReport(
    fechaDesde: DateTime
    fechaHasta: DateTime
    usuarioId: ID!
    repartodonaciones: Boolean
  ): [EventParticipationReport!]!
}

type Mutation {
  saveDonationFilter(
    nombre: String!
    filtros: DonationFilterInput!
  ): SavedFilter!
  
  updateDonationFilter(
    id: ID!
    nombre: String
    filtros: DonationFilterInput
  ): SavedFilter!
  
  deleteDonationFilter(id: ID!): Boolean!
}
```

**Schema de Eventos**
```graphql
type EventParticipationReport {
  mes: String!
  eventos: [EventDetail!]!
}

type EventDetail {
  dia: Int!
  nombre: String!
  descripcion: String
  donaciones: [Donation!]!
}
```

#### APIs REST

**Endpoints de Exportación Excel**
```
POST /api/reports/donations/excel
- Body: { filtros: DonationFilterInput }
- Response: { downloadUrl: string, fileName: string }

GET /api/reports/downloads/{fileId}
- Response: Excel file download
```

**Endpoints de Gestión de Filtros de Eventos**
```
POST /api/filters/events
- Body: { nombre: string, filtros: EventFilterInput }
- Response: SavedFilter

GET /api/filters/events
- Response: SavedFilter[]

PUT /api/filters/events/{id}
- Body: { nombre?: string, filtros?: EventFilterInput }
- Response: SavedFilter

DELETE /api/filters/events/{id}
- Response: { success: boolean }
```

#### Cliente SOAP

**Interfaz del Servicio SOAP**
```python
class SOAPService:
    def get_president_data(self, organization_ids: List[int]) -> List[PresidentData]
    def get_organization_data(self, organization_ids: List[int]) -> List[OrganizationData]
```

### 2. Componentes Frontend

#### Nuevos Componentes React

**Reportes de Donaciones**
```
src/components/reports/
├── DonationReports.jsx
├── DonationFilters.jsx
├── DonationResults.jsx
├── SavedFilters.jsx
└── ExcelExport.jsx
```

**Reportes de Eventos**
```
src/components/reports/
├── EventParticipationReports.jsx
├── EventFilters.jsx
├── EventResults.jsx
└── EventSavedFilters.jsx
```

**Consulta SOAP**
```
src/components/network/
├── NetworkConsultation.jsx
├── OrganizationInput.jsx
└── NetworkResults.jsx
```

#### Integración con Apollo Client

```javascript
// Apollo Client setup para GraphQL
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';

const httpLink = createHttpLink({
  uri: '/api/graphql',
});

const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache(),
});
```

### 3. Extensión del API Gateway

**Nuevas Rutas**
```javascript
// routes/reports.js
app.use('/api/graphql', graphqlProxy);
app.use('/api/reports', reportsProxy);
app.use('/api/filters', filtersProxy);
app.use('/api/network', networkProxy);
```

## Modelos de Datos

### Nuevas Tablas de Base de Datos

```sql
-- Tabla para filtros guardados
CREATE TABLE filtros_guardados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    tipo ENUM('DONACIONES', 'EVENTOS') NOT NULL,
    configuracion JSON NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    UNIQUE KEY unique_user_filter (usuario_id, nombre, tipo)
);

-- Tabla para archivos Excel generados (temporal)
CREATE TABLE archivos_excel (
    id VARCHAR(36) PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

### Modelos de Datos Python

```python
# models/filter.py
class SavedFilter(Base):
    __tablename__ = 'filtros_guardados'
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    nombre = Column(String(255))
    tipo = Column(Enum('DONACIONES', 'EVENTOS'))
    configuracion = Column(JSON)
    fecha_creacion = Column(DateTime)
    fecha_actualizacion = Column(DateTime)

# models/excel_file.py
class ExcelFile(Base):
    __tablename__ = 'archivos_excel'
    
    id = Column(String(36), primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    nombre_archivo = Column(String(255))
    ruta_archivo = Column(String(500))
    fecha_creacion = Column(DateTime)
    fecha_expiracion = Column(DateTime)
```

## Manejo de Errores

### Estrategia de Manejo de Errores

**GraphQL**
- Errores de validación: Retornar en el campo `errors` de la respuesta
- Errores de autorización: HTTP 401/403 con mensaje descriptivo
- Errores de servidor: HTTP 500 con logging detallado

**REST**
- Códigos de estado HTTP estándar
- Respuestas JSON estructuradas con mensajes de error
- Logging centralizado para debugging

**SOAP**
- Manejo básico de timeouts y errores de conexión
- Validación de respuestas XML
- Mensajes de error cuando el servicio no esté disponible

### Códigos de Error Personalizados

```python
class ReportError(Exception):
    INVALID_DATE_RANGE = "INVALID_DATE_RANGE"
    UNAUTHORIZED_USER_ACCESS = "UNAUTHORIZED_USER_ACCESS"
    FILTER_NOT_FOUND = "FILTER_NOT_FOUND"
    EXCEL_GENERATION_FAILED = "EXCEL_GENERATION_FAILED"
    SOAP_SERVICE_UNAVAILABLE = "SOAP_SERVICE_UNAVAILABLE"
```

## Estrategia de Testing

### Testing Básico

**Pruebas Mínimas Necesarias**
- Pruebas unitarias básicas para servicios principales
- Pruebas de endpoints REST y GraphQL
- Pruebas de integración con base de datos
- Pruebas básicas del cliente SOAP

**Herramientas**
- pytest para pruebas unitarias
- pytest-mock para mocking básico
- Pruebas manuales para validación funcional

## Consideraciones de Seguridad

### Autenticación y Autorización

**JWT Token Validation**
- Validación de tokens JWT almacenados en localStorage (como en el proyecto existente)
- Verificación de roles de usuario para acceso a funcionalidades
- Validación simple de permisos por endpoint

**Validación de Permisos**
- Presidentes y Vocales: Acceso completo a reportes de donaciones
- Todos los usuarios: Acceso a reportes de eventos con restricciones
- Solo Presidentes: Acceso a consulta SOAP

### Seguridad de Datos

**Validación Básica**
- Validación de parámetros GraphQL
- Sanitización básica de filtros de fecha
- Validación de IDs de organización para SOAP

## Deployment

### Configuración de Ambiente

**Variables de Entorno**
```env
DATABASE_URL=mysql://user:pass@localhost/ong_management
SOAP_SERVICE_URL=https://soap-applatest.onrender.com/?wsdl
EXCEL_STORAGE_PATH=./storage/excel
JWT_SECRET_KEY=your-secret-key
```

### Deployment Simple

**Desarrollo Local**
- Ejecutar el servicio directamente con Python
- Conexión directa a base de datos MySQL existente
- Almacenamiento local de archivos Excel

**Containerización (Opcional - Al Final)**
- Dockerfile básico para el servicio de reportes
- Integración con docker-compose existente si es necesario