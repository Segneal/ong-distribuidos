# Frontend - Red de ONGs

Documentación del frontend para las funcionalidades de red de ONGs colaborativas.

## 🌐 Funcionalidades Implementadas

### 1. Página Principal de Red (`/network`)
- **Descripción**: Punto de entrada principal para todas las funcionalidades de red
- **Componente**: `src/pages/Network.jsx`
- **Características**:
  - Vista general de funcionalidades disponibles
  - Estadísticas de la red
  - Guía de primeros pasos
  - Navegación basada en permisos

### 2. Solicitudes de Donaciones (`/donation-requests`)
- **Descripción**: Gestión de solicitudes de donaciones entre organizaciones
- **Componente**: `src/pages/DonationRequests.jsx`
- **Características**:
  - Crear nuevas solicitudes de donaciones
  - Ver solicitudes de otras organizaciones
  - Gestionar solicitudes propias (cancelar)
  - Filtros por categoría y estado

### 3. Transferencias de Donaciones (`/donation-transfers`)
- **Descripción**: Historial y gestión de transferencias
- **Componente**: `src/pages/DonationTransfers.jsx`
- **Características**:
  - Historial completo de transferencias
  - Filtros por tipo (enviadas/recibidas)
  - Detalles de cada transferencia
  - Estado de las transferencias

### 4. Ofertas de Donaciones (`/donation-offers`)
- **Descripción**: Publicación y consulta de ofertas disponibles
- **Componente**: `src/pages/DonationOffers.jsx`
- **Características**:
  - Crear ofertas basadas en inventario
  - Ver ofertas de otras organizaciones
  - Búsqueda y filtros
  - Gestión de ofertas propias

### 5. Eventos Externos (`/external-events`)
- **Descripción**: Eventos de otras organizaciones y adhesiones
- **Componente**: `src/pages/ExternalEvents.jsx`
- **Características**:
  - Ver eventos de otras organizaciones
  - Adherirse como voluntario a eventos externos
  - Gestionar adhesiones propias
  - Filtros por fecha y estado

## 🧩 Componentes Principales

### Componentes de Red (`src/components/network/`)

#### 1. `DonationRequestForm.jsx`
- Formulario para crear solicitudes de donaciones
- Validación de campos obligatorios
- Soporte para múltiples donaciones por solicitud
- Categorías predefinidas

#### 2. `ExternalRequestsList.jsx`
- Lista de solicitudes de otras organizaciones
- Botón para transferir donaciones
- Filtros y búsqueda
- Información detallada de cada solicitud

#### 3. `ActiveRequestsList.jsx`
- Lista de solicitudes propias activas
- Opción para cancelar solicitudes
- Estado de cada solicitud
- Información de transferencias recibidas

#### 4. `DonationTransferForm.jsx`
- Formulario para transferir donaciones
- Selección de donaciones del inventario
- Validación de cantidades disponibles
- Confirmación de transferencia

#### 5. `TransferHistory.jsx`
- Historial completo de transferencias
- Filtros por tipo y fecha
- Detalles de cada transferencia
- Indicadores visuales de tipo

#### 6. `DonationOfferForm.jsx`
- Formulario para crear ofertas
- Selección de donaciones del inventario
- Especificación de cantidades
- Validación de disponibilidad

#### 7. `ExternalOffersList.jsx`
- Lista de ofertas de otras organizaciones
- Información detallada de cada oferta
- Filtros y búsqueda
- Contacto con organizaciones oferentes

#### 8. `ExternalEventList.jsx`
- Lista de eventos de otras organizaciones
- Información detallada de eventos
- Botón para adherirse como voluntario
- Filtros por fecha y tipo

#### 9. `VolunteerAdhesions.jsx`
- Lista de adhesiones del usuario
- Estado de cada adhesión
- Información del evento
- Opción para cancelar adhesiones

#### 10. `EventAdhesionManager.jsx`
- Gestión de adhesiones recibidas (para administradores)
- Lista de voluntarios externos adheridos
- Información de contacto
- Confirmación/rechazo de adhesiones

## 🎨 Estilos y Diseño

### Archivo CSS Principal
- **Ubicación**: `src/components/network/Network.css`
- **Características**:
  - Diseño responsivo para móviles y desktop
  - Esquema de colores consistente
  - Animaciones y transiciones suaves
  - Estados de loading y error

### Paleta de Colores
- **Primario**: `#3498db` (Azul)
- **Secundario**: `#2c3e50` (Azul oscuro)
- **Éxito**: `#27ae60` (Verde)
- **Advertencia**: `#f39c12` (Naranja)
- **Error**: `#e74c3c` (Rojo)
- **Texto**: `#2c3e50` / `#7f8c8d`

### Componentes de UI
- **Botones**: Estilo consistente con estados hover y disabled
- **Tarjetas**: Sombras y bordes redondeados
- **Formularios**: Validación visual y mensajes de error
- **Navegación**: Tabs para organizar contenido

## 🔐 Control de Acceso

### Permisos por Rol

