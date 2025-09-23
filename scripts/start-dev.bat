@echo off
echo 🚀 Iniciando Sistema de Gestión ONG - Empuje Comunitario
echo ==================================================

REM Verificar que Docker esté ejecutándose
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Docker no está ejecutándose
    echo Por favor, inicia Docker Desktop y vuelve a intentar
    pause
    exit /b 1
)

echo ✅ Docker está ejecutándose
echo 📦 Construyendo e iniciando servicios...

REM Construir e iniciar todos los servicios
docker-compose up -d --build

echo.
echo 🎉 Sistema iniciado exitosamente!
echo.
echo 📋 Servicios disponibles:
echo    • Frontend:     http://localhost:3001
echo    • API Gateway:  http://localhost:3000
echo    • PostgreSQL:   localhost:5432
echo    • Kafka:        localhost:9092
echo.
echo 📊 Para ver los logs:
echo    docker-compose logs -f
echo.
echo 🛑 Para detener el sistema:
echo    docker-compose down
echo.
pause