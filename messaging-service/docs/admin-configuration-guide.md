# Guía de Configuración para Administradores
## Sistema de Mensajería para Red de ONGs

### Tabla de Contenidos
1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Configuración Inicial](#configuración-inicial)
3. [Variables de Entorno](#variables-de-entorno)
4. [Configuración de Kafka](#configuración-de-kafka)
5. [Configuración de Base de Datos](#configuración-de-base-de-datos)
6. [Deployment con Docker](#deployment-con-docker)
7. [Monitoreo y Logs](#monitoreo-y-logs)
8. [Troubleshooting](#troubleshooting)
9. [Mantenimiento](#mantenimiento)

---

## Requisitos del Sistema

### Software Requerido
- **Python 3.11+**
- **Apache Kafka 2.8+**
- **PostgreSQL 13+**
- **Docker & Docker Compose** (para deployment containerizado)

### Recursos Mínimos
- **RAM**: 2GB disponibles
- **CPU**: 2 cores
- **Almacenamiento**: 10GB libres
- **Red**: Conectividad a internet para sincronización con otras ONGs

---

## Configuración Inicial

### 1. Clonar y Preparar el Proyecto

```bash
# Clonar el repositorio
git clone <repository-url>
cd ong-management-system

# Navegar al servicio de mensajería
cd messaging-service

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar ID de Organización

**⚠️ IMPORTANTE**: Cada organización debe tener un ID único en la red.

```sql
-- Ejecutar en PostgreSQL
INSERT INTO configuracion_organizacion (clave, valor) 
VALUES ('ORGANIZATION_ID', 'tu-organizacion-id')
ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor;
```

**Formato recomendado para ID**: `nombre-organizacion` (ej: `empuje-comunitario`, `fundacion-esperanza`)

---

## Variables de Entorno

### Archivo `.env` Principal

Crear archivo `.env` en la raíz del proyecto:

```bash
# === CONFIGURACIÓN DE KAFKA ===
KAFKA_BROKERS=localhost:9092
KAFKA_GROUP_ID=tu-organizacion-group
ORGANIZATION_ID=tu-organizacion-id
KAFKA_RETRY_ATTEMPTS=3
KAFKA_RETRY_DELAY=1000
KAFKA_MAX_RETRY_DELAY=10000
KAFKA_AUTO_CREATE_TOPICS=true
KAFKA_REPLICATION_FACTOR=1

# === CONFIGURACIÓN DE BASE DE DATOS ===
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ong_management
DB_USER=ong_user
DB_PASSWORD=tu-password-seguro

# === CONFIGURACIÓN DEL SERVICIO ===
SERVICE_PORT=50054
HTTP_PORT=8000
LOG_LEVEL=INFO

# === CONFIGURACIÓN DE DESARROLLO ===
NODE_ENV=production
TESTING_MODE=false
```

### Variables Críticas

| Variable | Descripción | Valor por Defecto | Requerido |
|----------|-------------|-------------------|-----------|
| `ORGANIZATION_ID` | ID único de tu organización | - | ✅ |
| `KAFKA_BROKERS` | Dirección del broker Kafka | localhost:9092 | ✅ |
| `DB_HOST` | Host de PostgreSQL | localhost | ✅ |
| `DB_PASSWORD` | Contraseña de base de datos | - | ✅ |

---

## Configuración de Kafka

### 1. Instalación Local de Kafka

#### Opción A: Docker Compose (Recomendado)
```yaml
# Ya incluido en docker-compose.yml
kafka:
  image: wurstmeister/kafka:latest
  container_name: ong_kafka
  ports:
    - "9092:9092"
  environment:
    KAFKA_ADVERTISED_HOST_NAME: kafka
    KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
```

#### Opción B: Instalación Manual
```bash
# Descargar Kafka
wget https://downloads.apache.org/kafka/2.8.0/kafka_2.13-2.8.0.tgz
tar -xzf kafka_2.13-2.8.0.tgz
cd kafka_2.13-2.8.0

# Iniciar Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Iniciar Kafka
bin/kafka-server-start.sh config/server.properties
```

### 2. Topics de la Red de ONGs

El sistema utiliza los siguientes topics:

| Topic | Descripción | Particiones | Replicación |
|-------|-------------|-------------|-------------|
| `/solicitud-donaciones` | Solicitudes de donaciones | 3 | 1 |
| `/transferencia-donaciones/{org-id}` | Transferencias dirigidas | 1 | 1 |
| `/oferta-donaciones` | Ofertas disponibles | 3 | 1 |
| `/baja-solicitud-donaciones` | Cancelaciones de solicitudes | 1 | 1 |
| `/eventossolidarios` | Eventos solidarios | 3 | 1 |
| `/baja-evento-solidario` | Cancelaciones de eventos | 1 | 1 |
| `/adhesion-evento/{org-id}` | Adhesiones a eventos | 1 | 1 |

### 3. Verificar Configuración de Kafka

```bash
# Listar topics
docker exec ong_kafka kafka-topics.sh --list --bootstrap-server localhost:9092

# Verificar conectividad
docker exec ong_kafka kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

---

## Configuración de Base de Datos

### 1. Crear Base de Datos

```sql
-- Crear usuario y base de datos
CREATE USER ong_user WITH PASSWORD 'tu-password-seguro';
CREATE DATABASE ong_management OWNER ong_user;
GRANT ALL PRIVILEGES ON DATABASE ong_management TO ong_user;
```

### 2. Ejecutar Migraciones

```bash
# Ejecutar script de inicialización
psql -h localhost -U ong_user -d ong_management -f database/init.sql

# Ejecutar migraciones de red
psql -h localhost -U ong_user -d ong_management -f database/network_tables_migration.sql

# Aplicar optimizaciones
psql -h localhost -U ong_user -d ong_management -f database/network_indexes_optimization.sql
```

### 3. Verificar Tablas

```sql
-- Verificar que las tablas existen
\dt

-- Verificar configuración de organización
SELECT * FROM configuracion_organizacion WHERE clave = 'ORGANIZATION_ID';
```

---

## Deployment con Docker

### 1. Deployment Completo

```bash
# Iniciar todos los servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f messaging-service
```

### 2. Deployment Solo del Messaging Service

```bash
# Construir imagen
docker build -t ong-messaging-service ./messaging-service

# Ejecutar contenedor
docker run -d \
  --name ong_messaging_service \
  -p 50054:50054 \
  -p 8000:8000 \
  --env-file messaging-service/.env \
  ong-messaging-service
```

### 3. Verificar Deployment

```bash
# Verificar salud del servicio
curl http://localhost:8000/health

# Verificar conexión Kafka
curl -H "Authorization: Bearer <token>" http://localhost:8000/kafka/status
```

---

## Monitoreo y Logs

### 1. Configuración de Logs

```python
# Niveles de log disponibles
LOG_LEVEL=DEBUG    # Desarrollo
LOG_LEVEL=INFO     # Producción (recomendado)
LOG_LEVEL=WARNING  # Solo advertencias y errores
LOG_LEVEL=ERROR    # Solo errores
```

### 2. Ubicación de Logs

```bash
# Logs del contenedor Docker
docker logs ong_messaging_service

# Logs con timestamp
docker logs -t ong_messaging_service

# Seguir logs en tiempo real
docker logs -f ong_messaging_service
```

### 3. Métricas Importantes

#### Métricas de Kafka
- **Throughput**: Mensajes por segundo
- **Latencia**: Tiempo de procesamiento
- **Errores de conexión**: Fallos de conectividad
- **Lag del consumidor**: Retraso en procesamiento

#### Métricas de Base de Datos
- **Conexiones activas**: Número de conexiones
- **Tiempo de consulta**: Performance de queries
- **Errores de transacción**: Fallos de escritura

### 4. Dashboard de Monitoreo

```bash
# Verificar estado general
curl http://localhost:8000/health

# Respuesta esperada:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "kafka_connected": true,
  "database_connected": true
}
```

---

## Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a Kafka

**Síntoma**: `kafka.errors.NoBrokersAvailable`

**Soluciones**:
```bash
# Verificar que Kafka esté ejecutándose
docker ps | grep kafka

# Verificar conectividad
telnet localhost 9092

# Reiniciar Kafka
docker-compose restart kafka
```

#### 2. Error de Base de Datos

**Síntoma**: `psycopg2.OperationalError: could not connect`

**Soluciones**:
```bash
# Verificar PostgreSQL
docker ps | grep postgres

# Verificar credenciales
psql -h localhost -U ong_user -d ong_management -c "SELECT 1;"

# Verificar variables de entorno
echo $DB_HOST $DB_USER $DB_NAME
```

#### 3. Mensajes No Se Procesan

**Síntoma**: Mensajes enviados pero no recibidos por otras organizaciones

**Diagnóstico**:
```bash
# Verificar topics
docker exec ong_kafka kafka-topics.sh --list --bootstrap-server localhost:9092

# Verificar mensajes en topic
docker exec ong_kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic solicitud-donaciones \
  --from-beginning
```

#### 4. Problemas de Autenticación

**Síntoma**: `401 Unauthorized` en API calls

**Soluciones**:
- Verificar token JWT válido
- Verificar configuración de `JWT_SECRET`
- Verificar que el usuario tenga permisos adecuados

### Logs de Debugging

```bash
# Habilitar logs detallados
export LOG_LEVEL=DEBUG

# Ver logs específicos de Kafka
docker-compose logs -f messaging-service | grep -i kafka

# Ver logs de base de datos
docker-compose logs -f messaging-service | grep -i database
```

---

## Mantenimiento

### 1. Backup de Base de Datos

```bash
# Backup completo
pg_dump -h localhost -U ong_user ong_management > backup_$(date +%Y%m%d).sql

# Backup solo tablas de red
pg_dump -h localhost -U ong_user ong_management \
  -t solicitudes_externas \
  -t ofertas_externas \
  -t eventos_externos \
  -t adhesiones_eventos_externos \
  -t transferencias_donaciones \
  > backup_network_$(date +%Y%m%d).sql
```

### 2. Limpieza de Datos Antiguos

```sql
-- Limpiar solicitudes canceladas antiguas (más de 30 días)
DELETE FROM solicitudes_externas 
WHERE activa = false 
AND fecha_creacion < NOW() - INTERVAL '30 days';

-- Limpiar eventos pasados (más de 60 días)
DELETE FROM eventos_externos 
WHERE fecha_evento < NOW() - INTERVAL '60 days';

-- Limpiar transferencias antiguas (más de 1 año)
DELETE FROM transferencias_donaciones 
WHERE fecha_transferencia < NOW() - INTERVAL '1 year';
```

### 3. Actualización del Sistema

```bash
# Detener servicios
docker-compose down

# Actualizar código
git pull origin main

# Reconstruir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Verificar funcionamiento
curl http://localhost:8000/health
```

### 4. Rotación de Logs

```bash
# Configurar logrotate
sudo tee /etc/logrotate.d/ong-messaging << EOF
/var/log/ong-messaging/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
```

---

## Configuración de Producción

### 1. Variables de Entorno de Producción

```bash
# Configuración segura para producción
NODE_ENV=production
LOG_LEVEL=INFO
TESTING_MODE=false

# Configuración de Kafka para producción
KAFKA_REPLICATION_FACTOR=3
KAFKA_RETRY_ATTEMPTS=5
KAFKA_MAX_RETRY_DELAY=30000

# Configuración de base de datos
DB_POOL_SIZE=20
DB_MAX_CONNECTIONS=100
```

### 2. Seguridad

```bash
# Cambiar contraseñas por defecto
DB_PASSWORD=contraseña-muy-segura-y-compleja
JWT_SECRET=clave-jwt-muy-segura-de-al-menos-32-caracteres

# Configurar firewall
sudo ufw allow 8000/tcp  # API HTTP
sudo ufw allow 50054/tcp # gRPC
sudo ufw deny 5432/tcp   # PostgreSQL (solo acceso interno)
sudo ufw deny 9092/tcp   # Kafka (solo acceso interno)
```

### 3. Monitoreo Avanzado

```bash
# Instalar herramientas de monitoreo
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  prom/prometheus

docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana
```

---

## Contacto y Soporte

Para soporte técnico o consultas sobre la configuración:

- **Email**: dev@empujecomunitario.org
- **Documentación**: Ver `messaging-service/docs/`
- **Issues**: Crear issue en el repositorio del proyecto

---

**Última actualización**: Enero 2024  
**Versión del documento**: 1.0.0