#### PRESIDENTE
- ✅ Acceso completo a todas las funcionalidades
- ✅ Gestión de solicitudes, transferencias y ofertas
- ✅ Gestión de eventos y adhesiones
- ✅ Vista de estadísticas y reportes

#### VOCAL
- ✅ Gestión de inventario y donaciones
- ✅ Solicitudes y transferencias de donaciones
- ✅ Ofertas de donaciones
- ❌ Gestión de eventos (solo lectura)

#### COORDINADOR
- ✅ Gestión de eventos y adhesiones
- ✅ Vista de solicitudes y ofertas (solo lectura)
- ❌ Transferencias de donaciones

#### VOLUNTARIO
- ✅ Vista de eventos externos
- ✅ Adhesión a eventos externos
- ✅ Vista de solicitudes y ofertas (solo lectura)
- ❌ Creación de solicitudes o ofertas

### Implementación de Permisos
```jsx
// Ejemplo de uso en componentes
const { hasPermission } = useAuth();

if (hasPermission('inventory', 'write')) {
  // Mostrar botón de transferir donaciones
}

if (hasPermission('events', 'read')) {
  // Mostrar eventos externos
}
```

## 📱 Diseño Responsivo

### Breakpoints
- **Desktop**: `> 768px`
- **Tablet**: `768px - 480px`
- **Mobile**: `< 480px`

### Adaptaciones Móviles
- **Navegación**: Tabs verticales en móvil
- **Tarjetas**: Stack vertical en pantallas pequeñas
- **Formularios**: Campos de ancho completo
- **Botones**: Tamaño táctil apropiado

## 🔄 Estados de la Aplicación

### Estados de Carga
- **Loading**: Spinner con mensaje descriptivo
- **Empty**: Mensajes informativos cuando no hay datos
- **Error**: Mensajes de error con opciones de reintento

### Validación de Formularios
- **Tiempo real**: Validación mientras el usuario escribe
- **Envío**: Validación completa antes del envío
- **Mensajes**: Errores específicos por campo

## 🚀 Integración con Backend

### Servicios API (`src/services/api.js`)
```javascript
// Ejemplo de servicio
export const messagingService = {
  createDonationRequest: (requestData) => 
    api.post('/messaging/create-donation-request', requestData),
  
  getExternalRequests: (params = {}) => 
    api.post('/messaging/external-requests', params),
  
  transferDonations: (transferData) => 
    api.post('/messaging/transfer-donations', transferData)
};
```

### Manejo de Errores
- **Interceptores**: Manejo automático de errores 401/403
- **Retry**: Reintentos automáticos para errores temporales
- **Feedback**: Mensajes de error amigables al usuario

## 🧪 Testing

### Componentes a Testear
1. **Formularios**: Validación y envío
2. **Listas**: Filtros y paginación
3. **Navegación**: Rutas y permisos
4. **Estados**: Loading, error, empty

### Ejemplo de Test
```javascript
// Ejemplo de test para DonationRequestForm
describe('DonationRequestForm', () => {
  test('should validate required fields', () => {
    // Test de validación
  });
  
  test('should submit form with valid data', () => {
    // Test de envío exitoso
  });
});
```

## 📋 Checklist de Implementación

### ✅ Completado
- [x] Página principal de red
- [x] Solicitudes de donaciones
- [x] Transferencias de donaciones
- [x] Ofertas de donaciones
- [x] Eventos externos
- [x] Adhesiones a eventos
- [x] Control de permisos
- [x] Diseño responsivo
- [x] Integración con API
- [x] Manejo de errores
- [x] Validación de formularios

### 🔄 Mejoras Futuras
- [ ] Notificaciones push
- [ ] Chat entre organizaciones
- [ ] Mapas de ubicación
- [ ] Exportación de reportes
- [ ] Dashboard de métricas
- [ ] Integración con redes sociales

## 🛠️ Desarrollo

### Estructura de Archivos
```
frontend/src/
├── components/
│   ├── network/           # Componentes de red
│   │   ├── *.jsx         # Componentes React
│   │   └── Network.css   # Estilos
│   └── auth/             # Componentes de autenticación
├── pages/                # Páginas principales
│   ├── Network.jsx       # Página principal de red
│   ├── DonationRequests.jsx
│   ├── DonationTransfers.jsx
│   ├── DonationOffers.jsx
│   └── ExternalEvents.jsx
├── services/             # Servicios API
│   └── api.js           # Configuración y endpoints
└── contexts/            # Contextos React
    └── AuthContext.jsx  # Contexto de autenticación
```

### Comandos de Desarrollo
```bash
# Instalar dependencias
npm install

# Iniciar desarrollo
npm start

# Ejecutar tests
npm test

# Build para producción
npm run build
```

## 📞 Soporte

Para soporte técnico o consultas sobre el frontend:
- **Email**: dev@empujecomunitario.org
- **Documentación**: Ver carpeta `docs/`
- **Issues**: Crear issue en el repositorio

---

**Última actualización**: Enero 2024  
**Versión**: 1.0.0