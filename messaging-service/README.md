# Sistema de Mensajería para Red de ONGs

Sistema de mensajería basado en Apache Kafka que permite a las organizaciones participar en una red colaborativa de ONGs, facilitando el intercambio de solicitudes de donaciones, transferencias, ofertas, eventos y adhesiones de voluntarios.

## 🚀 Características Principales

- **Solicitudes de Donaciones**: Publicar y recibir solicitudes de donaciones entre organizaciones
- **Transferencias**: Transferir donaciones directamente a organizaciones que las necesitan
- **Ofertas**: Publicar donaciones disponibles para que otras organizaciones las soliciten
- **Eventos Solidarios**: Compartir eventos y permitir adhesiones de voluntarios externos
- **Mensajería Asíncrona**: Comunicación robusta y escalable mediante Apache Kafka
- **API REST**: Interfaz HTTP para integración con frontend y otros servicios
- **Validación de Datos**: Validación estricta de esquemas JSON para todos los mensajes

## 📋 Requisitos

- Python 3.11+
- Apache Kafka 2.8+
- PostgreSQL 13+
- Docker & Docker Compose (opcional)

## 🛠️ Instalación

### Instalación Local

```bash
# Clonar el repositorio
git clone <repository-url>
cd ong-management-system/messaging-service

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu configuración
```

### Instalación con Docker

```bash
# Desde la raíz del proyecto
docker-compose up -d messaging-service
```

## ⚙️ Configuración

### Variables de Entorno

Crear archivo `.env` en el directorio del servicio:

```bash
# Configuración de Kafka
KAFKA_BROKERS=localhost:9092
KAFKA_GROUP_ID=tu-organizacion-group
ORGANIZATION_ID=tu-organizacion-id

# Configuración de Base de Datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ong_management
DB_USER=ong_user
DB_PASSWORD=tu-password

# Configuración del Servicio
SERVICE_PORT=50054
HTTP_PORT=8000
LOG_LEVEL=INFO
```

### Configuración de Base de Datos

```sql
-- Ejecutar migraciones
psql -h localhost -U ong_user -d ong_management -f ../database/network_tables_migration.sql

-- Configurar ID de organización
INSERT INTO configuracion_organizacion (clave, valor) 
VALUES ('ORGANIZATION_ID', 'tu-organizacion-id');
```

## 🚀 Uso

### Iniciar el Servicio

```bash
# Desarrollo local
python src/main.py

# Con Docker
docker-compose up messaging-service
```

### Verificar Estado

```bash
# Verificar salud del servicio
curl http://localhost:8000/health

# Verificar conexión Kafka
curl -H "Authorization: Bearer <token>" http://localhost:8000/kafka/status
```

## 📚 API Documentation

### Endpoints Principales

#### Solicitudes de Donación

```bash
# Crear solicitud
POST /donation-requests
Content-Type: application/json
Authorization: Bearer <token>

{
  "donations": [
    {
      "category": "ALIMENTOS",
      "description": "Puré de tomates"
    }
  ]
}

# Listar solicitudes externas
GET /donation-requests?active_only=true
Authorization: Bearer <token>

# Cancelar solicitud
POST /donation-requests/{request_id}/cancel
Authorization: Bearer <token>
```

#### Transferencias de Donaciones

```bash
# Realizar transferencia
POST /donation-transfers
Content-Type: application/json
Authorization: Bearer <token>

{
  "target_organization": "organizacion-destino",
  "request_id": "REQ-2024-001",
  "donations": [
    {
      "category": "ALIMENTOS",
      "description": "Puré de tomates",
      "quantity": "2kg"
    }
  ]
}

# Ver historial
GET /donation-transfers?type=ALL&limit=50
Authorization: Bearer <token>
```

#### Ofertas de Donaciones

```bash
# Crear oferta
POST /donation-offers
Content-Type: application/json
Authorization: Bearer <token>

{
  "donations": [
    {
      "category": "ALIMENTOS",
      "description": "Conservas de atún",
      "quantity": "50 latas"
    }
  ]
}

# Listar ofertas externas
GET /donation-offers?active_only=true
Authorization: Bearer <token>
```

#### Eventos Solidarios

```bash
# Publicar evento
POST /events
Content-Type: application/json
Authorization: Bearer <token>

{
  "event_id": "EVT-2024-001",
  "name": "Jornada de Vacunación",
  "description": "Vacunación gratuita para la comunidad",
  "event_date": "2024-02-15T09:00:00.000Z"
}

# Listar eventos externos
GET /events?active_only=true&upcoming_only=true
Authorization: Bearer <token>

# Adherirse a evento
POST /events/{event_id}/adhesions
Content-Type: application/json
Authorization: Bearer <token>

{
  "volunteer_id": 123,
  "volunteer_name": "Juan",
  "volunteer_lastname": "Pérez",
  "volunteer_phone": "+54 11 1234-5678",
  "volunteer_email": "juan@email.com"
}
```

### Documentación Completa

- **OpenAPI/Swagger**: Ver `docs/api-documentation.yaml`
- **Formatos Kafka**: Ver `docs/kafka-message-formats.md`
- **Guía de Configuración**: Ver `docs/admin-configuration-guide.md`

