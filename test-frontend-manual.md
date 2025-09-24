# 🧪 Guía de Pruebas Manuales del Frontend

## 🚀 Inicio Rápido

1. **Levantar el sistema:**
   ```bash
   docker-compose up --build -d
   # O usar los scripts: .\start-services.ps1
   ```

2. **Abrir el frontend:** http://localhost:3000

## 📋 Lista de Verificación Rápida (5 minutos)

### ✅ 1. Login y Autenticación
- [ ] Ir a http://localhost:3000
- [ ] Debería mostrar formulario de login
- [ ] Login con: `admin` / `admin123`
- [ ] Debería redirigir al dashboard
- [ ] Verificar que muestra "Bienvenido, Juan Pérez" (nombre del admin)

### ✅ 2. Navegación Principal
- [ ] Verificar menú lateral con opciones:
  - [ ] Dashboard/Inicio
  - [ ] Usuarios (solo admin)
  - [ ] Inventario
  - [ ] Eventos
- [ ] Hacer clic en cada sección y verificar que carga

### ✅ 3. Gestión de Usuarios (Solo Admin)
- [ ] Ir a "Usuarios"
- [ ] Debería mostrar lista de usuarios existentes
- [ ] Hacer clic en "Agregar Usuario"
- [ ] Llenar formulario de prueba:
  - Username: `test_user`
  - Email: `test@test.com`
  - Nombre: `Usuario Test`
  - Rol: `VOLUNTARIO`
  - Contraseña: `test123`
- [ ] Guardar y verificar que aparece en la lista
- [ ] Editar el usuario creado
- [ ] Eliminar el usuario de prueba

### ✅ 4. Gestión de Inventario
- [ ] Ir a "Inventario"
- [ ] Debería mostrar items existentes (si los hay)
- [ ] Hacer clic en "Registrar Donación"
- [ ] Llenar formulario:
  - Donante: `Donante Prueba`
  - Email: `donante@test.com`
  - Teléfono: `123456789`
  - Agregar item:
    - Nombre: `Arroz`
    - Cantidad: `10`
    - Unidad: `kg`
    - Categoría: `ALIMENTOS`
    - Fecha vencimiento: `2024-12-31`
- [ ] Guardar y verificar que aparece en inventario

### ✅ 5. Gestión de Eventos
- [ ] Ir a "Eventos"
- [ ] Debería mostrar eventos existentes (si los hay)
- [ ] Hacer clic en "Crear Evento"
- [ ] Llenar formulario:
  - Nombre: `Evento de Prueba`
  - Descripción: `Evento para probar el sistema`
  - Fecha: `2024-12-25`
  - Hora: `10:00`
  - Ubicación: `Centro Comunitario`
  - Máx. participantes: `50`
  - Tipo: `DISTRIBUCION`
- [ ] Guardar evento
- [ ] Hacer clic en el evento creado
- [ ] Verificar botón "Participar" y hacer clic
- [ ] Verificar que aparece en "Mis Participaciones"

### ✅ 6. Pruebas de Roles Diferentes

#### Como Coordinador:
- [ ] Logout del admin
- [ ] Login con: `coord1` / `admin123`
- [ ] Verificar que NO ve opción "Usuarios"
- [ ] Verificar que NO ve "Inventario"
- [ ] Verificar que SÍ ve "Eventos" con permisos completos

#### Como Voluntario:
- [ ] Logout del coordinador
- [ ] Login con: `vol1` / `admin123`
- [ ] Verificar que solo ve "Eventos"
- [ ] Verificar que NO puede crear/editar eventos
- [ ] Verificar que SÍ puede participar en eventos

### ✅ 7. Funcionalidades Avanzadas de Eventos

#### Gestión de Participantes (como admin/coordinador):
- [ ] Login como admin
- [ ] Ir a un evento
- [ ] Hacer clic en "Gestionar Participantes"
- [ ] Verificar lista de participantes
- [ ] Probar agregar/quitar participantes

#### Donaciones Distribuidas:
- [ ] En un evento, hacer clic en "Donaciones Distribuidas"
- [ ] Verificar que muestra items del inventario
- [ ] Probar marcar items como distribuidos

## 🐛 Problemas Comunes y Soluciones

### Frontend no carga:
```bash
# Verificar que el frontend esté corriendo
docker-compose ps
# Debería mostrar frontend_1 como "Up"
```

### Error de conexión API:
```bash
# Verificar API Gateway
curl http://localhost:3001/health
# Debería responder con status OK
```

### Error de autenticación:
- Verificar que los microservicios estén corriendo
- Revisar logs: `docker-compose logs api-gateway`

### Base de datos vacía:
```bash
# Reinicializar datos de prueba
docker-compose exec database psql -U ong_user -d ong_management -f /docker-entrypoint-initdb.d/sample_data.sql
```

## 📊 Verificación de Logs

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs específicos
docker-compose logs -f frontend
docker-compose logs -f api-gateway
docker-compose logs -f user-service
```

## 🎯 Criterios de Éxito

✅ **Sistema funcionando correctamente si:**
- Login funciona con todos los roles
- Navegación fluida entre secciones
- CRUD completo en cada módulo según permisos
- Roles y permisos funcionan correctamente
- No hay errores en consola del navegador
- Datos se persisten correctamente

❌ **Revisar si:**
- Errores 500 en peticiones
- Pantallas en blanco
- Botones que no responden
- Datos que no se guardan
- Permisos incorrectos

## ⏱️ Tiempo Estimado

- **Prueba básica:** 5 minutos
- **Prueba completa:** 15 minutos
- **Prueba exhaustiva con todos los roles:** 30 minutos