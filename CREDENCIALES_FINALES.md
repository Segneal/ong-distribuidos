# Credenciales Finales - Sistema Multi-Organización

## 🔑 Password Universal: `admin`

**Todos los usuarios usan la misma password: `admin`**

## 🏢 Usuarios por Organización

### **Empuje Comunitario** (empuje-comunitario)
- `admin` / `admin` - PRESIDENTE - Juan Pérez
- `coord1` / `admin` - COORDINADOR - Carlos López  
- `vocal1` / `admin` - VOCAL - María González
- `vol1` / `admin` - VOLUNTARIO - Ana Martínez
- `vol2` / `admin` - VOLUNTARIO - Pedro Rodríguez

### **Fundación Esperanza** (fundacion-esperanza)
- `esperanza_admin` / `admin` - PRESIDENTE - María González
- `esperanza_coord` / `admin` - COORDINADOR - Carlos Ruiz

### **ONG Solidaria** (ong-solidaria)
- `solidaria_admin` / `admin` - PRESIDENTE - Ana López
- `solidaria_vol` / `admin` - VOLUNTARIO - Pedro Martín

### **Centro Comunitario Unidos** (centro-comunitario)
- `centro_admin` / `admin` - PRESIDENTE - Laura Fernández
- `centro_vocal` / `admin` - VOCAL - Diego Silva

## 🧪 Para Probar Multi-Organización

1. **Login** con `esperanza_admin` / `admin`
2. **Verificar** header muestra "Fundación Esperanza"
3. **Ver** solo usuarios de Fundación Esperanza en lista
4. **Logout** y login con `solidaria_admin` / `admin`
5. **Verificar** header muestra "ONG Solidaria"
6. **Ver** solo usuarios de ONG Solidaria en lista

## 🎯 Funcionalidades por Rol

- **PRESIDENTE**: Gestión completa de usuarios de su organización
- **COORDINADOR**: Gestión de eventos y voluntarios
- **VOCAL**: Gestión de inventario y donaciones
- **VOLUNTARIO**: Participación en eventos

## ✅ Sistema Listo

- ✅ Multi-organización implementado
- ✅ Header dinámico por organización
- ✅ Usuarios filtrados por organización
- ✅ Password universal para pruebas
- ✅ Kafka configurado para red de ONGs