# Extensiones de Base de Datos para Red de ONGs

Este documento describe las extensiones realizadas a la base de datos para soportar las funcionalidades de red de ONGs mediante mensajería Kafka.

## Nuevas Tablas Agregadas

### 1. `ofertas_externas`
Almacena ofertas de donaciones publicadas por otras organizaciones de la red.

**Campos principales:**
- `organizacion_donante`: ID de la organización que ofrece
- `oferta_id`: ID único de la oferta
- `donaciones`: JSON con detalles de las donaciones ofrecidas
- `activa`: Estado de la oferta (activa/inactiva)

### 2. `adhesiones_eventos_externos`
Registra adhesiones de voluntarios locales a eventos de otras organizaciones.

**Campos principales:**
- `evento_externo_id`: Referencia al evento externo
- `voluntario_id`: Referencia al voluntario local
- `estado`: PENDIENTE, CONFIRMADA, CANCELADA
- `datos_voluntario`: JSON con datos adicionales del voluntario

### 3. `transferencias_donaciones`
Historial de transferencias de donaciones enviadas y recibidas.

**Campos principales:**
- `tipo`: ENVIADA o RECIBIDA
- `organizacion_contraparte`: Organización con la que se transfiere
- `solicitud_id`: ID de la solicitud relacionada
- `donaciones`: JSON con detalles de las donaciones transferidas
- `estado`: PENDIENTE, COMPLETADA, CANCELADA

### 4. `configuracion_organizacion`
Configuración general de la organización para funcionalidades de red.

**Campos principales:**
- `clave`: Nombre de la configuración
- `valor`: Valor de la configuración
- `descripcion`: Descripción de la configuración

### 5. `historial_mensajes`
Auditoría de mensajes Kafka procesados por el sistema.

**Campos principales:**
- `topic`: Topic de Kafka
- `tipo_mensaje`: Tipo de mensaje procesado
- `organizacion_origen/destino`: Organizaciones involucradas
- `contenido`: JSON con el contenido del mensaje
- `estado`: PROCESADO, ERROR, PENDIENTE

## Archivos de Migración

### `network_tables_migration.sql`
Script principal que crea todas las nuevas tablas con:
- Definiciones de tablas con constraints apropiados
- Índices básicos para rendimiento
- Triggers para actualización automática de timestamps
- Datos de prueba iniciales
- Configuración inicial de la organización

### `network_indexes_optimization.sql`
Script de optimización que agrega:
- Índices compuestos para consultas frecuentes
- Índices parciales para casos específicos
- Índices GIN para búsquedas en campos JSON
- Análisis de estadísticas para el optimizador

## Repositorios Creados

### `shared/network_repository.py`
Repositorio principal para operaciones de red que incluye:
- Gestión de ofertas externas
- Registro de transferencias
- Gestión de adhesiones a eventos
- Configuración de organización
- Auditoría de mensajes Kafka

### `inventory-service/src/external_requests_repository.py`
Repositorio especializado para solicitudes externas:
- Gestión de solicitudes de donaciones externas
- Validación de disponibilidad para transferencias
- Reserva de items para transferencias
- Estadísticas de solicitudes

### `events-service/src/external_events_repository.py`
Repositorio especializado para eventos externos:
- Gestión de eventos de otras organizaciones
- Validación de adhesiones de voluntarios
- Búsqueda y filtrado de eventos
- Estadísticas de eventos y adhesiones

## Configuración Inicial

El sistema se configura automáticamente con:

```sql
-- Configuración de la organización
ORGANIZATION_ID = 'empuje-comunitario'
KAFKA_ENABLED = 'true'
AUTO_PROCESS_EXTERNAL_REQUESTS = 'true'
MAX_TRANSFER_AMOUNT = '1000'
```

## Índices de Rendimiento

Se han creado índices optimizados para:
- Consultas por organización y estado activo
- Búsquedas por fecha y rango temporal
- Búsquedas en contenido JSON de donaciones
- Consultas de estadísticas y reportes
- Filtros por estado y tipo

## Datos de Prueba

Se incluyen datos de prueba para:
- Ofertas externas de 3 organizaciones
- Transferencias históricas de ejemplo
- Adhesiones a eventos externos
- Configuración inicial completa

## Ejecución de Migraciones

### Automática (recomendada)
Las migraciones se ejecutan automáticamente al inicializar la base de datos:
```bash
docker-compose up postgres
```

### Manual
Para ejecutar manualmente:
```bash
psql -h localhost -U ong_user -d ong_management -f network_tables_migration.sql
```

## Verificación

Ejecutar el script de prueba para verificar que todo funciona:
```bash
cd shared
python test_network_repositories.py
```

## Mantenimiento

### Limpieza Automática
Los repositorios incluyen métodos para:
- Limpiar solicitudes antiguas inactivas
- Desactivar eventos pasados
- Limpiar eventos antiguos del historial

### Monitoreo
Usar las funciones de estadísticas para monitorear:
- Número de ofertas y solicitudes activas
- Transferencias por período
- Adhesiones a eventos
- Estado de mensajes Kafka

## Consideraciones de Rendimiento

1. **Índices JSON**: Se usan índices GIN para búsquedas eficientes en campos JSON
2. **Índices Parciales**: Solo indexan registros activos para mejor rendimiento
3. **Índices Compuestos**: Optimizan consultas multi-campo frecuentes
4. **Análisis Automático**: Se ejecuta ANALYZE para mantener estadísticas actualizadas

## Seguridad

- Todas las tablas incluyen timestamps de auditoría
- Los mensajes Kafka se registran para trazabilidad
- Las transferencias incluyen información del usuario que las registra
- Se valida la integridad referencial en todas las relaciones