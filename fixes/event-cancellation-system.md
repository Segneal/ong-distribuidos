# Sistema de Baja de Eventos Solidarios

## Descripción General

Implementación completa del sistema de notificación de baja de eventos a través del topic Kafka `/baja-evento-solidario`. Cuando una organización da de baja un evento, se notifica automáticamente a toda la red y se actualizan los sistemas correspondientes.

## Arquitectura del Sistema

### 1. Topic Kafka: `/baja-evento-solidario`

**Formato del mensaje:**
```json
{
  "organization_id": "empuje-comunitario",
  "event_id": 101,
  "cancellation_reason": "Cancelado por mal tiempo",
  "timestamp": "2025-09-30T22:30:00Z"
}
```

### 2. Componentes Implementados

#### Producer (Envío de mensajes)
- **Archivo:** `messaging-service/src/messaging/producers/event_cancellation_producer.py`
- **Función:** Envía mensajes cuando nuestra organización cancela un evento
- **Integración:** Se activa cuando se da de baja un evento expuesto a la red

#### Consumer (Recepción de mensajes)
- **Archivo:** `messaging-service/src/messaging/consumers/event_cancellation_consumer.py`
- **Función:** Procesa mensajes de otras organizaciones
- **Acciones:**
  - Desactiva eventos en `eventos_red`
  - Notifica a usuarios inscritos
  - Actualiza estado de adhesiones
  - Registra en historial

### 3. Base de Datos

#### Tabla de Notificaciones
```sql
CREATE TABLE notificaciones_usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    mensaje TEXT NOT NULL,
    tipo ENUM('EVENT_CANCELLED', 'EVENT_UPDATED', 'DONATION_RECEIVED', 'GENERAL'),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_leida TIMESTAMP NULL,
    leida BOOLEAN DEFAULT false
);
```

## Flujo de Cancelación de Eventos

### Cuando Nuestra Organización Cancela un Evento

1. **Usuario cancela evento** desde la interfaz
2. **API Gateway** (`/api/messaging/cancel-own-event`):
   - Marca evento como cancelado en BD local
   - Si estaba expuesto a la red, lo desactiva
   - Envía mensaje al topic Kafka
3. **Producer Kafka** envía notificación a la red
4. **Otras organizaciones** reciben y procesan el mensaje

### Cuando Otra Organización Cancela un Evento

1. **Consumer Kafka** recibe mensaje del topic
2. **Procesamiento automático**:
   - Desactiva evento en `eventos_red`
   - Busca usuarios inscritos al evento
   - Crea notificaciones personalizadas
   - Actualiza adhesiones a 'CANCELADA'
   - Registra en historial de mensajes

## Interfaz de Usuario

### Centro de Notificaciones

**Ubicación:** `/notifications`
**Características:**
- ✅ Lista de notificaciones por usuario
- ✅ Indicador de no leídas
- ✅ Marcar como leída individual/masivo
- ✅ Iconos por tipo de notificación
- ✅ Formato de fecha legible
- ✅ Diseño responsive

**Tipos de Notificación:**
- ❌ `EVENT_CANCELLED` - Evento cancelado
- 📅 `EVENT_UPDATED` - Evento actualizado  
- 🎁 `DONATION_RECEIVED` - Donación recibida
- 📢 `GENERAL` - Notificación general

### Integración en Navegación

- Agregado al menú principal como "Notificaciones"
- Accesible para todos los roles
- Icono de campana en la sidebar

## API Endpoints

### Notificaciones
- `GET /api/notifications` - Obtener notificaciones del usuario
- `PUT /api/notifications/:id/read` - Marcar como leída
- `PUT /api/notifications/read-all` - Marcar todas como leídas

### Cancelación de Eventos
- `POST /api/messaging/cancel-own-event` - Cancelar evento propio

## Beneficios del Sistema

### Para Usuarios
- ✅ **Notificación inmediata** de eventos cancelados
- ✅ **Información clara** sobre motivos de cancelación
- ✅ **Centro unificado** de notificaciones
- ✅ **Estado de lectura** para seguimiento

### Para la Red de ONGs
- ✅ **Sincronización automática** entre organizaciones
- ✅ **Integridad de datos** en tiempo real
- ✅ **Trazabilidad completa** de cambios
- ✅ **Escalabilidad** a través de Kafka

### Para Administradores
- ✅ **Historial completo** de mensajes procesados
- ✅ **Monitoreo** de estado del sistema
- ✅ **Auditoría** de cancelaciones
- ✅ **Gestión centralizada** de notificaciones

## Archivos Creados/Modificados

### Backend
1. `messaging-service/src/messaging/consumers/event_cancellation_consumer.py`
2. `messaging-service/src/messaging/producers/event_cancellation_producer.py`
3. `api-gateway/src/routes/notifications.js`
4. `api-gateway/src/routes/messaging.js` - Agregada ruta cancel-own-event
5. `api-gateway/src/server.js` - Registradas rutas de notificaciones

### Frontend
1. `frontend/src/components/notifications/NotificationCenter.jsx`
2. `frontend/src/components/notifications/Notifications.css`
3. `frontend/src/components/common/Layout.jsx` - Agregado menú
4. `frontend/src/App.js` - Agregada ruta

### Base de Datos
1. `database/user_notifications_table.sql`
2. `create_notifications_table.py` - Script de creación

## Próximos Pasos

### Integración Completa
1. **Iniciar Consumer** en messaging-service
2. **Configurar Producer** en eventos cancelados
3. **Testing** de flujo completo
4. **Monitoreo** de Kafka topics

### Mejoras Futuras
- Push notifications en tiempo real
- Email notifications para eventos críticos
- Dashboard de administración de notificaciones
- Configuración de preferencias de usuario

## Uso del Sistema

### Para Cancelar un Evento
1. Ir a la lista de eventos
2. Seleccionar evento a cancelar
3. Proporcionar motivo de cancelación
4. Sistema notifica automáticamente a la red

### Para Ver Notificaciones
1. Hacer clic en "Notificaciones" en el menú
2. Ver lista de notificaciones ordenadas por fecha
3. Hacer clic para marcar como leída
4. Usar "Marcar todas como leídas" si es necesario

¡El sistema está listo para mantener a toda la red informada sobre cambios en eventos! 🎉