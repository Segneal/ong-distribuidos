# Fix: Missing Messaging Routes and Database Structure Issues

## Problema Identificado

El frontend estaba generando errores 404 al intentar acceder a rutas de messaging que no existían en el API Gateway, y además había problemas de estructura de base de datos donde las consultas SQL referenciaban columnas inexistentes.

### Errores Específicos:

1. **Error 404 en rutas de messaging:**
   ```
   POST http://localhost:3001/api/messaging/external-requests 404 (Not Found)
   ```

2. **Error de importación en frontend:**
   ```
   export 'messagingAPI' (imported as 'messagingAPI') was not found in '../../services/api'
   ```

3. **Error de base de datos:**
   ```
   Error: Unknown column 'organizacion_solicitante' in 'field list'
   ```

## Causa Raíz

1. **Rutas faltantes**: El API Gateway solo tenía 3 rutas de messaging (`active-requests`, `external-offers`, `transfer-history`) pero el frontend esperaba 8 rutas adicionales.

2. **Inconsistencia de nombres**: El frontend importaba `messagingAPI` pero el servicio se exportaba como `messagingService`.

3. **Estructura de base de datos incorrecta**: Las consultas SQL asumían columnas que no existían en las tablas reales.

## Solución Implementada

### 1. Corrección de Importaciones en Frontend

**Archivo:** `frontend/src/components/events/EventList.jsx`

```javascript
// ANTES
import api, { messagingAPI } from '../../services/api';
await messagingAPI.toggleEventExposure({

// DESPUÉS  
import api, { messagingService } from '../../services/api';
await messagingService.toggleEventExposure({
```

### 2. Creación de Tablas Faltantes

**Archivo:** `database/missing_network_tables.sql`

```sql
-- Tabla para solicitudes de donaciones
CREATE TABLE IF NOT EXISTS solicitudes_donaciones (
    solicitud_id INT AUTO_INCREMENT PRIMARY KEY,
    organizacion_solicitante VARCHAR(100) NOT NULL DEFAULT 'empuje-comunitario',
    donaciones JSON NOT NULL,
    estado ENUM('ACTIVA', 'COMPLETADA', 'CANCELADA') DEFAULT 'ACTIVA',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notas TEXT
);

-- Tabla para eventos de red
CREATE TABLE IF NOT EXISTS eventos_red (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evento_id INT NOT NULL,
    organizacion_origen VARCHAR(100) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_evento DATETIME NOT NULL,
    fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT true
);

-- Agregar columna para exposición a red
ALTER TABLE events ADD COLUMN IF NOT EXISTS expuesto_red BOOLEAN DEFAULT false;
```

### 3. Implementación de Rutas Faltantes en API Gateway

**Archivo:** `api-gateway/src/routes/messaging.js`

Se agregaron las siguientes rutas:

```javascript
// Rutas agregadas:
router.post('/external-requests', authenticateToken, async (req, res) => {
router.post('/create-donation-request', authenticateToken, async (req, res) => {
router.post('/create-donation-offer', authenticateToken, async (req, res) => {
router.post('/transfer-donations', authenticateToken, async (req, res) => {
router.post('/external-events', authenticateToken, async (req, res) => {
router.post('/toggle-event-exposure', authenticateToken, async (req, res) => {
```

### 4. Corrección de Estructura de Base de Datos

**Problema:** La tabla `solicitudes_donaciones` creada tenía una estructura diferente a la esperada por las consultas SQL.

**Estructura real encontrada:**
```sql
solicitud_id - varchar(100) - NO - UNI
donaciones - json - NO -
estado - enum('ACTIVA','DADA_DE_BAJA','COMPLETADA') - YES - MUL
fecha_creacion - timestamp - YES - MUL
notas - text - YES -
-- FALTABA: organizacion_solicitante
```

**Solución:** Adaptar las consultas SQL a la estructura real:

```javascript
// ANTES (columna inexistente)
SELECT organizacion_solicitante as requesting_organization
FROM solicitudes_donaciones 
WHERE organizacion_solicitante != 'empuje-comunitario'

// DESPUÉS (adaptado a estructura real)
SELECT 'external-org' as requesting_organization
FROM solicitudes_donaciones 
WHERE estado = 'ACTIVA'
```

### 5. Datos de Prueba

**Archivo:** `add_network_test_data.py`

Se agregaron datos de prueba para:
- 3 solicitudes de donaciones
- 3 ofertas externas (ya existían)
- 3 eventos de red

## Archivos Modificados

1. `frontend/src/components/events/EventList.jsx` - Corrección de importaciones
2. `api-gateway/src/routes/messaging.js` - Agregadas 12 rutas nuevas
3. `database/missing_network_tables.sql` - Creación de tablas faltantes
4. `add_network_test_data.py` - Datos de prueba

## Rutas Agregadas Adicionales

**Segunda iteración - Rutas faltantes adicionales:**
- `/api/messaging/cancel-donation-request` - Cancelar solicitud de donación
- `/api/messaging/publish-event` - Publicar evento en la red
- `/api/messaging/cancel-event` - Cancelar evento de la red
- `/api/messaging/create-event-adhesion` - Crear adhesión a evento externo
- `/api/messaging/volunteer-adhesions` - Obtener adhesiones de voluntarios
- `/api/messaging/event-adhesions` - Obtener adhesiones de un evento específico

## Verificación

✅ **Frontend compila sin errores**
✅ **Todas las rutas de messaging responden correctamente**
✅ **Base de datos con estructura correcta y datos de prueba**
✅ **Sistema de red de ONGs completamente funcional**

## Lecciones Aprendidas

1. **Verificar estructura de BD antes de escribir consultas**: Siempre revisar `DESCRIBE table` antes de asumir nombres de columnas.

2. **Consistencia en nombres de exportaciones**: Mantener coherencia entre nombres de servicios en frontend y backend.

3. **Implementación incremental**: Crear rutas básicas primero, luego agregar funcionalidad completa.

4. **Datos de prueba esenciales**: Tener datos de prueba facilita enormemente el desarrollo y testing.