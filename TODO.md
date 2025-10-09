# TODO - Sistema ONG Multi-Organización

## 🔔 Sistema de Aprobación de Adhesiones a Eventos

### Descripción
Cuando alguien se adhiere a un evento externo, debe aparecer como "pendiente" y los PRESIDENTE/VOCAL de la organización que organiza el evento deben poder aceptar o rechazar la adhesión.

### Funcionalidades Requeridas

#### 1. **Notificaciones en Campanita**
- [ ] Cuando alguien se adhiere a un evento, debe aparecer notificación en la campanita del PRESIDENTE/VOCAL
- [ ] La notificación debe mostrar: nombre del voluntario, evento, organización de origen
- [ ] Contador de adhesiones pendientes en la campanita

#### 2. **Panel de Gestión de Adhesiones**
- [ ] Crear componente `PendingEventAdhesions.jsx` para PRESIDENTE/VOCAL
- [ ] Mostrar lista de adhesiones pendientes con:
  - Nombre y datos del voluntario
  - Evento al que se quiere adherir
  - Organización de origen del voluntario
  - Fecha de solicitud
  - Botones: Aceptar / Rechazar

#### 3. **Estados de Adhesión**
- [ ] **PENDIENTE**: Recién enviada, esperando aprobación
- [ ] **ACEPTADA**: Aprobada por PRESIDENTE/VOCAL
- [ ] **RECHAZADA**: Rechazada por PRESIDENTE/VOCAL

#### 4. **Backend - Kafka Integration**
- [ ] Producer para enviar notificaciones de adhesión
- [ ] Consumer para procesar aprobaciones/rechazos
- [ ] Actualizar `adhesion_service.py` para manejar estados

#### 5. **Base de Datos**
- [ ] Verificar que tabla `adhesiones_eventos_externos` tenga campo `estado`
- [ ] Agregar tabla de notificaciones para adhesiones si no existe
- [ ] Migración para actualizar estados existentes

#### 6. **API Endpoints**
- [ ] `GET /api/messaging/pending-adhesions` - Obtener adhesiones pendientes
- [ ] `POST /api/messaging/process-adhesion` - Aprobar/rechazar adhesión
- [ ] `GET /api/messaging/adhesion-notifications` - Notificaciones de adhesiones

#### 7. **Frontend Updates**
- [ ] Actualizar `NotificationBell.jsx` para mostrar adhesiones pendientes
- [ ] Crear página/modal para gestionar adhesiones
- [ ] Actualizar `ExternalEventList.jsx` para mostrar estado de adhesión
- [ ] Agregar indicadores visuales de estado (pendiente/aceptada/rechazada)

### Flujo Completo
```
1. Voluntario se adhiere a evento externo
2. Se crea adhesión con estado PENDIENTE
3. Se envía mensaje Kafka a organización del evento
4. PRESIDENTE/VOCAL recibe notificación en campanita
5. PRESIDENTE/VOCAL va al panel de adhesiones
6. Aprueba o rechaza la adhesión
7. Se actualiza estado en BD
8. Se envía notificación de vuelta al voluntario
9. Voluntario ve estado actualizado en su panel
```

### Prioridad
🔥 **ALTA** - Funcionalidad core para el sistema de red de ONGs

---

## 📋 Otros TODOs

### Sistema de Solicitudes de Inscripción
- [x] ✅ Implementado completamente
- [x] ✅ Formulario público de solicitud
- [x] ✅ Panel de aprobación para PRESIDENTE/VOCAL
- [x] ✅ Notificaciones via Kafka
- [x] ✅ Creación automática de usuarios

### Filtrado de Eventos Externos
- [x] ✅ Corregido filtrado por organización
- [x] ✅ Eventos propios vs externos se muestran correctamente
- [x] ✅ Ordenamiento dinámico por organización del usuario

### Mejoras Futuras
- [ ] Dashboard de métricas de red
- [ ] Reportes de actividad inter-organizacional
- [ ] Sistema de ratings/reviews entre organizaciones
- [ ] Integración con calendarios externos
- [ ] Notificaciones push en tiempo real
- [ ] Sistema de mensajería directa entre organizaciones
- [ ] Workflow de aprobación multi-nivel para transferencias grandes
- [ ] Geolocalización de eventos y organizaciones
- [ ] Sistema de badges/reconocimientos para voluntarios activos
- [ ] API pública para integraciones externas

---

## 🐛 Bugs Conocidos
- [ ] Verificar que todos los eventos huérfanos estén limpiados
- [ ] Optimizar consultas de eventos externos para mejor performance
- [ ] Validar que todos los filtros por organización funcionen correctamente

---

## 🔧 Refactoring Técnico
- [ ] Consolidar repositorios de red (hay múltiples archivos)
- [ ] Mejorar manejo de errores en Kafka consumers
- [ ] Agregar tests automatizados para flujos multi-organización
- [ ] Documentar APIs con Swagger/OpenAPI
- [ ] Implementar rate limiting en APIs públicas
- [ ] Agregar monitoring y logging estructurado