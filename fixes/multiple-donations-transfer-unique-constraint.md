# Fix: Error de Restricción Única en Transferencias Múltiples

## Problema Identificado

**Error**: `duplicate key value violates unique constraint "historial_transferencias_transfer_id_key"`

**Síntoma**: Al intentar transferir múltiples donaciones en una sola operación, la segunda donación fallaba con error de clave duplicada.

**Causa**: Todas las donaciones de una transferencia intentaban usar el mismo `transfer_id`, violando la restricción UNIQUE de la tabla.

## Análisis del Problema

### Escenario Problemático
```javascript
// Transferencia con múltiples donaciones
{
  "targetOrganization": "fundacion-esperanza",
  "requestId": "REQ-MULTI-001", 
  "donations": [
    {"inventoryId": 3, "quantity": "2"},  // ← Primera donación
    {"inventoryId": 5, "quantity": "3"}   // ← Segunda donación
  ]
}
```

### Implementación Problemática
```javascript
const transferId = `TRF-${Date.now()}`;  // ← ID único para toda la transferencia

for (const donation of donations) {
  // Ambas donaciones intentan usar el mismo transfer_id
  await pool.query(
    'INSERT INTO historial_transferencias (transfer_id, donacion_id, ...) VALUES ($1, $2, ...)',
    [transferId, donationId, ...]  // ← Mismo transferId para ambas
  );
}
```

### Restricción de Base de Datos
```sql
-- Tabla historial_transferencias tiene restricción UNIQUE
"historial_transferencias_transfer_id_key" UNIQUE (transfer_id)
```

### Resultado del Error
- ✅ **Primera donación**: Se inserta correctamente
- ❌ **Segunda donación**: Falla con `duplicate key value violates unique constraint`
- ❌ **Transacción**: Se revierte completamente (ROLLBACK)

## Solución Implementada

### Generar IDs Únicos por Donación Individual

```javascript
// Antes (Problemático)
const transferId = `TRF-${Date.now()}`;

for (const donation of donations) {
  await pool.query(
    'INSERT INTO historial_transferencias (transfer_id, ...) VALUES ($1, ...)',
    [transferId, ...]  // ← Mismo ID para todas
  );
}

// Después (Solucionado)
const baseTransferId = `TRF-${Date.now()}`;

for (let i = 0; i < donations.length; i++) {
  const donation = donations[i];
  const uniqueTransferId = `${baseTransferId}-${i + 1}`;  // ← ID único por donación
  
  await pool.query(
    'INSERT INTO historial_transferencias (transfer_id, ...) VALUES ($1, ...)',
    [uniqueTransferId, ...]  // ← ID único para cada registro
  );
}
```

### Patrón de IDs Generados

| Transferencia | Donación | Transfer ID Generado |
|---|---|---|
| TRF-1759170229261 | 1 | TRF-1759170229261-1 |
| TRF-1759170229261 | 2 | TRF-1759170229261-2 |
| TRF-1759170229261 | 3 | TRF-1759170229261-3 |

### Ventajas de la Solución

1. **Unicidad garantizada**: Cada registro tiene un ID único
2. **Trazabilidad mantenida**: Se puede identificar que pertenecen a la misma transferencia
3. **Escalabilidad**: Funciona con cualquier cantidad de donaciones
4. **Retrocompatibilidad**: No afecta transferencias existentes

## Verificación

### Prueba de Transferencia Múltiple
```bash
curl -X POST http://localhost:3000/api/messaging/transfer-donations \
  -H "Content-Type: application/json" \
  -d '{
    "targetOrganization": "fundacion-esperanza",
    "requestId": "REQ-MULTI-001",
    "donations": [
      {"inventoryId": 3, "quantity": "2"},
      {"inventoryId": 5, "quantity": "3"}
    ],
    "userId": 1
  }'
```

### Respuesta Exitosa
```json
{
  "success": true,
  "message": "Donation transfer completed successfully",
  "transfer_id": "TRF-1759170229261",
  "timestamp": "2025-09-29T18:23:49.323Z",
  "transferred_items": 2
}
```

### Registros en Base de Datos
```sql
SELECT transfer_id, donacion_id, cantidad_transferida, organizacion_destino 
FROM historial_transferencias 
WHERE transfer_id LIKE 'TRF-1759170229261%';

-- Resultado:
-- TRF-1759170229261-1 | 3 | 2 | fundacion-esperanza
-- TRF-1759170229261-2 | 5 | 3 | fundacion-esperanza
```

### Verificación de Inventario
```sql
SELECT id, descripcion, cantidad FROM donaciones WHERE id IN (3, 5);

-- Antes:  3 | Camisetas talle M | 25    5 | Pelotas de fútbol | 15
-- Después: 3 | Camisetas talle M | 23    5 | Pelotas de fútbol | 12
```

## Impacto en el Frontend

### Historial de Transferencias
- ✅ **Múltiples registros**: Cada donación aparece como entrada separada
- ✅ **Información completa**: Descripción, cantidad, organización destino
- ✅ **Trazabilidad**: Mismo `solicitud_id` para identificar transferencias relacionadas

### Experiencia de Usuario
- ✅ **Transferencias múltiples**: Funciona sin errores
- ✅ **Feedback inmediato**: Decrementos visibles en inventario
- ✅ **Historial detallado**: Cada item transferido aparece listado

## Consideraciones Futuras

### Agrupación Visual (Opcional)
Para mejorar la UX, el frontend podría agrupar transferencias con el mismo timestamp y solicitud_id:

```javascript
// Agrupar transferencias relacionadas
const groupedTransfers = transfers.reduce((groups, transfer) => {
  const key = `${transfer.solicitud_id}-${transfer.fecha_transferencia}`;
  if (!groups[key]) groups[key] = [];
  groups[key].push(transfer);
  return groups;
}, {});
```

### Alternativa: Campo Batch ID
Para futuras mejoras, se podría agregar un campo `batch_id` para agrupar transferencias relacionadas:

```sql
ALTER TABLE historial_transferencias 
ADD COLUMN batch_id VARCHAR(50);
```

## Estado Final

- ✅ **Transferencias múltiples**: Funcionan correctamente
- ✅ **Restricción única**: No se viola la constraint
- ✅ **Inventario actualizado**: Decrementos aplicados correctamente
- ✅ **Historial completo**: Cada donación registrada individualmente
- ✅ **Transacciones atómicas**: Éxito o fallo completo (no parcial)

**Fecha de resolución**: 29 de septiembre de 2025  
**Tiempo de resolución**: ~15 minutos  
**Impacto**: Alto - Funcionalidad crítica para transferencias múltiples