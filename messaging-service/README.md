# Messaging Service

Servicio de mensajería basado en Apache Kafka para la red de ONGs. Permite la comunicación entre organizaciones mediante el intercambio de solicitudes de donaciones, transferencias, ofertas, eventos y adhesiones.

## Características

- **Productores de mensajes**: Publican mensajes en topics específicos de Kafka
- **Consumidores de mensajes**: Procesan mensajes entrantes de otros servicios y organizaciones
- **Manejo de errores**: Reintentos automáticos y recuperación ante fallos
- **Reconexión automática**: Reconexión automática a Kafka en caso de pérdida de conexión
- **Logging estructurado**: Logs detallados para debugging y monitoreo
- **Health checks**: Endpoints para verificar el estado del servicio

## Arquitectura

### Componentes Principales

1. **KafkaConnectionManager**: Gestiona conexiones con Kafka con reintentos automáticos
2. **BaseProducer**: Clase base para publicar mensajes en topics
3. **BaseConsumer**: Clase base para consumir mensajes de topics
4. **NetworkConsumer**: Consumidor para mensajes de red (solicitudes, ofertas, eventos)
5. **OrganizationConsumer**: Consumidor para mensajes específicos de la organización

### Topics de Kafka

- `/solicitud-donaciones`: Solicitudes de donaciones
- `/transferencia-donaciones/{org-id}`: Transferencias de donaciones
- `/oferta-donaciones`: Ofertas de donaciones
- `/baja-solicitud-donaciones`: Bajas de solicitudes
- `/eventossolidarios`: Eventos solidarios
- `/baja-evento-solidario`: Bajas de eventos
- `/adhesion-evento/{org-id}`: Adhesiones a eventos

## Configuración

### Variables de Entorno

```bash
# Configuración Kafka
KAFKA_BROKERS=kafka:9092
KAFKA_GROUP_ID=empuje-comunitario-group
ORGANIZATION_ID=empuje-comunitario

# Configuración de reintentos
KAFKA_RETRY_ATTEMPTS=3
KAFKA_RETRY_DELAY=1000
KAFKA_MAX_RETRY_DELAY=10000

# Configuración de topics
KAFKA_AUTO_CREATE_TOPICS=true
KAFKA_REPLICATION_FACTOR=1

# Base de datos
DB_HOST=postgres
DB_PORT=5432
DB_NAME=ong_management
DB_USER=ong_user
DB_PASSWORD=ong_pass

# Servicio
SERVICE_PORT=50054
LOG_LEVEL=INFO
```

## Uso

### Desarrollo Local

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno (copiar .env.example a .env)

3. Ejecutar el servicio:
```bash
python -m src.main
```

### Docker

El servicio se ejecuta automáticamente con docker-compose:

```bash
docker-compose up messaging-service
```

## Endpoints

### Health Check
```
GET /health
```
Verifica el estado del servicio y la conectividad con Kafka.

### Status
```
GET /status
```
Obtiene información detallada del estado del servicio.

### Test Publishing
```
POST /test/publish?message_type={type}
```
Endpoint de prueba para publicar mensajes.

## Testing

Ejecutar el script de prueba:

```bash
python test_messaging.py
```

## Estructura de Mensajes

### Envelope de Mensaje
Todos los mensajes siguen una estructura estándar:

```json
{
  "message_id": "uuid",
  "message_type": "donation_request",
  "organization_id": "empuje-comunitario",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    // Datos específicos del mensaje
  }
}
```

### Ejemplos de Mensajes

#### Solicitud de Donación
```json
{
  "type": "donation_request",
  "organization_id": "empuje-comunitario",
  "request_id": "REQ-2024-001",
  "donations": [
    {
      "category": "ALIMENTOS",
      "description": "Puré de tomates"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Transferencia de Donación
```json
{
  "type": "donation_transfer",
  "request_id": "REQ-2024-001",
  "donor_organization": "empuje-comunitario",
  "donations": [
    {
      "category": "ALIMENTOS",
      "description": "Puré de tomates",
      "quantity": "2kg"
    }
  ],
  "timestamp": "2024-01-15T11:00:00Z"
}
```

## Monitoreo

El servicio incluye:

- Logs estructurados en formato JSON
- Métricas de conectividad con Kafka
- Health checks para monitoreo externo
- Manejo de errores con reintentos automáticos

## Desarrollo

### Agregar Nuevos Tipos de Mensaje

1. Definir el tipo de mensaje en `config.py`
2. Agregar método en `BaseProducer`
3. Agregar handler en el consumidor apropiado
4. Actualizar tests

### Debugging

Los logs estructurados incluyen:
- IDs de mensaje para trazabilidad
- Información de topics y particiones
- Detalles de errores y reintentos
- Estado de conectividad

## Dependencias

- `kafka-python`: Cliente de Kafka
- `fastapi`: Framework web
- `structlog`: Logging estructurado
- `tenacity`: Reintentos automáticos
- `pydantic`: Validación de datos
- `psycopg2-binary`: Cliente PostgreSQL