# Prueba del Frontend - Red de ONGs

## 🧪 Pasos para Probar la Funcionalidad de Red de ONGs

### 1. Acceder al Sistema
1. Abrir navegador en: http://localhost:3001
2. Hacer login con credenciales de prueba:
   - **Usuario**: admin@empujecomunitario.org
   - **Contraseña**: admin123

### 2. Verificar Navegación
Una vez logueado, deberías ver en el menú lateral:
- ✅ **Inicio**
- ✅ **Usuarios** (solo PRESIDENTE)
- ✅ **Inventario** (PRESIDENTE/VOCAL)
- ✅ **Red de ONGs** ← **ESTA ES LA NUEVA FUNCIONALIDAD**
- ✅ **Solicitudes Red** (PRESIDENTE/VOCAL)
- ✅ **Transferencias** (PRESIDENTE/VOCAL)
- ✅ **Ofertas Red** (PRESIDENTE/VOCAL)
- ✅ **Eventos** (PRESIDENTE/COORDINADOR/VOLUNTARIO)
- ✅ **Eventos Externos** (PRESIDENTE/COORDINADOR/VOLUNTARIO)

### 3. Probar Red de ONGs
Hacer clic en **"Red de ONGs"** para acceder a:
- 📋 Vista general de la red
- 🌐 Estadísticas de colaboración
- 🎯 Acceso a todas las funcionalidades
- 📚 Guía de primeros pasos

### 4. Probar Funcionalidades Específicas

#### A. Solicitudes de Donaciones
1. Ir a **"Solicitudes Red"**
2. Crear nueva solicitud
3. Ver solicitudes externas
4. Gestionar solicitudes propias

#### B. Transferencias
1. Ir a **"Transferencias"**
2. Ver historial completo
3. Filtrar por tipo (enviadas/recibidas)

#### C. Ofertas de Donaciones
1. Ir a **"Ofertas Red"**
2. Crear nueva oferta
3. Explorar ofertas disponibles

#### D. Eventos Externos
1. Ir a **"Eventos Externos"**
2. Ver eventos de otras organizaciones
3. Adherirse como voluntario

### 5. Verificar Permisos por Rol

#### PRESIDENTE (admin@empujecomunitario.org)
- ✅ Acceso completo a todas las funcionalidades
- ✅ Puede crear solicitudes, ofertas y transferencias
- ✅ Puede gestionar eventos y adhesiones

#### VOCAL (vocal@empujecomunitario.org)
- ✅ Acceso a inventario y donaciones
- ✅ Puede crear solicitudes y ofertas
- ✅ Puede realizar transferencias
- ❌ No puede gestionar eventos (solo ver)

#### COORDINADOR (coordinador@empujecomunitario.org)
- ✅ Acceso a eventos y adhesiones
- ✅ Puede ver solicitudes y ofertas
- ❌ No puede crear transferencias

#### VOLUNTARIO (voluntario@empujecomunitario.org)
- ✅ Puede ver eventos externos
- ✅ Puede adherirse a eventos
- ✅ Puede ver solicitudes y ofertas
- ❌ No puede crear solicitudes o ofertas

### 6. Verificar Diseño Responsivo
- 💻 **Desktop**: Navegación lateral fija
- 📱 **Móvil**: Menú hamburguesa
- 📱 **Tablet**: Adaptación automática

### 7. Verificar Estados de la Aplicación
- ⏳ **Loading**: Spinners durante carga
- 📭 **Empty**: Mensajes cuando no hay datos
- ❌ **Error**: Manejo de errores con opciones de reintento
- ✅ **Success**: Confirmaciones de acciones exitosas

## 🔧 Troubleshooting

### Si no ves "Red de ONGs" en el menú:
1. Verificar que estés logueado
2. Refrescar la página (F5)
3. Limpiar cache del navegador
4. Verificar que el contenedor frontend esté ejecutándose:
   ```bash
   docker-compose ps frontend
   ```

### Si hay errores de conectividad:
1. Verificar que todos los servicios estén ejecutándose:
   ```bash
   docker-compose ps
   ```
2. Verificar logs del frontend:
   ```bash
   docker-compose logs frontend
   ```
3. Verificar logs del API gateway:
   ```bash
   docker-compose logs api-gateway
   ```

### Si las funcionalidades no cargan:
1. Verificar que el messaging-service esté ejecutándose:
   ```bash
   docker-compose ps messaging-service
   ```
2. Verificar conectividad con Kafka:
   ```bash
   docker-compose logs kafka
   ```

## 📋 Checklist de Verificación

### ✅ Navegación
- [ ] Menú "Red de ONGs" visible
- [ ] Todas las sub-funcionalidades accesibles
- [ ] Permisos funcionando correctamente

### ✅ Funcionalidades
- [ ] Solicitudes de donaciones
- [ ] Transferencias de donaciones
- [ ] Ofertas de donaciones
- [ ] Eventos externos
- [ ] Adhesiones a eventos

### ✅ UX/UI
- [ ] Diseño responsivo
- [ ] Formularios con validación
- [ ] Estados de loading/error
- [ ] Navegación intuitiva

### ✅ Integración
- [ ] API calls funcionando
- [ ] Datos cargando correctamente
- [ ] Errores manejados apropiadamente

## 🎉 Resultado Esperado

Al completar estas pruebas, deberías poder:
1. **Navegar** fácilmente por todas las funcionalidades de red
2. **Crear** solicitudes y ofertas de donaciones
3. **Transferir** donaciones entre organizaciones
4. **Participar** en eventos de otras ONGs
5. **Gestionar** adhesiones de voluntarios

¡La red de ONGs colaborativas está lista para conectar organizaciones y maximizar el impacto social! 🌟