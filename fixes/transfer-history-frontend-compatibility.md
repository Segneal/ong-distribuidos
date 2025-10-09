# Fix: Compatibilidad de Estructura de Datos en Transfer History

## Problema Identificado

**Error Frontend**:
```
TypeError: Cannot read properties of undefined (reading 'map')
at TransferHistory.jsx:184:44
```

**Causa**: El frontend esperaba `transfer.donaciones.map()` pero la API devolvía una estructura diferente.

## Análisis del Problema

### Estructura Esperada por Frontend
```javascript
// TransferHistory.jsx línea 184
{transfer.donaciones.map((donation, donationIndex) => (
  <div key={donationIndex} className="donation-item">
    <span className="category-badge">
      {getCategoryLabel(donation.category)}
    </span>
  </div>
))}
```

El frontend espera:
```javascript
{
  id: "TRF-123",
  tipo: "ENVIADA",
  organizacion_destino: "fundacion-esperanza", 
  fecha: "2025-09-29T17:51:33.814Z",
  estado: "COMPLETADA",
  donaciones: [  // ← Array requerido
    {
      id: "donation_1",
      descripcion: "Camisetas talle M",
      category: "ROPA",
      cantidad: 5
    }
  ]
}
```

### Estructura Devuelta por API (Incorrecta)
```javascript
{
  transfer_id: "TRF-1759168293802",
  quantity: 5,
  target_organization: "fundacion-esperanza",
  request_id: "REQ-TEST-001", 
  timestamp: "2025-09-29T17:51:33.814Z",
  status: "COMPLETADA",
  donation: {  // ← Objeto único, no array
    description: "Camisetas talle M",
    category: "ROPA"
  }
}
```

## Solución Implementada

### Ajustar Estructura de Respuesta API

```javascript
// Antes (Incorrecto)
const transfers = result.rows.map(row => ({
  transfer_id: row.transfer_id,
  quantity: row.quantity,
  target_organization: row.target_organization,
  request_id: row.request_id,
  timestamp: row.timestamp,
  status: row.status,
  donation: {
    description: row.donation_description,
    category: row.donation_category
  }
}));

// Después (Correcto)
const transfers = result.rows.map(row => ({
  id: row.transfer_id,
  tipo: 'ENVIADA',
  organizacion_destino: row.target_organization,
  fecha: row.timestamp,
  estado: row.status,
  donaciones: [{  // ← Array con un elemento
    id: row.transfer_id + '_donation',
    descripcion: row.donation_description,
    category: row.donation_category,
    cantidad: row.quantity
  }]
}));
```

### Mapeo de Campos

| Campo Frontend | Campo API Original | Campo API Corregido |
|---|---|---|
| `id` | `transfer_id` | `id` |
| `tipo` | N/A | `tipo` (hardcoded "ENVIADA") |
| `organizacion_destino` | `target_organization` | `organizacion_destino` |
| `fecha` | `timestamp` | `fecha` |
| `estado` | `status` | `estado` |
| `donaciones[]` | `donation{}` | `donaciones[]` |
| `donaciones[].descripcion` | `donation.description` | `donaciones[].descripcion` |
| `donaciones[].category` | `donation.category` | `donaciones[].category` |
| `donaciones[].cantidad` | `quantity` | `donaciones[].cantidad` |

## Verificación

### Prueba de API
```bash
curl -X POST http://localhost:3000/api/messaging/transfer-history \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Respuesta Corregida
```json
{
  "success": true,
  "transfers": [
    {
      "id": "TRF-1759168944916",
      "tipo": "ENVIADA",
      "organizacion_destino": "educacion-popular",
      "fecha": "2025-09-29T18:02:24.921Z",
      "estado": "COMPLETADA",
      "donaciones": [
        {
          "id": "TRF-1759168944916_donation",
          "descripcion": "Pantalones infantiles",
          "category": "ROPA",
          "cantidad": 3
        }
      ]
    },
    {
      "id": "TRF-1759168293802",
      "tipo": "ENVIADA", 
      "organizacion_destino": "fundacion-esperanza",
      "fecha": "2025-09-29T17:51:33.814Z",
      "estado": "COMPLETADA",
      "donaciones": [
        {
          "id": "TRF-1759168293802_donation",
          "descripcion": "Camisetas talle M",
          "category": "ROPA",
          "cantidad": 5
        }
      ]
    }
  ]
}
```

## Consideraciones Futuras

### Limitación Actual
- Cada transferencia muestra solo **una donación** por registro
- Si una transferencia incluye múltiples items, aparecerán como transferencias separadas

### Mejora Futura
Para soportar múltiples donaciones por transferencia:

```sql
-- Agrupar por transfer_id y agregar array de donaciones
SELECT 
  ht.transfer_id,
  ht.organizacion_destino,
  ht.fecha_transferencia,
  ht.estado,
  JSON_AGG(
    JSON_BUILD_OBJECT(
      'id', d.id,
      'descripcion', d.descripcion,
      'category', d.categoria,
      'cantidad', ht.cantidad_transferida
    )
  ) as donaciones
FROM historial_transferencias ht
JOIN donaciones d ON ht.donacion_id = d.id
GROUP BY ht.transfer_id, ht.organizacion_destino, ht.fecha_transferencia, ht.estado
ORDER BY ht.fecha_transferencia DESC
```

## Estado Final

- ✅ **Error frontend resuelto**: No más `Cannot read properties of undefined`
- ✅ **Estructura compatible**: API devuelve formato esperado por frontend
- ✅ **Historial funcional**: Frontend puede mostrar transferencias
- ✅ **Datos consistentes**: Campos mapeados correctamente
- ⚠️ **Limitación conocida**: Una donación por transferencia (mejora futura)

**Fecha de resolución**: 29 de septiembre de 2025  
**Tiempo de resolución**: ~15 minutos  
**Impacto**: Medio - Frontend puede mostrar historial sin errores