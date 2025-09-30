# Fix: Events Table Name Mismatch

## Problema Identificado

Al intentar exponer eventos a la red, se produce el siguiente error:

```
POST http://localhost:3001/api/messaging/toggle-event-exposure 500 (Internal Server Error)
API Error: {success: false, error: 'Internal server error', message: "Table 'ong_management.events' doesn't exist"}
```

## Causa Raíz

**Desajuste de nombres de tabla:**
- El API Gateway estaba usando `events` (inglés)
- La base de datos real tiene la tabla `eventos` (español)

## Diagnóstico

### Verificación de Tablas
```bash
python check_events_table.py
```

**Resultado:**
- ✅ Tabla `eventos` existe
- ❌ Tabla `events` NO existe
- ✅ Columna `expuesto_red` existe en `eventos`

### Estructura de la Tabla `eventos`
```sql
id - int - NO - PRI
nombre - varchar(255) - NO -
descripcion - text - YES -
fecha_evento - timestamp - NO -
fecha_creacion - timestamp - YES -
fecha_actualizacion - timestamp - YES -
expuesto_red - tinyint(1) - YES -
```

## Solución Implementada

### 1. Corregidas Consultas SQL en API Gateway

**Archivo:** `api-gateway/src/routes/messaging.js`

```javascript
// ANTES - Tabla incorrecta
UPDATE events SET expuesto_red = ? WHERE id = ?

// DESPUÉS - Tabla correcta
UPDATE eventos SET expuesto_red = ? WHERE id = ?
```

### 2. Corregido Mapeo de Campos

```javascript
// ANTES - Campos en inglés
SELECT name, description, eventDate FROM events WHERE id = ?

// DESPUÉS - Campos mapeados correctamente
SELECT nombre as name, descripcion as description, fecha_evento as eventDate 
FROM eventos WHERE id = ?
```

### 3. Todas las Referencias Actualizadas

- ✅ `toggle-event-exposure` - Actualizada tabla y campos
- ✅ `publish-event` - Actualizada tabla
- ✅ `cancel-event` - Actualizada tabla

## Archivos Modificados

1. **api-gateway/src/routes/messaging.js**
   - Cambiadas todas las referencias de `events` a `eventos`
   - Corregido mapeo de campos español → inglés
   - Mantenida compatibilidad con frontend

## Verificación

Para verificar que el fix funciona:

1. ✅ Tabla `eventos` existe y tiene columna `expuesto_red`
2. ✅ Consultas SQL corregidas
3. 🔄 **Probar funcionalidad**: Exponer evento a la red desde frontend

## Funcionalidad Esperada

Después del fix:
1. Usuario hace clic en "🌐 Exponer a Red"
2. API Gateway actualiza `eventos.expuesto_red = true`
3. Se inserta/actualiza registro en `eventos_red`
4. Frontend muestra "🌐 Ocultar de Red"
5. Evento aparece en lista de eventos externos

## Prevención

Para evitar este problema en el futuro:
1. **Consistencia de nombres**: Usar español o inglés consistentemente
2. **Documentación de esquema**: Mantener documentación actualizada
3. **Testing de integración**: Probar rutas con base de datos real
4. **Validación de esquema**: Verificar existencia de tablas en startup