# Fixes Aplicados

## ❌ Problemas Identificados:
1. Error gRPC "Error interno del servidor" en login
2. Falta separación de usuarios por organización

## ✅ Fixes Aplicados:

### 1. Arreglado verify_password para SHA256 y bcrypt
**Archivo:** `user-service/src/crypto.py`
- Ahora maneja tanto hash bcrypt (usuarios originales) como SHA256 (usuarios nuevos)

### 2. Separación de usuarios por organización
**Archivo:** `user-service/src/user_repository_mysql.py`
- Agregado parámetro `organization` a `list_users()`

**Archivo:** `api-gateway/src/routes/users.js`
- Filtro de usuarios por organización del usuario logueado
- Forzar organización en creación de usuarios

## 🧪 Para Probar:
1. Iniciar user-service: `cd user-service && python src/server.py`
2. Iniciar API Gateway: `cd api-gateway && npm start`
3. Probar login con: `esperanza_admin` / `password123`

## 📋 Credenciales:
- esperanza_admin / password123 (fundacion-esperanza)
- solidaria_admin / password123 (ong-solidaria)
- centro_admin / password123 (centro-comunitario)