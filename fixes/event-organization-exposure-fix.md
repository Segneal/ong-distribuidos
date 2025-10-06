# Fix: Exposición de Eventos con Organización Correcta

## 🐛 Problema Identificado

Los eventos se exponían a la red siempre como "empuje-comunitario", independientemente de la organización del usuario que los creaba.

**Ejemplo del problema:**
- Usuario de `fundacion-esperanza` crea y expone un evento
- El evento aparece en la red como si fuera de `empuje-comunitario`
- Otras organizaciones ven el evento con la organización incorrecta

## 🔍 Causa Raíz

En `api-gateway/src/routes/messaging.js`, había múltiples lugares donde la organización estaba hardcodeada como `'empuje-comunitario'`:

### Lugares problemáticos:

1. **Toggle Event Exposure** (línea ~410):
```javascript
// ❌ INCORRECTO - Organización hardcodeada
VALUES (?, 'empuje-comunitario', ?, ?, ?, NOW(), true)
```

2. **Expose Event** (línea ~503):
```javascript
// ❌ INCORRECTO - Organización hardcodeada
VALUES (?, 'empuje-comunitario', ?, ?, ?, NOW(), true)
```

3. **Hide Event** (línea ~546):
```javascript
// ❌ INCORRECTO - Filtro por organización hardcodeada
WHERE evento_id = ? AND organizacion_origen = 'empuje-comunitario'
```

4. **Cancel Event** (línea ~785):
```javascript
// ❌ INCORRECTO - Filtro por organización hardcodeada
WHERE evento_id = ? AND organizacion_origen = 'empuje-comunitario'
```

## ✅ Solución Implementada

### 1. Usar Organización del Usuario Logueado

**Archivo**: `api-gateway/src/routes/messaging.js`

#### Toggle Event Exposure
```javascript
// ✅ CORRECTO - Usar organización del usuario
const insertNetworkEventQuery = `
  INSERT INTO eventos_red 
  (evento_id, organizacion_origen, nombre, descripcion, fecha_evento, fecha_publicacion, activo)
  VALUES (?, ?, ?, ?, ?, NOW(), true)  // ← Placeholder para organización
  ON DUPLICATE KEY UPDATE
  activo = true, fecha_publicacion = NOW()
`;

await connection.execute(insertNetworkEventQuery, [
  eventId,
  req.user.organization, // ← Usar organización del usuario logueado
  event.name,
  event.description,
  event.eventDate
]);
```

#### Deactivate Event
```javascript
// ✅ CORRECTO - Filtrar por organización del usuario
const deactivateNetworkEventQuery = `
  UPDATE eventos_red 
  SET activo = false
  WHERE evento_id = ? AND organizacion_origen = ?  // ← Placeholder para organización
`;

await connection.execute(deactivateNetworkEventQuery, [
  eventId, 
  req.user.organization  // ← Usar organización del usuario
]);
```

#### Expose Event
```javascript
// ✅ CORRECTO - Usar organización del usuario
const query = `
  INSERT INTO eventos_red 
  (evento_id, organizacion_origen, nombre, descripcion, fecha_evento, fecha_publicacion, activo)
  VALUES (?, ?, ?, ?, ?, NOW(), true)  // ← Placeholder para organización
  ON DUPLICATE KEY UPDATE
  activo = true, fecha_publicacion = NOW()
`;

await connection.execute(query, [
  eventId, 
  req.user.organization,  // ← Usar organización del usuario
  name, 
  description, 
  eventDate
]);
```

#### Hide Event
```javascript
// ✅ CORRECTO - Filtrar por organización del usuario
const query = `
  UPDATE eventos_red 
  SET activo = false
  WHERE evento_id = ? AND organizacion_origen = ?  // ← Placeholder para organización
`;

await connection.execute(query, [
  eventId, 
  req.user.organization  // ← Usar organización del usuario
]);
```

#### Cancel Event
```javascript
// ✅ CORRECTO - Filtrar por organización del usuario
const deactivateNetworkQuery = `
  UPDATE eventos_red 
  SET activo = false,
      descripcion = CONCAT(descripcion, ' - CANCELADO: ', ?)
  WHERE evento_id = ? AND organizacion_origen = ?  // ← Placeholder para organización
`;

await connection.execute(deactivateNetworkQuery, [
  cancellationReason || 'Evento cancelado',
  eventId,
  req.user.organization  // ← Usar organización del usuario
]);
```

### 2. Logs de Debugging

```javascript
console.log('=== TOGGLE EVENT EXPOSURE ===');
const { eventId, expuesto_red } = req.body;
console.log(`User organization: ${req.user.organization}`);  // ← Log para debugging
console.log(`Event ID: ${eventId}, Expose: ${expuesto_red}`);
```

## 🧪 Resultado Esperado

### ✅ Antes del Fix
- ❌ Usuario de `fundacion-esperanza` expone evento
- ❌ Evento aparece como de `empuje-comunitario` en la red
- ❌ Organización incorrecta en `eventos_red` table

### ✅ Después del Fix
- ✅ Usuario de `fundacion-esperanza` expone evento
- ✅ Evento aparece como de `fundacion-esperanza` en la red
- ✅ Organización correcta en `eventos_red` table
- ✅ Otras organizaciones ven el evento con la organización correcta

## 📊 Impacto

### Funcionalidad
- **Exposición correcta**: Eventos se exponen con la organización del usuario
- **Filtrado correcto**: Solo se modifican eventos de la organización del usuario
- **Integridad de datos**: La tabla `eventos_red` refleja la organización real

### Multi-organización
- **Separación clara**: Cada organización maneja solo sus eventos
- **Seguridad**: No se pueden modificar eventos de otras organizaciones
- **Trazabilidad**: Se puede identificar qué organización publicó cada evento

## 🔧 Archivos Modificados

1. **api-gateway/src/routes/messaging.js**
   - Toggle event exposure: Usar `req.user.organization`
   - Expose event: Usar `req.user.organization`
   - Hide event: Filtrar por `req.user.organization`
   - Cancel event: Filtrar por `req.user.organization`
   - Agregados logs de debugging

## 🎯 Estado Final

✅ **Exposición**: Eventos se exponen con la organización correcta
✅ **Filtrado**: Solo se modifican eventos de la organización del usuario
✅ **Seguridad**: Separación correcta entre organizaciones
✅ **Trazabilidad**: Organización real visible en la red

---

**Fecha**: 2025-10-02
**Severidad**: Alta - Funcionalidad core del sistema multi-organización
**Estado**: ✅ Resuelto