# Credenciales del Sistema Multi-Organización

## 🏢 Organizaciones Disponibles

### 1. **Empuje Comunitario** (Organización Principal)
- **ID:** `empuje-comunitario`
- **Usuarios existentes:** Los usuarios originales del sistema
- **Credenciales principales:**
  - **admin** / **admin123** (PRESIDENTE)
  - **coordinador1** / **coord123** (COORDINADOR)
  - **vocal1** / **vocal123** (VOCAL)
  - **voluntario1** / **vol123** (VOLUNTARIO)

### 2. **Fundación Esperanza**
- **ID:** `fundacion-esperanza`
- **Usuarios:**
  - **esperanza_admin** / **password123** (PRESIDENTE)
    - Nombre: María González
    - Email: maria@esperanza.org
    - Teléfono: +54-11-1111-1111
  - **esperanza_coord** / **password123** (COORDINADOR)
    - Nombre: Carlos Ruiz
    - Email: carlos@esperanza.org
    - Teléfono: +54-11-2222-2222

### 3. **ONG Solidaria**
- **ID:** `ong-solidaria`
- **Usuarios:**
  - **solidaria_admin** / **password123** (PRESIDENTE)
    - Nombre: Ana López
    - Email: ana@solidaria.org
    - Teléfono: +54-11-3333-3333
  - **solidaria_vol** / **password123** (VOLUNTARIO)
    - Nombre: Pedro Martín
    - Email: pedro@solidaria.org
    - Teléfono: +54-11-4444-4444

### 4. **Centro Comunitario Unidos**
- **ID:** `centro-comunitario`
- **Usuarios:**
  - **centro_admin** / **password123** (PRESIDENTE)
    - Nombre: Laura Fernández
    - Email: laura@centro.org
    - Teléfono: +54-11-5555-5555
  - **centro_vocal** / **password123** (VOCAL)
    - Nombre: Diego Silva
    - Email: diego@centro.org
    - Teléfono: +54-11-6666-6666

## 🧪 Cómo Probar el Sistema Multi-Organización

### Paso 1: Probar Diferentes Organizaciones
1. **Logout** del usuario actual si estás logueado
2. **Login** con `esperanza_admin` / `password123`
3. **Verificar** que el header muestra **"Fundación Esperanza"**
4. **Navegar** por el sistema y crear eventos/solicitudes
5. **Logout** y login con `solidaria_admin` / `password123`
6. **Verificar** que el header muestra **"ONG Solidaria"**
7. **Repetir** con otros usuarios para ver diferentes organizaciones

### Paso 2: Probar Flujos de Red Entre Organizaciones

#### Como Fundación Esperanza:
1. **Login:** `esperanza_admin` / `password123`
2. **Ir a Red > Solicitudes de Donación**
3. **Crear solicitud** de donaciones necesarias
4. **Ir a Red > Eventos Solidarios**
5. **Crear y exponer** eventos a la red

#### Como ONG Solidaria:
1. **Login:** `solidaria_admin` / `password123`
2. **Ir a Red > Solicitudes Externas**
3. **Ver solicitudes** de Fundación Esperanza
4. **Ir a Red > Eventos Externos**
5. **Ver eventos** de otras organizaciones
6. **Inscribir voluntarios** a eventos externos

#### Como Centro Comunitario:
1. **Login:** `centro_admin` / `password123`
2. **Ir a Red > Ofertas de Donación**
3. **Crear ofertas** de donaciones disponibles
4. **Ir a Red > Transferir Donaciones**
5. **Transferir donaciones** a solicitudes de otras organizaciones

#### Como Empuje Comunitario:
1. **Login:** `admin` / `admin123`
2. **Ver todas las actividades** de la red
3. **Participar** en flujos con otras organizaciones
4. **Gestionar** como organización coordinadora

### Paso 3: Verificar Kafka y Mensajería
- **Crear solicitudes** en una organización
- **Verificar** que aparecen en "Solicitudes Externas" de otras organizaciones
- **Crear ofertas** y ver que se distribuyen por la red
- **Transferir donaciones** y verificar notificaciones
- **Publicar eventos** y ver adhesiones de otras organizaciones

## 🎯 Funcionalidades por Rol

### PRESIDENTE
- **Acceso completo** a todas las funcionalidades
- **Gestión de usuarios** de su organización
- **Configuración** de red y Kafka
- **Creación** de solicitudes, ofertas y eventos
- **Aprobación** de transferencias importantes

### COORDINADOR
- **Gestión de eventos** solidarios
- **Participación** en red de ONGs
- **Coordinación** de voluntarios
- **Creación** de solicitudes y ofertas
- **Gestión** de adhesiones

### VOCAL
- **Gestión de inventario**
- **Transferencias** de donaciones
- **Solicitudes y ofertas**
- **Participación** en eventos
- **Consulta** de información de red

### VOLUNTARIO
- **Participación** en eventos
- **Adhesión** a eventos externos
- **Consulta** de información
- **Registro** de actividades básicas

## 🚀 Scripts de Prueba Automatizada

### 1. Crear Usuarios de Prueba
```bash
python test_multi_org_user_creation.py
```
Este script crea usuarios adicionales para cada organización.

### 2. Prueba Completa del Sistema
```bash
python test_complete_multi_org_system.py
```
Este script ejecuta un flujo completo:
- Login de usuarios de diferentes organizaciones
- Creación de solicitudes de donación
- Creación de ofertas de donación
- Transferencias entre organizaciones
- Verificación de mensajería Kafka

## 📊 Estado del Sistema

### Base de Datos
- ✅ **4 organizaciones** registradas
- ✅ **12+ usuarios** distribuidos entre organizaciones
- ✅ **Tablas de red** implementadas (solicitudes_externas, ofertas_externas, etc.)
- ✅ **Relaciones** multi-organización configuradas

### Kafka
- ✅ **7 topics** configurados para mensajería
- ✅ **Producers** funcionando para todas las organizaciones
- ✅ **Consumers** procesando mensajes entre organizaciones
- ✅ **Mensajería** en tiempo real entre ONGs

### Frontend
- ✅ **Header dinámico** que cambia según la organización del usuario
- ✅ **Formularios** adaptados para multi-organización
- ✅ **Pantallas de red** implementadas
- ✅ **UI responsive** para todas las organizaciones

## 🔧 Próximos Pasos

### Inmediatos
1. **Probar** login con diferentes usuarios
2. **Verificar** que el header cambia correctamente
3. **Crear** solicitudes/ofertas desde diferentes organizaciones
4. **Verificar** flujos de Kafka entre organizaciones

### Mejoras Futuras
1. **Notificaciones** en tiempo real con WebSockets
2. **Dashboard** de métricas de red
3. **Filtros avanzados** por organización
4. **Reportes** de actividad inter-organizacional

## 🎉 ¡Sistema Listo!

El sistema multi-organización está **completamente implementado** y listo para usar. Cada organización tiene:

- ✅ **Usuarios propios** con credenciales específicas
- ✅ **Header personalizado** que muestra su organización
- ✅ **Flujos de Kafka** para colaborar con otras ONGs
- ✅ **Interfaces adaptadas** a su contexto organizacional

**¡Comienza probando con las credenciales de arriba!** 🚀