## 🏗️ Arquitectura

### Componentes Principales

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  API Gateway    │    │ Messaging       │
│   (React)       │◄──►│  (Node.js)      │◄──►│ Service         │
└─────────────────┘    └─────────────────┘    │ (Python)        │
                                              └─────────┬───────┘
                                                        │
                       ┌─────────────────┐              │
                       │   PostgreSQL    │◄─────────────┤
                       │   Database      │              │
                       └─────────────────┘              │
                                                        │
                       ┌─────────────────┐              │
                       │  Apache Kafka   │◄─────────────┘
                       │   (Red ONGs)    │
                       └─────────────────┘
```

### Topics de Kafka

| Topic | Propósito |
|-------|-----------|
| `/solicitud-donaciones` | Solicitudes de donaciones |
| `/transferencia-donaciones/{org-id}` | Transferencias dirigidas |
| `/oferta-donaciones` | Ofertas disponibles |
| `/baja-solicitud-donaciones` | Cancelaciones de solicitudes |
| `/eventossolidarios` | Eventos solidarios |
| `/baja-evento-solidario` | Cancelaciones de eventos |
| `/adhesion-evento/{org-id}` | Adhesiones a eventos |

## 🧪 Testing

### Ejecutar Tests

```bash
# Tests unitarios
python -m pytest tests/test_*.py -v

# Tests de integración
python -m pytest tests/integration/ -v

# Tests end-to-end
python run_integration_tests.py

# Verificar cobertura
python -m pytest --cov=src tests/
```

### Tests Disponibles

- **Tests Unitarios**: Productores, consumidores, modelos, validación
- **Tests de Integración**: Kafka, base de datos, flujos completos
- **Tests End-to-End**: Simulación de múltiples organizaciones

## 📊 Monitoreo

### Métricas Disponibles

```bash
# Estado general del servicio
GET /health

# Estado de Kafka
GET /kafka/status

# Logs del servicio
docker logs ong_messaging_service -f
```

### Logs Importantes

```python
# Configurar nivel de log
LOG_LEVEL=DEBUG  # Para desarrollo
LOG_LEVEL=INFO   # Para producción
LOG_LEVEL=ERROR  # Solo errores críticos
```

## 🔧 Desarrollo

### Estructura del Proyecto

```
messaging-service/
├── src/
│   ├── main.py                 # Punto de entrada
│   ├── messaging/
│   │   ├── kafka/
│   │   │   ├── connection.py   # Conexión Kafka
│   │   │   ├── producers.py    # Productores de mensajes
│   │   │   └── consumers.py    # Consumidores de mensajes
│   │   ├── database/
│   │   │   ├── connection.py   # Conexión DB
│   │   │   └── repositories.py # Repositorios de datos
│   │   ├── models/
│   │   │   └── donation.py     # Modelos de datos
│   │   ├── services/
│   │   │   ├── donation_service.py
│   │   │   ├── transfer_service.py
│   │   │   ├── offer_service.py
│   │   │   ├── event_service.py
│   │   │   └── adhesion_service.py
│   │   └── api/
│   │       └── routes.py       # Rutas HTTP
├── tests/                      # Tests unitarios e integración
├── docs/                       # Documentación
├── requirements.txt            # Dependencias Python
├── Dockerfile                  # Imagen Docker
└── README.md                   # Este archivo
```

### Agregar Nueva Funcionalidad

1. **Definir Modelo**: Agregar en `src/messaging/models/`
2. **Crear Servicio**: Implementar lógica en `src/messaging/services/`
3. **Agregar Rutas**: Definir endpoints en `src/messaging/api/`
4. **Escribir Tests**: Crear tests en `tests/`
5. **Documentar**: Actualizar documentación en `docs/`

### Contribuir

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 🐛 Troubleshooting

### Problemas Comunes

#### Error de Conexión Kafka

```bash
# Verificar que Kafka esté ejecutándose
docker ps | grep kafka

# Verificar conectividad
telnet localhost 9092

# Reiniciar Kafka
docker-compose restart kafka
```

#### Error de Base de Datos

```bash
# Verificar PostgreSQL
docker ps | grep postgres

# Verificar conexión
psql -h localhost -U ong_user -d ong_management -c "SELECT 1;"
```

#### Mensajes No Se Procesan

```bash
# Verificar topics
docker exec ong_kafka kafka-topics.sh --list --bootstrap-server localhost:9092

# Ver mensajes en topic
docker exec ong_kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic solicitud-donaciones \
  --from-beginning
```

### Logs de Debug

```bash
# Habilitar logs detallados
export LOG_LEVEL=DEBUG

# Ver logs específicos
docker-compose logs -f messaging-service | grep -i kafka
docker-compose logs -f messaging-service | grep -i error
```

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👥 Equipo

- **Desarrollo**: Equipo de Desarrollo ONG
- **Contacto**: dev@empujecomunitario.org
- **Documentación**: Ver carpeta `docs/`

## 🔗 Enlaces Útiles

- [Documentación de Kafka](https://kafka.apache.org/documentation/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

**Versión**: 1.0.0  
**Última actualización**: Enero 2024