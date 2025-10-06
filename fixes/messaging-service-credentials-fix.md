# Fix: Error de Credenciales en Messaging Service

## 🐛 Problema
Error: `"Access denied for user 'ong_user'@'localhost' (using password: YES)"`

## 🔍 Diagnóstico
El messaging service está corriendo con la configuración por defecto que usa:
- **Usuario**: `ong_user`
- **Contraseña**: `ong_pass`

Pero nuestra base de datos local usa:
- **Usuario**: `root`
- **Contraseña**: `root`

## ✅ Solución

### 1. **Detener el Messaging Service Actual**
En la terminal donde está corriendo el messaging service, presionar:
```
Ctrl + C
```

### 2. **Iniciar con Configuración Local**
Ejecutar el script que usa las credenciales correctas:
```bash
python start_messaging_local.py
```

Este script:
- ✅ Carga variables de entorno desde `.env.local`
- ✅ Usa credenciales `root`/`root`
- ✅ Conecta a `localhost:3306`
- ✅ Inicia en puerto `50054`

### 3. **Verificar que Funciona**
```bash
python check_messaging_config.py
```

Debería mostrar:
```
✅ Messaging service está corriendo
✅ Solicitud creada exitosamente
```

### 4. **Probar API Completa**
```bash
python test_donation_request_api.py
```

### 5. **Probar desde Frontend**
- Ir a Red → Solicitudes de Donación
- Crear nueva solicitud
- Debería funcionar sin errores

## 📁 Archivos de Configuración

### `.env.local` (Correcto)
```bash
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ong_management
DB_USER=root
DB_PASSWORD=root
HTTP_PORT=50054
ORGANIZATION_ID=empuje-comunitario
KAFKA_ENABLED=false
```

### Configuración por Defecto (Problemática)
```python
# messaging-service/src/messaging/config.py
db_user: str = Field(default_factory=lambda: os.getenv("DB_USER", "ong_user"))
db_password: str = Field(default_factory=lambda: os.getenv("DB_PASSWORD", "ong_pass"))
```

## 🔧 Scripts de Utilidad

### `start_messaging_local.py`
- ✅ Carga configuración desde `.env.local`
- ✅ Inicia messaging service con credenciales correctas

### `check_messaging_config.py`
- ✅ Verifica si el servicio está corriendo
- ✅ Detecta problemas de credenciales
- ✅ Proporciona diagnóstico específico

### `test_messaging_config_local.py`
- ✅ Prueba configuración antes de iniciar
- ✅ Verifica conexión a base de datos

## 📊 Estado Después del Fix

### ✅ Lo que Funcionará
- ✅ **Conexión a BD**: `root@localhost:3306`
- ✅ **Solicitudes**: Creación sin errores de credenciales
- ✅ **API Gateway**: Comunicación exitosa con messaging service
- ✅ **Frontend**: Formularios de solicitudes funcionando

### 🔧 Configuración Final
- **Messaging Service**: Puerto 50054 con credenciales `root`/`root`
- **Base de Datos**: MySQL en localhost:3306
- **API Gateway**: Puerto 3001 conectando a messaging service

## 💡 Prevención Futura

### Para Desarrollo Local
1. **Siempre usar** `start_messaging_local.py`
2. **Verificar configuración** con `check_messaging_config.py`
3. **Mantener** `.env.local` actualizado

### Para Producción
1. **Configurar variables de entorno** apropiadas
2. **Usar credenciales específicas** para cada entorno
3. **Documentar configuración** requerida

## 🎯 Comando de Solución Rápida

```bash
# 1. Detener servicio actual (Ctrl+C en su terminal)
# 2. Iniciar con configuración correcta:
python start_messaging_local.py
```

## 🎉 Resultado Esperado

Después de reiniciar el messaging service:
- ✅ **Sin errores de credenciales**
- ✅ **Solicitudes de donación funcionando**
- ✅ **API completa operativa**
- ✅ **Frontend sin errores 500**

**¡Sistema de solicitudes de donación completamente funcional!** 🚀