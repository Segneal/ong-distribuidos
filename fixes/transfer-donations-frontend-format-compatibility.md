# Fix: Compatibilidad de Formato de Datos Frontend en Transfer Donations

## Problema Identificado

**Error API**:
```
POST http://localhost:3000/api/messaging/transfer-donations 500 (Internal Server Error)
API Error: {
  success: false, 
  error: 'Transfer failed', 
  message: 'Invalid donation: {"category":"UTILES_ESCOLARES","descripcion":"Cuadernos rayados","quantity":"14","inventoryId":7}'
}
```

**Causa**: El frontend envía un formato de datos diferente al que espera la API.

## Análisis del Problema

### Formato Enviado por Frontend
```javascript
{
  "targetOrganization": "fundacion-esperanza",
  "requestId": "REQ-TEST-003",
  "donations": [
    {
      "category": "UTILES_ESCOLARES",
      "descripcion": "Cuadernos rayados", 
      "quantity": "14",        // ← String, no número
      "inventoryId": 7         // ← inventoryId, no donation_id
    }
  ],
  "userId": 1
}
```

### Formato Esperado por API (Original)
```javascript
{
  "targetOrganization": "fundacion-esperanza",
  "requestId": "REQ-TEST-003", 
  "donations": [
    {
      "donation_id": 7,        // ← donation_id, no inventoryId
      "quantity": 14           // ← Número, no string
    }
  ],
  "userId": 1
}
```

### Problemas Identificados
1. **Campo ID**: Frontend envía `inventoryId`, API espera `donation_id`
2. **Tipo de dato**: Frontend envía `quantity` como string, API espera número
3. **Validación estricta**: API rechaza formato del frontend

## Solución Implementada

### Ajustar Validación para Soportar Ambos Formatos

```javascript
// Antes (Solo formato API)
for (const donation of donations) {
  const { donation_id, quantity } = donation;
  
  if (!donation_id || !quantity || quantity <= 0) {
    throw new Error(`Invalid donation: ${JSON.stringify(donation)}`);
  }
}

// Después (Formato flexible)
for (const donation of donations) {
  // Handle both frontend formats: inventoryId or donation_id
  const donationId = donation.donation_id || donation.inventoryId;
  const quantity = parseInt(donation.quantity) || donation.quantity;
  
  if (!donationId || !quantity || quantity <= 0) {
    throw new Error(`Invalid donation: ${JSON.stringify(donation)}`);
  }
}
```

### Cambios Realizados

1. **ID flexible**: `donation.donation_id || donation.inventoryId`
2. **Conversión de tipo**: `parseInt(donation.quantity) || donation.quantity`
3. **Uso consistente**: Reemplazar todas las referencias a `donation_id` con `donationId`

### Código Completo Actualizado

```javascript
// Process each donation transfer
for (const donation of donations) {
  // Handle both frontend formats: inventoryId or donation_id
  const donationId = donation.donation_id || donation.inventoryId;
  const quantity = parseInt(donation.quantity) || donation.quantity;
  
  if (!donationId || !quantity || quantity <= 0) {
    throw new Error(`Invalid donation: ${JSON.stringify(donation)}`);
  }
  
  // Check current quantity
  const checkResult = await pool.query(
    'SELECT cantidad, descripcion FROM donaciones WHERE id = $1 AND eliminado = false',
    [donationId]  // ← Usar donationId
  );
  
  if (checkResult.rows.length === 0) {
    throw new Error(`Donation with ID ${donationId} not found`);  // ← Usar donationId
  }
  
  const currentQuantity = checkResult.rows[0].cantidad;
  const description = checkResult.rows[0].descripcion;
  
  if (currentQuantity < quantity) {
    throw new Error(`Insufficient quantity for ${description}. Available: ${currentQuantity}, Requested: ${quantity}`);
  }
  
  // Update donation quantity
  await pool.query(
    'UPDATE donaciones SET cantidad = cantidad - $1, fecha_modificacion = CURRENT_TIMESTAMP, usuario_modificacion = $2 WHERE id = $3',
    [quantity, userId || 1, donationId]  // ← Usar donationId
  );
  
  // Create transfer history record
  await pool.query(
    'INSERT INTO historial_transferencias (transfer_id, donacion_id, cantidad_transferida, organizacion_destino, solicitud_id, usuario_id) VALUES ($1, $2, $3, $4, $5, $6)',
    [transferId, donationId, quantity, targetOrganization, requestId, userId || 1]  // ← Usar donationId
  );
}
```

## Verificación

### Prueba con Formato Frontend
```bash
curl -X POST http://localhost:3000/api/messaging/transfer-donations \
  -H "Content-Type: application/json" \
  -d '{
    "targetOrganization": "fundacion-esperanza",
    "requestId": "REQ-TEST-003",
    "donations": [
      {
        "category": "UTILES_ESCOLARES",
        "descripcion": "Cuadernos rayados",
        "quantity": "5",
        "inventoryId": 7
      }
    ],
    "userId": 1
  }'
```

### Respuesta Exitosa
```json
{
  "success": true,
  "message": "Donation transfer completed successfully",
  "transfer_id": "TRF-1759169143115",
  "timestamp": "2025-09-29T18:05:43.123Z",
  "transferred_items": 1
}
```

### Verificación de Decremento
```sql
-- Antes: 100 cuadernos
-- Después: 95 cuadernos
SELECT id, descripcion, cantidad FROM donaciones WHERE id = 7;
-- Resultado: 7 | Cuadernos rayados | 95
```

## Compatibilidad Garantizada

### ✅ Formatos Soportados

**Formato Frontend (React)**:
```javascript
{
  inventoryId: 7,
  quantity: "5"  // String
}
```

**Formato API Original**:
```javascript
{
  donation_id: 7,
  quantity: 5    // Number
}
```

**Formato Mixto**:
```javascript
{
  inventoryId: 7,
  quantity: 5    // Number
}
```

### ✅ Conversiones Automáticas
- `inventoryId` → `donationId`
- `"5"` → `5` (string to number)
- Mantiene compatibilidad con formato original

## Estado Final

- ✅ **Frontend compatible**: Acepta formato enviado por React
- ✅ **API flexible**: Soporta múltiples formatos de entrada
- ✅ **Transferencias funcionales**: Decrementan inventario correctamente
- ✅ **Historial actualizado**: Se registran todas las transferencias
- ✅ **Retrocompatibilidad**: Formato API original sigue funcionando

**Fecha de resolución**: 29 de septiembre de 2025  
**Tiempo de resolución**: ~20 minutos  
**Impacto**: Alto - Frontend puede transferir donaciones sin errores