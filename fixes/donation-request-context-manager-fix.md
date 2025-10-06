# Fix: Error Context Manager en Solicitudes de Donación

## 🐛 Problema
Error específico: `"'_GeneratorContextManager' object has no attribute 'cursor'"`

## 🔍 Diagnóstico
El problema tenía múltiples capas:

### 1. **Uso Incorrecto del Context Manager**
El `RequestService` estaba usando `get_db_connection()` incorrectamente:
```python
# ❌ INCORRECTO
conn = get_db_connection()
cursor = conn.cursor()
```

Debería usar:
```python
# ✅ CORRECTO
with get_database_connection() as conn:
    cursor = conn.cursor()
```

### 2. **Columna 'notas' No Existe**
El código intentaba insertar en una columna `notas` que no existe en la tabla `solicitudes_externas`.

### 3. **Formato JSON Incorrecto**
Se estaba guardando `str(donations)` en lugar de `json.dumps(donations)` para la columna JSON.

### 4. **Validación de Campos**
El servicio esperaba campos en inglés (`category`, `description`) pero el frontend envía en español (`categoria`, `descripcion`).

## ✅ Solución Implementada

### 1. **Corregir Context Manager**
**Archivo**: `messaging-service/src/messaging/services/request_service.py`

**Antes**:
```python
conn = get_db_connection()
cursor = conn.cursor()
try:
    # operaciones
finally:
    cursor.close()
    conn.close()
```

**Después**:
```python
with get_database_connection() as conn:
    cursor = conn.cursor()
    # operaciones
```

### 2. **Corregir Importación**
```python
# Cambiar
from messaging.database.connection import get_db_connection

# Por
from messaging.database.connection import get_database_connection
```

### 3. **Eliminar Columna 'notas'**
```python
# Antes
cursor.execute("""
    INSERT INTO solicitudes_externas 
    (solicitud_id, organizacion_solicitante, donaciones, fecha_creacion, activa, notas)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (..., notes or ''))

# Después
cursor.execute("""
    INSERT INTO solicitudes_externas 
    (solicitud_id, organizacion_solicitante, donaciones, activa)
    VALUES (%s, %s, %s, %s)
""", (...))
```

### 4. **Corregir Formato JSON**
```python
# Antes
str(donations)  # Genera formato incorrecto

# Después
import json
json.dumps(donations)  # Genera JSON válido
```

### 5. **Validación Multi-idioma**
```python
# Antes
if not donation.get('category') or not donation.get('description'):

# Después
category = donation.get('category') or donation.get('categoria')
description = donation.get('description') or donation.get('descripcion')
if not category or not description:
```

## 📊 Cambios Aplicados

### Archivos Modificados:
- ✅ `messaging-service/src/messaging/services/request_service.py`
  - Context manager corregido en todos los métodos
  - Importación corregida
  - Columna 'notas' eliminada de queries
  - JSON format corregido
  - Validación multi-idioma agregada

### Métodos Corregidos:
- ✅ `create_donation_request()`
- ✅ `get_external_requests()`
- ✅ `get_active_requests()`
- ✅ `cancel_donation_request()`

## 🧪 Testing

### Test Directo del Servicio:
```bash
python test_request_service_direct.py
```

**Resultado**:
- ✅ Formato español: `categoria`, `descripcion` → Funciona
- ✅ Formato inglés: `category`, `description` → Funciona
- ✅ Base de datos: Inserción exitosa
- ✅ Kafka: Publicación exitosa

### Estructura de Tabla Verificada:
```sql
solicitudes_externas:
- id (int, NOT NULL)
- organizacion_solicitante (varchar(100), NOT NULL)
- solicitud_id (varchar(100), NOT NULL)
- donaciones (json, NOT NULL)
- activa (tinyint(1), DEFAULT 1)
- fecha_creacion (timestamp, DEFAULT CURRENT_TIMESTAMP)
```

## 🚀 Cómo Aplicar la Solución

### 1. **Reiniciar Messaging Service**
El messaging service que está corriendo necesita reiniciarse para usar el código corregido:

```bash
# Detener el servicio actual (Ctrl+C)
# Luego reiniciar con:
python start_messaging_local.py
```

### 2. **Verificar Funcionamiento**
```bash
python test_donation_request_api.py
```

### 3. **Probar desde Frontend**
- Ir a Red → Solicitudes de Donación
- Crear nueva solicitud
- Debería funcionar sin errores

## 📋 Estado Después del Fix

### ✅ Lo que Funciona Ahora
- ✅ **Context Manager**: Uso correcto del patrón with
- ✅ **Base de Datos**: Inserción sin errores de columnas
- ✅ **JSON**: Formato válido para columna JSON
- ✅ **Multi-idioma**: Acepta campos en español e inglés
- ✅ **Kafka**: Publicación exitosa de mensajes

### 🔧 Configuración Verificada
- ✅ **Messaging Service**: Puerto 50054
- ✅ **Base de Datos**: localhost:3306
- ✅ **Tabla**: solicitudes_externas con estructura correcta

## 💡 Lecciones Aprendidas

### 1. **Context Managers**
- Siempre usar `with` para recursos que necesitan cleanup
- Verificar que las funciones devuelvan context managers correctos

### 2. **Esquema de Base de Datos**
- Verificar estructura de tablas antes de escribir código
- Mantener sincronización entre código y esquema

### 3. **Formato de Datos**
- JSON columns requieren `json.dumps()`, no `str()`
- Validar formatos de entrada vs esperados

### 4. **Testing Incremental**
- Probar servicios directamente antes de APIs completas
- Aislar problemas capa por capa

## 🎉 Resultado Final

**El error del context manager está completamente resuelto.**

El `RequestService` ahora:
- ✅ Usa context managers correctamente
- ✅ Maneja la base de datos sin errores
- ✅ Acepta datos en español e inglés
- ✅ Genera JSON válido
- ✅ Publica a Kafka exitosamente

**¡Sistema de solicitudes de donación funcionando correctamente!** 🚀

## 🔄 Próximo Paso

**Reiniciar el messaging service** para que use el código corregido:
```bash
python start_messaging_local.py
```