# Sistema de Solicitudes de Inscripción

## 🎯 Descripción General

Sistema completo para gestionar solicitudes de inscripción de nuevos usuarios a las organizaciones, utilizando Kafka para notificaciones en tiempo real a PRESIDENTE y VOCAL, quienes pueden aprobar o denegar las solicitudes.

## 🏗️ Arquitectura del Sistema

### Componentes Principales

1. **Frontend (React)**
   - Formulario de solicitud de inscripción
   - Panel de gestión para PRESIDENTE/VOCAL
   - Notificaciones en tiempo real

2. **API Gateway (Node.js)**
   - Rutas para solicitudes de inscripción
   - Autenticación y autorización
   - Proxy al messaging service

3. **Messaging Service (Python/FastAPI)**
   - Lógica de negocio
   - Integración con Kafka
   - Gestión de base de datos

4. **Kafka**
   - Topics: `inscription-requests`, `inscription-responses`
   - Notificaciones asíncronas
   - Procesamiento distribuido

5. **Base de Datos (MySQL)**
   - Tabla `solicitudes_inscripcion`
   - Tabla `notificaciones_solicitudes`

## 📊 Flujo del Sistema

### 1. Solicitud de Inscripción
```
Usuario Externo → Formulario → API Gateway → Messaging Service → Base de Datos → Kafka Producer
```

### 2. Notificación a Administradores
```
Kafka Consumer → Base de Datos (notificaciones) → PRESIDENTE/VOCAL reciben notificación
```

### 3. Procesamiento de Solicitud
```
PRESIDENTE/VOCAL → Aprobar/Denegar → API Gateway → Messaging Service → Kafka Producer → Consumer → Crear Usuario (si aprobada)
```

## 🗄️ Estructura de Base de Datos

### Tabla: `solicitudes_inscripcion`
```sql
CREATE TABLE solicitudes_inscripcion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    solicitud_id VARCHAR(100) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    organizacion_destino VARCHAR(100) NOT NULL,
    rol_solicitado ENUM('COORDINADOR', 'VOLUNTARIO') NOT NULL,
    mensaje TEXT,
    estado ENUM('PENDIENTE', 'APROBADA', 'DENEGADA') DEFAULT 'PENDIENTE',
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_respuesta TIMESTAMP NULL,
    usuario_revisor INT NULL,
    comentarios_revisor TEXT,
    datos_adicionales JSON
);
```

### Tabla: `notificaciones_solicitudes`
```sql
CREATE TABLE notificaciones_solicitudes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    solicitud_id VARCHAR(100) NOT NULL,
    usuario_destinatario INT NOT NULL,
    tipo_notificacion ENUM('NUEVA_SOLICITUD', 'SOLICITUD_APROBADA', 'SOLICITUD_DENEGADA') NOT NULL,
    leida BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔌 API Endpoints

### API Gateway (Puerto 3001)

#### POST `/api/messaging/inscription-request`
Crear nueva solicitud de inscripción (sin autenticación)

**Request Body:**
```json
{
  "nombre": "Juan Carlos",
  "apellido": "Pérez",
  "email": "juan.perez@email.com",
  "telefono": "+54911555666",
  "organizacion_destino": "empuje-comunitario",
  "rol_solicitado": "VOLUNTARIO",
  "mensaje": "Me interesa colaborar..."
}
```

#### GET `/api/messaging/pending-inscriptions`
Obtener solicitudes pendientes (requiere autenticación PRESIDENTE/VOCAL)

#### POST `/api/messaging/process-inscription`
Procesar solicitud - aprobar/denegar (requiere autenticación PRESIDENTE/VOCAL)

**Request Body:**
```json
{
  "solicitud_id": "INS-20251006-ABC123",
  "accion": "APROBAR",
  "comentarios": "Bienvenido al equipo"
}
```

#### GET `/api/messaging/inscription-notifications`
Obtener notificaciones de inscripción (requiere autenticación PRESIDENTE/VOCAL)

### Messaging Service (Puerto 50054)

#### POST `/api/inscription-request`
Crear solicitud de inscripción

#### GET `/api/pending-inscriptions`
Obtener solicitudes pendientes

#### POST `/api/process-inscription`
Procesar solicitud

#### GET `/api/inscription-notifications`
Obtener notificaciones

## 📨 Mensajes de Kafka

### Topic: `inscription-requests`
```json
{
  "event_type": "NUEVA_SOLICITUD_INSCRIPCION",
  "timestamp": "2025-10-06T01:30:00.000Z",
  "solicitud_id": "INS-20251006-ABC123",
  "organizacion_destino": "empuje-comunitario",
  "solicitante": {
    "nombre": "Juan Carlos",
    "apellido": "Pérez",
    "email": "juan.perez@email.com",
    "telefono": "+54911555666",
    "rol_solicitado": "VOLUNTARIO",
    "mensaje": "Me interesa colaborar..."
  }
}
```

### Topic: `inscription-responses`
```json
{
  "event_type": "SOLICITUD_APROBADA",
  "timestamp": "2025-10-06T01:35:00.000Z",
  "solicitud_id": "INS-20251006-ABC123",
  "organizacion": "empuje-comunitario",
  "estado": "APROBADA",
  "revisor": {
    "id": 1,
    "nombre": "admin",
    "rol": "PRESIDENTE"
  },
  "comentarios": "Bienvenido al equipo"
}
```

## 🎨 Componentes Frontend

### `InscriptionRequestForm.jsx`
- Formulario público para solicitar inscripción
- Validación de campos
- Selección de organización y rol
- Envío sin autenticación

### `PendingInscriptions.jsx`
- Panel para PRESIDENTE/VOCAL
- Lista de solicitudes pendientes
- Botones de aprobar/denegar
- Actualización en tiempo real

### `Inscriptions.css`
- Estilos responsivos
- Diseño moderno
- Estados de carga y error

## 🚀 Instalación y Configuración

### 1. Aplicar Migración de Base de Datos
```bash
python apply_inscription_migration.py
```

### 2. Iniciar Consumer de Kafka
```bash
python start_inscription_consumer.py
```

### 3. Verificar Servicios
- API Gateway: `http://localhost:3001`
- Messaging Service: `http://localhost:50054`
- Frontend: `http://localhost:3000`

