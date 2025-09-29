# Formatos de Mensajes Kafka
## Sistema de Mensajería para Red de ONGs

### Tabla de Contenidos
1. [Introducción](#introducción)
2. [Estructura General](#estructura-general)
3. [Topics y Mensajes](#topics-y-mensajes)
4. [Esquemas JSON](#esquemas-json)
5. [Ejemplos Prácticos](#ejemplos-prácticos)
6. [Validación de Mensajes](#validación-de-mensajes)
7. [Versionado de Esquemas](#versionado-de-esquemas)

---

## Introducción

Este documento describe los formatos de mensajes utilizados en el sistema de mensajería Kafka para la red de ONGs. Todos los mensajes siguen un formato JSON estándar y incluyen validación de esquemas para garantizar la integridad de los datos.

### Principios de Diseño
- **Consistencia**: Todos los mensajes siguen la misma estructura base
- **Versionado**: Soporte para evolución de esquemas
- **Validación**: Validación estricta de tipos y formatos
- **Trazabilidad**: Cada mensaje incluye información de origen y timestamp

---

## Estructura General

### Formato Base de Mensaje

Todos los mensajes Kafka siguen esta estructura base:

```json
{
  "version": "1.0",
  "message_type": "TIPO_MENSAJE",
  "organization_id": "id-organizacion-origen",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "message_id": "uuid-unico-del-mensaje",
  "data": {
    // Contenido específico del mensaje
  }
}
```

### Campos Obligatorios

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `version` | string | Versión del esquema del mensaje | "1.0" |
| `message_type` | string | Tipo de mensaje | "DONATION_REQUEST" |
| `organization_id` | string | ID de la organización que envía | "empuje-comunitario" |
| `timestamp` | string (ISO 8601) | Momento de creación del mensaje | "2024-01-15T10:30:00.000Z" |
| `message_id` | string (UUID) | Identificador único del mensaje | "550e8400-e29b-41d4-a716-446655440000" |
| `data` | object | Contenido específico del mensaje | {} |

---

## Topics y Mensajes

### 1. Topic: `/solicitud-donaciones`

**Propósito**: Publicar solicitudes de donaciones a la red de ONGs

#### Estructura del Mensaje

```json
{
  "version": "1.0",
  "message_type": "DONATION_REQUEST",
  "organization_id": "empuje-comunitario",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "request_id": "REQ-2024-001",
    "donations": [
      {
        "category": "ALIMENTOS",
        "description": "Puré de tomates"
      },
      {
        "category": "ROPA",
        "description": "Abrigos para invierno"
      }
    ]
  }
}
```

#### Campos del Data

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `request_id` | string | ✅ | ID único de la solicitud |
| `donations` | array | ✅ | Lista de donaciones solicitadas |
| `donations[].category` | enum | ✅ | Categoría: ALIMENTOS, ROPA, MEDICAMENTOS, JUGUETES, LIBROS, OTROS |
| `donations[].description` | string | ✅ | Descripción específica de la donación |

---

### 2. Topic: `/transferencia-donaciones/{org-id}`

**Propósito**: Transferir donaciones a una organización específica

#### Estructura del Mensaje

```json
{
  "version": "1.0",
  "message_type": "DONATION_TRANSFER",
  "organization_id": "empuje-comunitario",
  "timestamp": "2024-01-15T11:00:00.000Z",
  "message_id": "550e8400-e29b-41d4-a716-446655440001",
  "data": {
    "request_id": "REQ-2024-001",
    "donor_organization": "empuje-comunitario",
    "donations": [
      {
        "category": "ALIMENTOS",
        "description": "Puré de tomates",
        "quantity": "2kg"
      }
    ]
  }
}
```

#### Campos del Data

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `request_id` | string | ✅ | ID de la solicitud original |
| `donor_organization` | string | ✅ | ID de la organización donante |
| `donations` | array | ✅ | Lista de donaciones transferidas |
| `donations[].category` | enum | ✅ | Categoría de la donación |
| `donations[].description` | string | ✅ | Descripción de la donación |
| `donations[].quantity` | string | ✅ | Cantidad con unidad (ej: "2kg", "5 unidades") |

---

### 3. Topic: `/oferta-donaciones`

**Propósito**: Publicar ofertas de donaciones disponibles

#### Estructura del Mensaje

```json
{
  "version": "1.0",
  "message_type": "DONATION_OFFER",
  "organization_id": "empuje-comunitario",
  "timestamp": "2024-01-15T12:00:00.000Z",
  "message_id": "550e8400-e29b-41d4-a716-446655440002",
  "data": {
    "offer_id": "OFF-2024-001",
    "donor_organization": "empuje-comunitario",
    "donations": [
      {
        "category": "ALIMENTOS",
        "description": "Conservas de atún",
        "quantity": "50 latas"
      }
    ]
  }
}
```

#### Campos del Data

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `offer_id` | string | ✅ | ID único de la oferta |
| `donor_organization` | string | ✅ | ID de la organización que ofrece |
| `donations` | array | ✅ | Lista de donaciones ofrecidas |
| `donations[].category` | enum | ✅ | Categoría de la donación |
| `donations[].description` | string | ✅ | Descripción de la donación |
| `donations[].quantity` | string | ✅ | Cantidad disponible |

---

### 4. Topic: `/baja-solicitud-donaciones`

**Propósito**: Cancelar solicitudes de donaciones

#### Estructura del Mensaje

```json
{
  "version": "1.0",
  "message_type": "DONATION_REQUEST_CANCELLATION",
  "organization_id": "empuje-comunitario",
  "timestamp": "2024-01-15T13:00:00.000Z",
  "message_id": "550e8400-e29b-41d4-a716-446655440003",
  "data": {
    "request_id": "REQ-2024-001",
    "reason": "Ya no necesitamos estas donaciones"
  }
}
```

#### Campos del Data

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `request_id` | string | ✅ | ID de la solicitud a cancelar |
| `reason` | string | ❌ | Motivo de la cancelación |

---

### 5. Topic: `/eventossolidarios`

**Propósito**: Publicar eventos solidarios en la red

#### Estructura del Mensaje

```json
{
  "version": "1.0",
  "message_type": "SOLIDARITY_EVENT",
  "organization_id": "empuje-comunitario",
  "timestamp": "2024-01-15T14:00:00.000Z",
  "message_id": "550e8400-e29b-41d4-a716-446655440004",
  "data": {
    "event_id": "EVT-2024-001",
    "name": "Jornada de Vacunación Comunitaria",
    "description": "Vacunación gratuita para toda la comunidad",
    "event_date": "2024-02-15T09:00:00.000Z",
    "location": "Centro Comunitario Principal",
    "contact_info": {
      "phone": "+54 11 1234-5678",
      "email": "eventos@empujecomunitario.org"
    }
  }
}
```

#### Campos del Data

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `event_id` | string | ✅ | ID único del evento |
| `name` | string | ✅ | Nombre del evento |
| `description` | string | ✅ | Descripción del evento |
| `event_date` | string (ISO 8601) | ✅ | Fecha y hora del evento |
| `location` | string | ❌ | Ubicación del evento |
| `contact_info` | object | ❌ | Información de contacto |
| `contact_info.phone` | string | ❌ | Teléfono de contacto |
| `contact_info.email` | string | ❌ | Email de contacto |

---

### 6. Topic: `/baja-evento-solidario`

**Propósito**: Cancelar eventos solidarios

#### Estructura del Mensaje

```json
{
  "version": "1.0",
  "message_type": "EVENT_CANCELLATION",
  "organization_id": "empuje-comunitario",
  "timestamp": "2024-01-15T15:00:00.000Z",
  "message_id": "550e8400-e29b-41d4-a716-446655440005",
  "data": {
    "event_id": "EVT-2024-001",
    "reason": "Condiciones climáticas adversas"
  }
}
```

#### Campos del Data

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `event_id` | string | ✅ | ID del evento a cancelar |
| `reason` | string | ❌ | Motivo de la cancelación |

---

### 7. Topic: `/adhesion-evento/{org-id}`

**Propósito**: Registrar adhesión de voluntarios a eventos externos

#### Estructura del Mensaje

```json
{
  "version": "1.0",
  "message_type": "EVENT_ADHESION",
  "organization_id": "empuje-comunitario",
  "timestamp": "2024-01-15T16:00:00.000Z",
  "message_id": "550e8400-e29b-41d4-a716-446655440006",
  "data": {
    "event_id": "EVT-2024-001",
    "volunteer": {
      "volunteer_id": 123,
      "organization_id": "empuje-comunitario",
      "name": "Juan",
      "lastname": "Pérez",
      "phone": "+54 11 9876-5432",
      "email": "juan.perez@email.com"
    }
  }
}
```

#### Campos del Data

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `event_id` | string | ✅ | ID del evento al que se adhiere |
| `volunteer` | object | ✅ | Información del voluntario |
| `volunteer.volunteer_id` | integer | ✅ | ID del voluntario en su organización |
| `volunteer.organization_id` | string | ✅ | ID de la organización del voluntario |
| `volunteer.name` | string | ✅ | Nombre del voluntario |
| `volunteer.lastname` | string | ✅ | Apellido del voluntario |
| `volunteer.phone` | string | ✅ | Teléfono del voluntario |
| `volunteer.email` | string | ✅ | Email del voluntario |

---

## Esquemas JSON

### Esquema Base para Validación

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "message_type", "organization_id", "timestamp", "message_id", "data"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$"
    },
    "message_type": {
      "type": "string",
      "enum": [
        "DONATION_REQUEST",
        "DONATION_TRANSFER", 
        "DONATION_OFFER",
        "DONATION_REQUEST_CANCELLATION",
        "SOLIDARITY_EVENT",
        "EVENT_CANCELLATION",
        "EVENT_ADHESION"
      ]
    },
    "organization_id": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$",
      "minLength": 3,
      "maxLength": 50
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "message_id": {
      "type": "string",
      "format": "uuid"
    },
    "data": {
      "type": "object"
    }
  }
}
```

### Categorías de Donación

```json
{
  "donation_categories": [
    "ALIMENTOS",
    "ROPA", 
    "MEDICAMENTOS",
    "JUGUETES",
    "LIBROS",
    "OTROS"
  ]
}
```

---

## Ejemplos Prácticos

### Flujo Completo: Solicitud → Transferencia

#### 1. Organización A solicita donaciones

```json
{
  "version": "1.0",
  "message_type": "DONATION_REQUEST",
  "organization_id": "fundacion-esperanza",
  "timestamp": "2024-01-15T10:00:00.000Z",
  "message_id": "req-001",
  "data": {
    "request_id": "REQ-2024-001",
    "donations": [
      {
        "category": "ALIMENTOS",
        "description": "Leche en polvo para bebés"
      }
    ]
  }
}
```

#### 2. Organización B transfiere donaciones

```json
{
  "version": "1.0",
  "message_type": "DONATION_TRANSFER",
  "organization_id": "empuje-comunitario",
  "timestamp": "2024-01-15T11:00:00.000Z",
  "message_id": "trans-001",
  "data": {
    "request_id": "REQ-2024-001",
    "donor_organization": "empuje-comunitario",
    "donations": [
      {
        "category": "ALIMENTOS",
        "description": "Leche en polvo para bebés",
        "quantity": "10 latas de 400g"
      }
    ]
  }
}
```

### Flujo de Eventos

#### 1. Publicar evento

```json
{
  "version": "1.0",
  "message_type": "SOLIDARITY_EVENT",
  "organization_id": "empuje-comunitario",
  "timestamp": "2024-01-15T14:00:00.000Z",
  "message_id": "evt-001",
  "data": {
    "event_id": "EVT-2024-001",
    "name": "Campaña de Donación de Sangre",
    "description": "Jornada de donación voluntaria de sangre",
    "event_date": "2024-02-15T08:00:00.000Z",
    "location": "Hospital Municipal"
  }
}
```

#### 2. Voluntario se adhiere

```json
{
  "version": "1.0",
  "message_type": "EVENT_ADHESION",
  "organization_id": "fundacion-esperanza",
  "timestamp": "2024-01-16T09:00:00.000Z",
  "message_id": "adh-001",
  "data": {
    "event_id": "EVT-2024-001",
    "volunteer": {
      "volunteer_id": 456,
      "organization_id": "fundacion-esperanza",
      "name": "María",
      "lastname": "González",
      "phone": "+54 11 5555-1234",
      "email": "maria.gonzalez@email.com"
    }
  }
}
```

---

## Validación de Mensajes

### Validación en el Productor

```python
import jsonschema
from datetime import datetime
import uuid

def validate_message(message, schema):
    """Valida un mensaje contra su esquema JSON"""
    try:
        jsonschema.validate(message, schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e)

def create_base_message(message_type, organization_id, data):
    """Crea la estructura base de un mensaje"""
    return {
        "version": "1.0",
        "message_type": message_type,
        "organization_id": organization_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "message_id": str(uuid.uuid4()),
        "data": data
    }
```

### Validación en el Consumidor

```python
def process_message(message):
    """Procesa un mensaje recibido de Kafka"""
    
    # Validar estructura base
    is_valid, error = validate_message(message, BASE_SCHEMA)
    if not is_valid:
        logger.error(f"Invalid message structure: {error}")
        return False
    
    # Validar que no sea de nuestra organización
    if message["organization_id"] == OUR_ORGANIZATION_ID:
        logger.debug("Ignoring message from our own organization")
        return True
    
    # Procesar según tipo de mensaje
    message_type = message["message_type"]
    if message_type == "DONATION_REQUEST":
        return process_donation_request(message["data"])
    elif message_type == "DONATION_TRANSFER":
        return process_donation_transfer(message["data"])
    # ... otros tipos
    
    return False
```

---

## Versionado de Esquemas

### Estrategia de Versionado

1. **Versión Mayor** (1.0 → 2.0): Cambios incompatibles
2. **Versión Menor** (1.0 → 1.1): Nuevos campos opcionales
3. **Versión Patch** (1.0.0 → 1.0.1): Correcciones de bugs

### Compatibilidad hacia Atrás

```python
def handle_version_compatibility(message):
    """Maneja compatibilidad entre versiones"""
    version = message.get("version", "1.0")
    
    if version.startswith("1."):
        # Procesar con esquema v1.x
        return process_v1_message(message)
    elif version.startswith("2."):
        # Procesar con esquema v2.x
        return process_v2_message(message)
    else:
        logger.warning(f"Unsupported message version: {version}")
        return False
```

### Migración de Esquemas

```json
{
  "version": "1.1",
  "message_type": "DONATION_REQUEST",
  "organization_id": "empuje-comunitario",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "request_id": "REQ-2024-001",
    "priority": "HIGH",
    "expiry_date": "2024-02-15T00:00:00.000Z",
    "donations": [
      {
        "category": "ALIMENTOS",
        "description": "Puré de tomates",
        "urgency": "MEDIUM"
      }
    ]
  }
}
```

---

## Mejores Prácticas

### 1. Diseño de Mensajes
- Mantener mensajes pequeños y enfocados
- Incluir toda la información necesaria para el procesamiento
- Usar IDs únicos y descriptivos
- Incluir timestamps en UTC

### 2. Manejo de Errores
- Validar todos los mensajes antes de procesar
- Implementar reintentos para errores temporales
- Registrar errores detallados para debugging
- Usar Dead Letter Queues para mensajes fallidos

### 3. Performance
- Usar compresión para mensajes grandes
- Implementar batching cuando sea apropiado
- Monitorear latencia y throughput
- Optimizar serialización/deserialización

### 4. Seguridad
- Validar origen de mensajes
- Sanitizar datos de entrada
- Implementar rate limiting
- Auditar todas las operaciones

---

**Última actualización**: Enero 2024  
**Versión del documento**: 1.0.0