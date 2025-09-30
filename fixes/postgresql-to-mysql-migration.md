# Migración de PostgreSQL a MySQL - Fix Completo

## Problema Original
El sistema estaba configurado para usar PostgreSQL con Docker, pero había problemas de:
- Encoding UTF-8 en Windows
- Configuración compleja de Docker
- Mensajes de error en español que causaban problemas de codificación
- Conflictos de JWT_SECRET entre servicios

## Solución Implementada

### 1. Migración a MySQL Local

#### Base de Datos
- Creamos `setup_complete_mysql.py` para configurar MySQL con todos los datos
- Mantuvimos la estructura original de tablas en español para no romper el frontend
- Configuramos MySQL con charset `utf8mb4` y collation `utf8mb4_unicode_ci`

#### Configuración de Servicios
```bash
# Configuración .env para todos los servicios
DB_HOST=localhost
DB_NAME=ong_management
DB_USER=root
DB_PASSWORD=root
DB_PORT=3306
```

### 2. Fixes Específicos por Servicio

#### User Service
**Problema**: `RETURNING` clause no existe en MySQL
**Solución**: Modificar `user_repository.py`

```python
# ANTES (PostgreSQL)
query = """
    INSERT INTO usuarios (...)
    VALUES (...)
    RETURNING id, nombre_usuario, ...
"""

# DESPUÉS (MySQL)
query = """
    INSERT INTO usuarios (...)
    VALUES (...)
"""
cursor.execute(query, values)
user_id = cursor.lastrowid

# Fetch separado
select_query = "SELECT ... FROM usuarios WHERE id = %s"
cursor.execute(select_query, (user_id,))
```

#### Inventory Service
**Problema**: Mismatch entre nombres de campos del modelo Donation
**Solución**: Usar nombres en español consistentes con la base de datos

```python
# CORRECTO - usar nombres en español
donation = Donation(
    id=result['id'],
    categoria=DonationCategory(result['categoria']),
    descripcion=result['descripcion'],
    cantidad=result['cantidad'],
    eliminado=result['eliminado'],
    fecha_alta=result['fecha_alta'],
    usuario_alta=result['usuario_alta']
)
```

#### API Gateway
**Problema**: JWT_SECRET diferente entre user-service y api-gateway
**Solución**: Sincronizar JWT_SECRET en ambos .env

```bash
# user-service/.env y api-gateway/.env
JWT_SECRET=your-super-secret-jwt-key-for-development
```

#### Frontend
**Problema**: Frontend apuntaba al puerto 3000, API Gateway en 3001
**Solución**: Actualizar `frontend/src/services/api.js`

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';
```

### 3. Archivos Creados/Modificados

#### Nuevos Archivos
- `database/mysql_schema.sql` - Schema completo para MySQL
- `setup_complete_mysql.py` - Script de configuración automática
- `user-service/src/database_mysql.py` - Conexión MySQL para user-service
- `inventory-service/src/database_mysql.py` - Conexión MySQL para inventory-service

#### Archivos Modificados
- `user-service/src/user_repository.py` - Eliminadas cláusulas RETURNING
- `user-service/.env` - Configuración MySQL + JWT_SECRET sincronizado
- `inventory-service/.env` - Configuración MySQL
- `api-gateway/.env` - JWT_SECRET sincronizado
- `frontend/src/services/api.js` - Puerto 3001 para API Gateway

### 4. Comandos de Setup

```bash
# 1. Instalar dependencia MySQL para Python
pip install mysql-connector-python

# 2. Configurar base de datos
python setup_complete_mysql.py

# 3. Verificar datos
# Usuarios: 5, Donaciones: 8, Eventos: 4
```

### 5. Resultado Final

✅ **Login funciona correctamente**
- Frontend se conecta al API Gateway (puerto 3001)
- JWT tokens se validan correctamente
- User-service se conecta a MySQL sin problemas de encoding

✅ **Creación de usuarios funciona**
- Sin errores de sintaxis SQL
- Datos se insertan correctamente en MySQL

✅ **Inventario funciona**
- Modelos de datos compatibles
- Conexión MySQL estable

### 6. Lecciones Aprendidas

1. **Mantener consistencia**: No cambiar nombres de campos de la base de datos sin actualizar todo el stack
2. **JWT_SECRET**: Debe ser idéntico en todos los servicios que lo usan
3. **MySQL vs PostgreSQL**: Principales diferencias en `RETURNING`, `SERIAL` vs `AUTO_INCREMENT`
4. **Encoding**: MySQL con `utf8mb4` evita problemas de caracteres especiales en Windows

### 7. Events Service - Fixes Adicionales

**Problema**: Events Service tenía múltiples problemas después de la migración a MySQL
**Soluciones aplicadas**:

1. **Campo `expuesto_red` faltante**:
   ```sql
   ALTER TABLE eventos ADD COLUMN expuesto_red BOOLEAN DEFAULT FALSE
   ```

2. **Protobuf desactualizado**: 
   ```bash
   python -m grpc_tools.protoc --proto_path=proto --python_out=src --grpc_python_out=src proto/events.proto
   ```

3. **Sintaxis PostgreSQL en `add_participant`**:
   ```python
   # ANTES (PostgreSQL)
   INSERT INTO participantes_evento (evento_id, usuario_id)
   VALUES (%s, %s)
   ON CONFLICT (evento_id, usuario_id) DO NOTHING
   
   # DESPUÉS (MySQL)
   INSERT IGNORE INTO participantes_evento (evento_id, usuario_id)
   VALUES (%s, %s)
   ```

4. **Método `delete_event` usando helper inconsistente**:
   - Cambió de usar `_execute_query` a conexión directa como otros métodos
   - Manejo explícito de transacciones y cleanup de conexiones

### 8. Estado Actual del Sistema

✅ **Servicios Funcionando con MySQL**:
- User Service: Login, creación de usuarios, gestión completa
- Inventory Service: Gestión de donaciones
- Events Service: Crear, listar, actualizar, eliminar eventos, agregar/quitar participantes
- API Gateway: Todas las rutas funcionando correctamente
- Frontend: Conectado al puerto 3001, autenticación JWT funcionando

✅ **Funcionalidades Verificadas**:
- Login con credenciales de prueba
- Creación y gestión de usuarios
- Gestión completa de inventario
- Gestión completa de eventos
- Agregar/quitar participantes de eventos

### 9. Próximos Pasos

- Implementar live reload con `watchdog` para desarrollo
- Migrar messaging-service a MySQL (último servicio pendiente)
- Crear scripts de backup/restore para MySQL
- Optimizar consultas y agregar índices adicionales si es necesario