## 🧪 Testing

### Script de Prueba Completo
```bash
python test_inscription_system.py
```

Este script prueba:
1. ✅ Creación de solicitud
2. ✅ Login como PRESIDENTE
3. ✅ Obtención de solicitudes pendientes
4. ✅ Aprobación de solicitud
5. ✅ Verificación de notificaciones

### Prueba Manual

#### 1. Crear Solicitud (Frontend)
1. Ir a la página de inscripción
2. Llenar formulario
3. Enviar solicitud

#### 2. Gestionar Solicitudes (PRESIDENTE/VOCAL)
1. Login como `admin` / `admin123`
2. Ir a panel de solicitudes
3. Aprobar/denegar solicitudes

## 🔐 Permisos y Roles

### Roles Autorizados
- **PRESIDENTE**: Puede ver y procesar todas las solicitudes
- **VOCAL**: Puede ver y procesar todas las solicitudes
- **COORDINADOR**: Sin acceso
- **VOLUNTARIO**: Sin acceso

### Flujo de Permisos
1. **Solicitud**: Cualquier persona (sin autenticación)
2. **Visualización**: Solo PRESIDENTE/VOCAL de la organización destino
3. **Procesamiento**: Solo PRESIDENTE/VOCAL de la organización destino
4. **Notificaciones**: Solo PRESIDENTE/VOCAL

## 📈 Características del Sistema

### ✅ Funcionalidades Implementadas
- ✅ Formulario de solicitud público
- ✅ Validación de datos
- ✅ Envío a Kafka
- ✅ Notificaciones automáticas a PRESIDENTE/VOCAL
- ✅ Panel de gestión para administradores
- ✅ Aprobación/denegación con comentarios
- ✅ Creación automática de usuario al aprobar
- ✅ Historial de notificaciones
- ✅ Interfaz responsive
- ✅ Manejo de errores

### 🔄 Flujo de Estados
```
PENDIENTE → APROBADA → Usuario creado
         → DENEGADA → Fin del proceso
```

### 🎯 Casos de Uso

#### Caso 1: Solicitud Exitosa
1. Usuario llena formulario
2. Sistema valida datos
3. Se crea solicitud en BD
4. Se envía mensaje a Kafka
5. PRESIDENTE/VOCAL reciben notificación
6. Administrador aprueba solicitud
7. Se crea usuario automáticamente
8. Usuario recibe credenciales (futuro)

#### Caso 2: Solicitud Denegada
1. Usuario llena formulario
2. Sistema valida datos
3. Se crea solicitud en BD
4. Se envía mensaje a Kafka
5. PRESIDENTE/VOCAL reciben notificación
6. Administrador deniega con comentarios
7. Solicitud marcada como denegada

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Messaging Service
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=ong_management
MYSQL_USER=root
MYSQL_PASSWORD=root

# API Gateway
MESSAGING_SERVICE_URL=http://localhost:50054
JWT_SECRET=your-secret-key
```

### Topics de Kafka
- `inscription-requests`: Nuevas solicitudes
- `inscription-responses`: Respuestas a solicitudes

## 📝 Próximas Mejoras

### Funcionalidades Futuras
- [ ] Envío de emails automáticos
- [ ] Notificaciones push en tiempo real
- [ ] Dashboard de métricas
- [ ] Filtros avanzados
- [ ] Exportación de reportes
- [ ] Integración con sistema de usuarios
- [ ] Workflow de aprobación multi-nivel
- [ ] Templates de respuesta
- [ ] Historial de cambios

### Optimizaciones Técnicas
- [ ] Cache de solicitudes frecuentes
- [ ] Paginación de resultados
- [ ] Compresión de mensajes Kafka
- [ ] Monitoreo de performance
- [ ] Tests automatizados
- [ ] Documentación API con Swagger

## 🎉 Conclusión

El sistema de solicitudes de inscripción está **completamente implementado** y funcional:

- ✅ **Backend completo** con Kafka y base de datos
- ✅ **Frontend responsive** con formularios y paneles
- ✅ **API Gateway** con autenticación y autorización
- ✅ **Notificaciones en tiempo real** via Kafka
- ✅ **Gestión de permisos** por rol
- ✅ **Testing automatizado** incluido

**¡El sistema está listo para usar!** 🚀