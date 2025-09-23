@echo off
echo 🐳 Iniciando PostgreSQL con Docker y servicios localmente...
echo.

echo 🔍 Verificando Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está disponible
    pause
    exit /b 1
)

echo ✅ Docker disponible
echo.

echo 🗄️  Iniciando PostgreSQL...
docker-compose up -d postgres
if errorlevel 1 (
    echo ❌ Error iniciando PostgreSQL
    pause
    exit /b 1
)

echo ⏳ Esperando que PostgreSQL se inicialice...
timeout /t 15 /nobreak >nul

echo 📋 Verificando PostgreSQL...
docker exec ong_postgres pg_isready -U ong_user -d ong_management
if errorlevel 1 (
    echo ❌ PostgreSQL no está listo
    pause
    exit /b 1
)

echo ✅ PostgreSQL está listo
echo.

echo 🚀 Iniciando microservicios localmente...
echo.

echo 🔄 Iniciando User Service...
start "User Service" cmd /k "cd user-service && set PYTHONIOENCODING=utf-8 && set PYTHONLEGACYWINDOWSSTDIO=utf-8 && python src/server.py"

timeout /t 3 /nobreak >nul

echo 🔄 Iniciando Inventory Service...
start "Inventory Service" cmd /k "cd inventory-service && set PYTHONIOENCODING=utf-8 && set PYTHONLEGACYWINDOWSSTDIO=utf-8 && python src/server.py"

timeout /t 3 /nobreak >nul

echo 🔄 Iniciando Events Service...
start "Events Service" cmd /k "cd events-service && set PYTHONIOENCODING=utf-8 && set PYTHONLEGACYWINDOWSSTDIO=utf-8 && python src/server.py"

echo.
echo 🎉 Servicios iniciados!
echo.
echo 📋 Estado:
echo   🗄️  PostgreSQL:     Docker (localhost:5432)
echo   👥 User Service:    localhost:50051
echo   📦 Inventory:       localhost:50052
echo   📅 Events:          localhost:50053
echo.
echo 🔧 Próximos pasos:
echo   1. Espera que todos los servicios se inicialicen
echo   2. Inicia el API Gateway: cd api-gateway && npm start
echo   3. Inicia el Frontend: cd frontend && npm start
echo.
pause