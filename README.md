# Sistema de Gestión ONG "Empuje Comunitario"

Sistema integral de gestión para ONGs con arquitectura de microservicios, que incluye gestión de usuarios, inventario de donaciones, eventos solidarios y red colaborativa entre organizaciones.

## Arquitectura

- **Frontend**: React 18+ con Material-UI
- **API Gateway**: Node.js/Express
- **Microservicios**: Python con gRPC
  - Servicio de Usuarios (Puerto 50051)
  - Servicio de Inventario (Puerto 50052)
  - Servicio de Eventos (Puerto 50053)
- **Base de Datos**: PostgreSQL
- **Mensajería**: Apache Kafka
- **Containerización**: Docker & Docker Compose

## Estructura del Proyecto

```
├── api-gateway/          # API Gateway en Node.js/Express
├── user-service/         # Microservicio de usuarios (Python/gRPC)
├── inventory-service/    # Microservicio de inventario (Python/gRPC)
├── events-service/       # Microservicio de eventos (Python/gRPC)
├── frontend/            # Aplicación React
├── database/            # Scripts de base de datos
├── testing/             # Archivos de testing
├── docker-compose.yml   # Configuración de Docker Compose
├── .env                 # Variables de entorno
└── README.md           # Este archivo
```

## Requisitos Previos

- Docker y Docker Compose
- Node.js 18+ (para desarrollo local)
- Python 3.11+ (para desarrollo local)

## Instalación y Ejecución

### Con Docker Compose (Recomendado)

1. Clonar el repositorio
2. Configurar variables de entorno en `.env`
3. Ejecutar el sistema completo:

```bash
docker-compose up -d
```

### Servicios Disponibles

- **Frontend**: http://localhost:3001
- **API Gateway**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **Kafka**: localhost:9092

## Variables de Entorno

Copiar `.env` y configurar las siguientes variables:

- `DATABASE_URL`: URL de conexión a PostgreSQL
- `KAFKA_BROKERS`: Brokers de Kafka
- `SMTP_*`: Configuración de email
- `JWT_SECRET`: Clave secreta para JWT

## Desarrollo

### Desarrollo Local de Servicios

Cada servicio puede ejecutarse independientemente para desarrollo:

```bash
# API Gateway
cd api-gateway
npm install
npm run dev

# Microservicios Python
cd user-service
pip install -r requirements.txt
python src/server.py

# Frontend
cd frontend
npm install
npm start
```

## Testing

Los archivos de testing se encuentran en el directorio `testing/`:
- Credenciales de usuarios de prueba en `testing/usuarios/passlogs.txt`
- Colecciones de Postman (se crearán en tareas posteriores)

## Documentación

- Documentación de API: http://localhost:3000/api-docs (Swagger)
- Especificaciones gRPC en directorios `proto/` de cada servicio

## Contribución

1. Fork del proyecto
2. Crear rama de feature
3. Commit de cambios
4. Push a la rama
5. Crear Pull Request

## Licencia

MIT License - ver archivo LICENSE para detalles.