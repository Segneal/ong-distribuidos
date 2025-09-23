# 🚀 Instrucciones para Iniciar el Sistema ONG

## Prerrequisitos

1. **Docker Desktop** instalado y ejecutándose
2. **Docker Compose** (incluido con Docker Desktop)
3. **Git** para clonar el repositorio

## 🐳 Inicio con Docker (Recomendado)

### Opción A: Script Automático
```bash
# PowerShell (Recomendado)
.\start-docker.ps1

# O CMD/Batch
.\start-docker.bat
```

### Opción B: Manual con Docker Compose
```bash
# Construir e iniciar todos los servicios
docker-compose up --build -d

# Ver el estado de los servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f
```

## 🛠️ Desarrollo Local (Sin Docker)

Si prefieres ejecutar los servicios localmente para desarrollo:

### Prerrequisitos Adicionales
1. **Python 3.8+** instalado
2. **Node.js 16+** instalado  
3. **PostgreSQL** ejecutándose localmente

### 1. Preparar la Base de Datos
```bash
# Crear la base de datos y usuario
psql -U postgres -c "CREATE DATABASE ong_management;"
psql -U postgres -c "CREATE USER ong_user WITH PASSWORD 'ong_pass';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ong_management TO ong_user;"

# Ejecutar scripts de inicialización
psql -U ong_user -d ong_management -f database/schema.sql
psql -U ong_user -d ong_management -f database/init.sql
psql -U ong_user -d ong_management -f database/sample_data.sql
```

### 2. Iniciar Microservicios
```bash
# Terminal 1 - User Service
cd user-service
pip install -r requirements.txt
python src/server.py

# Terminal 2 - Inventory Service  
cd inventory-service
pip install -r requirements.txt
python src/server.py

# Terminal 3 - Events Service
cd events-service
pip install -r requirements.txt
python src/server.py
```

### 3. Iniciar API Gateway
```bash
cd api-gateway
npm install
npm start
```

### 4. Iniciar Frontend
```bash
cd frontend
npm install
npm start
```

## 🔍 Verificación

### Verificar Microservicios
Los microservicios deberían mostrar mensajes como:
- `Servidor gRPC de usuarios iniciado en puerto 50051`
- `Starting Inventory Service gRPC server on [::]:50052`
- `Events Service starting on port 50053`

### Verificar API Gateway
- Debería iniciar en `http://localhost:3000`
- Endpoint de salud: `http://localhost:3000/health`

### Verificar Frontend
- Debería abrir automáticamente en `http://localhost:3001`
- Página de login debería estar disponible

## 🔐 Credenciales de Prueba

Consulta el archivo `CREDENCIALES_PRUEBA.md` para las credenciales de usuarios de prueba.

## 🐛 Solución de Problemas

### Error: "ECONNREFUSED ::1:50051"
- **Causa:** Los microservicios gRPC no están ejecutándose
- **Solución:** Asegúrate de iniciar los microservicios antes que el API Gateway

### Error: "Cannot connect to database"
- **Causa:** PostgreSQL no está ejecutándose o la configuración es incorrecta
- **Solución:** Verifica que PostgreSQL esté ejecutándose y las credenciales en los archivos `.env`

### Error: "Port already in use"
- **Causa:** Los puertos ya están siendo utilizados
- **Solución:** Cierra los procesos existentes o cambia los puertos en los archivos `.env`

### Puertos Utilizados
- **User Service:** 50051 (gRPC)
- **Inventory Service:** 50052 (gRPC)
- **Events Service:** 50053 (gRPC)
- **API Gateway:** 3000 (HTTP)
- **Frontend:** 3001 (HTTP)
- **PostgreSQL:** 5432 (Database)

## 📝 Notas Importantes

1. **Orden de inicio:** Siempre inicia los microservicios gRPC antes que el API Gateway
2. **Base de datos:** Asegúrate de que la base de datos esté configurada y ejecutándose
3. **Dependencias:** Ejecuta `npm install` y `pip install -r requirements.txt` en cada servicio
4. **Variables de entorno:** Los archivos `.env` ya están configurados con valores por defecto

## 🔄 Para Detener el Sistema

1. **Microservicios:** Presiona `Ctrl+C` en cada terminal o cierra las ventanas
2. **API Gateway:** Presiona `Ctrl+C` en la terminal
3. **Frontend:** Presiona `Ctrl+C` en la terminal

## 📞 Ayuda

Si encuentras problemas, verifica:
1. Que todos los servicios estén ejecutándose
2. Los logs de cada servicio para errores específicos
3. Que las credenciales de base de datos sean correctas
4. Que los puertos no estén siendo utilizados por otros procesos