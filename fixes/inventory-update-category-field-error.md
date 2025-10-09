# Fix: Inventory Update Category Field Error

## Problema Identificado

Al intentar actualizar una donación en el inventario, se produce el siguiente error:

```
PUT http://localhost:3001/api/inventory/3 400 (Bad Request)
API Error: {error: 'Error interno del servidor: Protocol message UpdateDonationRequest has no "category" field.'}
```

## Causa Raíz

El error indica que el servicio gRPC de inventario no reconoce el campo "category" en el mensaje `UpdateDonationRequest`, a pesar de que:

1. El archivo proto define correctamente el campo `category`
2. El transformer en el API Gateway mapea correctamente la categoría
3. El servicio de inventario tiene código para manejar el campo

## Diagnóstico

El problema puede estar en:
1. **Archivos proto desactualizados**: Los archivos generados por protoc no están sincronizados
2. **Servicio no reiniciado**: El inventory-service no ha tomado los cambios del proto
3. **Mapeo de categorías**: Problema en el transformer del API Gateway

## Solución Implementada

### 1. Regeneración de Archivos Proto

**Inventory Service:**
```bash
cd inventory-service
python -m grpc_tools.protoc --proto_path=proto --python_out=src --grpc_python_out=src proto/inventory.proto
```

### 2. Mejora del Transformer

**Archivo:** `api-gateway/src/utils/grpcMapper.js`

```javascript
// ANTES - Categoría opcional
if (restDonation.category) {
  grpcRequest.category = CATEGORY_MAPPING[restDonation.category] || 0;
}

// DESPUÉS - Categoría siempre incluida
if (restDonation.category) {
  const mappedCategory = CATEGORY_MAPPING[restDonation.category];
  if (mappedCategory !== undefined) {
    grpcRequest.category = mappedCategory;
  } else {
    grpcRequest.category = 0; // Default
  }
} else {
  grpcRequest.category = 0; // Default cuando no se proporciona
}
```

### 3. Logging Mejorado

Agregado logging detallado para debug:
- Mapeo de categorías
- Valores de entrada y salida
- Estado del transformer

## Pasos para Resolver

1. ✅ **Regenerar archivos proto** en inventory-service
2. ✅ **Mejorar transformer** para siempre incluir categoría
3. ✅ **Agregar logging** para debug
4. 🔄 **Reiniciar inventory-service** (manual)
5. 🔄 **Probar actualización** de donación

## Verificación

Para verificar que el fix funciona:

1. Reiniciar el inventory-service: `python src/server.py`
2. Intentar actualizar una donación desde el frontend
3. Verificar logs del API Gateway y inventory-service
4. Confirmar que la actualización se completa exitosamente

## Archivos Modificados

1. `api-gateway/src/utils/grpcMapper.js` - Mejorado transformer
2. `inventory-service/src/inventory_pb2.py` - Regenerado desde proto
3. `inventory-service/src/inventory_pb2_grpc.py` - Regenerado desde proto

## Prevención

Para evitar este problema en el futuro:
1. Siempre regenerar archivos proto después de cambios
2. Reiniciar servicios gRPC después de cambios en proto
3. Incluir campos requeridos en transformers
4. Mantener logging detallado para debug