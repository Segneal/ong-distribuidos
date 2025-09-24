# 🚀 Setup Rápido - Sistema ONG desde Cero

## ⚡ Inicio Ultra-Rápido (1 comando)

```bash
# PowerShell (Recomendado - más completo)
.\setup-completo-desde-cero.ps1

# O CMD (Básico)
.\setup-completo-desde-cero.bat
```

**¡Eso es todo!** En 5-10 minutos tendrás el sistema completo funcionando.

## 📋 Lo que hace el script automáticamente:

1. ✅ **Verifica prerrequisitos** (Docker, Docker Compose)
2. 🧹 **Limpia contenedores/imágenes anteriores**
3. 🏗️ **Construye todas las imágenes desde cero**
4. 🚀 **Inicia todos los servicios**
5. ⏳ **Espera que todo esté listo**
6. 🧪 **Prueba el sistema automáticamente**
7. 📊 **Muestra estado final y URLs**

## 🎯 Resultado Final

Después de ejecutar el script tendrás:

- **Frontend:** http://localhost:3000
- **API Gateway:** http://localhost:3001
- **Base de datos:** PostgreSQL con datos de prueba
- **Microservicios:** User, Inventory, Events (gRPC)

## 🔐 Credenciales Listas

| Usuario | Contraseña | Rol | Permisos |
|---------|------------|-----|----------|
| `admin` | `admin123` | PRESIDENTE | Todo |
| `coord1` | `admin123` | COORDINADOR | Solo eventos |
| `vol1` | `admin123` | VOLUNTARIO | Solo lectura |

## 🧪 Verificación Rápida

1. **Abrir:** http://localhost:3000
2. **Login:** `admin` / `admin123`
3. **Probar:** Crear usuario, evento, donación

## 🛠️ Si algo falla:

```bash
# Ver logs detallados
docker-compose logs -f

# Reiniciar servicios
docker-compose restart

# Empezar de nuevo
docker-compose down
.\setup-completo-desde-cero.ps1
```

## 📦 Prerrequisitos Mínimos

- **Docker Desktop** instalado y corriendo
- **8GB RAM** disponible
- **5GB espacio** en disco
- **Puertos libres:** 3000, 3001, 5432, 50051-50053

## ⏱️ Tiempos Estimados

- **Primera vez:** 8-12 minutos (descarga + build)
- **Siguientes veces:** 3-5 minutos (solo build)
- **Con imágenes cached:** 1-2 minutos

## 🎉 ¡Listo para demostrar!

Una vez completado el setup, el sistema está 100% funcional con:
- ✅ Autenticación por roles
- ✅ Gestión de usuarios
- ✅ Inventario de donaciones
- ✅ Eventos y participantes
- ✅ Permisos granulares
- ✅ Datos de prueba precargados