# Sistema de Aprobación de Adhesiones a Eventos

## Resumen de Cambios Implementados

Se ha implementado un sistema completo de aprobación para las adhesiones a eventos distribuidos, donde los voluntarios deben esperar la aprobación del encargado de eventos antes de ser confirmados.

## Cambios en la Base de Datos

### 1. Migración de la Tabla `adhesiones_eventos_externos`

**Archivo**: `database/add_rejected_status_migration.sql`

- ✅ Agregado estado `'RECHAZADA'` al ENUM de estados
- ✅ Agregada columna `fecha_aprobacion` (TIMESTAMP NULL)
- ✅ Agregada columna `motivo_rechazo` (TEXT NULL)
- ✅ Creados índices para mejorar rendimiento

**Estados disponibles**:
- `PENDIENTE` (por defecto) - Esperando aprobación
- `CONFIRMADA` - Aprobada por el encargado
- `CANCELADA` - Cancelada por el voluntario
- `RECHAZADA` - Rechazada por el encargado

## Cambios en el Backend

### 1. API Gateway - Rutas de Messaging

**Archivo**: `api-gateway/src/routes/messaging.js`

#### Ruta Modificada: `/create-event-adhesion`
- ✅ Cambiado estado inicial de `'CONFIRMADA'` a `'PENDIENTE'`
- ✅ Actualizado mensaje de respuesta para indicar que está pendiente de aprobación

#### Nuevas Rutas:

**`POST /api/messaging/approve-event-adhesion`**
- Aprueba una adhesión pendiente
- Verifica permisos del usuario (debe ser de la organización del evento)
- Actualiza estado a `'CONFIRMADA'` y registra `fecha_aprobacion`

**`POST /api/messaging/reject-event-adhesion`**
- Rechaza una adhesión pendiente
- Permite especificar motivo de rechazo
- Actualiza estado a `'RECHAZADA'` y registra `fecha_aprobacion` y `motivo_rechazo`

## Cambios en el Frontend

### 1. Servicio de API

**Archivo**: `frontend/src/services/api.js`

- ✅ Agregada función `approveEventAdhesion(adhesionId)`
- ✅ Agregada función `rejectEventAdhesion(adhesionId, reason)`

### 2. Componente EventAdhesionManager

**Archivo**: `frontend/src/components/network/EventAdhesionManager.jsx`

#### Nuevas Funcionalidades:
- ✅ Botones "Aprobar" y "Rechazar" para adhesiones pendientes
- ✅ Función `handleApproveAdhesion()` - Aprueba adhesiones
- ✅ Función `handleRejectAdhesion()` - Rechaza adhesiones con motivo opcional
- ✅ Estados de carga durante procesamiento
- ✅ Mensajes de éxito/error
- ✅ Actualización automática de la lista tras aprobar/rechazar
- ✅ Estadísticas actualizadas incluyendo adhesiones rechazadas
- ✅ Soporte para estado `'RECHAZADA'` en badges y indicadores

### 3. Componente ExternalEventList

**Archivo**: `frontend/src/components/events/ExternalEventList.jsx`

- ✅ Actualizado mensaje de éxito para indicar que está pendiente de aprobación
- ✅ Actualizada información para explicar el nuevo flujo de aprobación

### 4. Componente VolunteerAdhesions

**Archivo**: `frontend/src/components/events/VolunteerAdhesions.jsx`

- ✅ Agregado soporte para estado `'RECHAZADA'`
- ✅ Actualizado `getStatusBadge()` con textos más descriptivos
- ✅ Agregado mensaje para adhesiones rechazadas
- ✅ Mejorados los textos de estado para mayor claridad

## Flujo del Sistema

### 1. Adhesión del Voluntario
```
1. Voluntario ve evento en "Eventos de la Red"
2. Hace clic en "Inscribirme como Voluntario"
3. Completa formulario con sus datos
4. Sistema crea adhesión con estado 'PENDIENTE'
5. Voluntario recibe mensaje: "Tu solicitud está pendiente de aprobación"
```

### 2. Gestión por el Encargado
```
1. Encargado va a "Gestión de Adhesiones"
2. Selecciona evento de su organización
3. Ve lista de adhesiones pendientes
4. Para cada adhesión puede:
   - Hacer clic en "Aprobar" → Estado cambia a 'CONFIRMADA'
   - Hacer clic en "Rechazar" → Puede agregar motivo → Estado cambia a 'RECHAZADA'
```

### 3. Notificación al Voluntario
```
1. Voluntario ve estado actualizado en "Mis Adhesiones"
2. Estados posibles:
   - "Pendiente de Aprobación" (amarillo)
   - "Aprobada" (verde) 
   - "Rechazada" (rojo) con motivo si se especificó
```

## Seguridad y Validaciones

### Backend
- ✅ Verificación de permisos: Solo la organización del evento puede aprobar/rechazar
- ✅ Validación de estado: Solo adhesiones 'PENDIENTE' pueden ser procesadas
- ✅ Prevención de duplicados: Constraint UNIQUE en (evento_externo_id, voluntario_id)
- ✅ Autenticación requerida en todas las rutas

### Frontend
- ✅ Botones deshabilitados durante procesamiento
- ✅ Mensajes de error claros
- ✅ Actualización automática de datos tras cambios
- ✅ Validación de permisos en la interfaz

## Archivos de Prueba

### 1. Script de Migración
**Archivo**: `apply_adhesion_approval_migration.py`
- Aplica cambios en la base de datos
- Manejo de errores y validaciones
- Mensajes informativos del progreso

### 2. Script de Pruebas
**Archivo**: `test_adhesion_approval_system.py`
- Prueba completa del sistema
- Verifica estructura de base de datos
- Simula flujo completo: crear → aprobar → rechazar
- Genera datos de prueba

## Beneficios del Sistema

### Para las Organizaciones
- ✅ Control total sobre quién participa en sus eventos
- ✅ Capacidad de gestionar aforo y requisitos
- ✅ Historial completo de adhesiones
- ✅ Motivos de rechazo para transparencia

### Para los Voluntarios
- ✅ Proceso claro y transparente
- ✅ Notificación del estado de su solicitud
- ✅ Información sobre motivos de rechazo
- ✅ Historial de todas sus adhesiones

### Para el Sistema
- ✅ Mejor organización de eventos
- ✅ Reducción de no-shows
- ✅ Datos para análisis y mejoras
- ✅ Cumplimiento de requisitos de capacidad

## Estado Final

✅ **Sistema completamente implementado y probado**
✅ **Base de datos migrada exitosamente**
✅ **Frontend actualizado con nueva funcionalidad**
✅ **Backend con rutas de aprobación/rechazo**
✅ **Validaciones y seguridad implementadas**
✅ **Documentación completa**

El sistema está listo para uso en producción y proporciona una experiencia completa de gestión de adhesiones a eventos distribuidos.