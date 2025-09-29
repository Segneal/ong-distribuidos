@echo off
echo 🐳 Iniciando Sistema ONG con Docker Compose...
echo.

echo 🔍 Verificando Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está instalado o no está ejecutándose
    echo 💡 Por favor instala Docker Desktop y asegúrate de que esté ejecutándose
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose no está disponible
    echo 💡 Por favor instala Docker Compose
    pause
    exit /b 1
)

echo ✅ Docker está disponible
echo.

echo 🛑 Deteniendo contenedores existentes...
docker-compose down

echo.
echo 🏗️  Construyendo e iniciando servicios...
echo ⏳ Esto puede tomar varios minutos la primera vez...
docker-compose up --build -d

echo.
echo 📋 Verificando estado de los servicios...
timeout /t 10 /nobreak >nul
docker-compose ps

echo.
echo 🎉 Sistema iniciado!
echo.
echo 📋 Servicios disponibles:
echo   🗄️  PostgreSQL:     localhost:5432
echo   📨 Kafka:          localhost:9092
echo   👥 User Service:    localhost:50051 (gRPC)
echo   📦 Inventory:       localhost:50052 (gRPC)
echo   📅 Events:          localhost:50053 (gRPC)
echo   💬 Messaging:       localhost:50054 (HTTP)
echo   📧 Email Service:   localhost:3002
echo   📬 MailHog UI:      http://localhost:8025
echo   🌐 API Gateway:     http://localhost:3000
echo   💻 Frontend:        http://localhost:3001
echo.
echo 🔧 Comandos útiles:
echo   Ver logs:           docker-compose logs -f
echo   Ver logs específicos: docker-compose logs -f [servicio]
echo   Detener sistema:    docker-compose down
echo   Reiniciar:          docker-compose restart
echo.
echo 🌐 Abre tu navegador en: http://localhost:3001
echo.
pause