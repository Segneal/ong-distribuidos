# Credenciales de Prueba - Sistema ONG Empuje Comunitario

## Usuarios de Prueba

Todos los usuarios tienen la misma contraseña para facilitar las pruebas: **`admin123`**

### Usuarios Disponibles:

| Usuario | Nombre | Rol | Email | Contraseña |
|---------|--------|-----|-------|------------|
| `admin` | Juan Pérez | PRESIDENTE | admin@empujecomunitario.org | `admin123` |
| `vocal1` | María González | VOCAL | maria@empujecomunitario.org | `admin123` |
| `coord1` | Carlos López | COORDINADOR | carlos@empujecomunitario.org | `admin123` |
| `vol1` | Ana Martínez | VOLUNTARIO | ana@empujecomunitario.org | `admin123` |
| `vol2` | Pedro Rodríguez | VOLUNTARIO | pedro@empujecomunitario.org | `admin123` |

## Permisos por Rol:

### PRESIDENTE (admin)
- ✅ Gestión completa de usuarios (CRUD)
- ✅ Gestión completa de inventario (CRUD)
- ✅ Gestión completa de eventos (CRUD)

### VOCAL (vocal1)
- ❌ Sin acceso a usuarios
- ✅ Gestión completa de inventario (CRUD)
- ❌ Sin acceso a eventos

### COORDINADOR (coord1)
- ❌ Sin acceso a usuarios
- ❌ Sin acceso a inventario
- ✅ Gestión completa de eventos (CRUD)

### VOLUNTARIO (vol1, vol2)
- ❌ Sin acceso a usuarios
- ❌ Sin acceso a inventario
- ✅ Solo lectura de eventos y participación

## URLs de Acceso:

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:3001
- **Health Check**: http://localhost:3001/health

## Ejemplo de Login:

```json
{
  "usernameOrEmail": "admin",
  "password": "admin123"
}
```

O también puedes usar el email:

```json
{
  "usernameOrEmail": "admin@empujecomunitario.org",
  "password": "admin123"
}
```