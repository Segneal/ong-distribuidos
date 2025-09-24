@echo off
echo 🚀 INICIANDO SISTEMA ONG
echo ========================

echo.
echo 📋 Verificando Docker...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no esta corriendo. Inicia Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker OK

echo.
echo 🏗️ Construyendo imagenes...
docker-compose build
if %errorlevel% neq 0 (
    echo ❌ Error en build
    pause
    exit /b 1
)

echo.
echo 🚀 Iniciando servicios...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Error al iniciar servicios
    pause
    exit /b 1
)

echo.
echo ⏳ Esperando servicios...
echo 🗄️ Esperando PostgreSQL...
timeout /t 10 /nobreak >nul

echo 🔧 Esperando microservicios...
timeout /t 15 /nobreak >nul

echo 🌐 Verificando API Gateway...
:check_api
curl -s http://localhost:3001/health >nul 2>&1
if %errorlevel% neq 0 (
    echo    Esperando API Gateway...
    timeout /t 2 /nobreak >nul
    goto check_api
)
echo ✅ API Gateway listo

echo 🖥️ Verificando Frontend...
:check_frontend
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% neq 0 (
    echo    Esperando Frontend...
    timeout /t 2 /nobreak >nul
    goto check_frontend
)
echo ✅ Frontend listo

echo.
echo 🧪 Prueba rapida...
curl -s -X POST http://localhost:3001/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"usernameOrEmail\":\"admin\",\"password\":\"admin123\"}" >nul 2>&1

if %errorlevel% equ 0 (
    echo ✅ Sistema funcionando correctamente!
) else (
    echo ⚠️ Sistema iniciado, verificar manualmente
)

echo.
echo 📊 Estado de servicios:
docker-compose ps

echo.
echo 🎯 SISTEMA INICIADO!
echo ===================

echo.
echo 🌐 URLs:
echo    Frontend:    http://localhost:3000
echo    API Gateway: http://localhost:3001

echo.
echo 🔐 Login:
echo    Usuario: admin
echo    Contraseña: admin123

echo.
echo 📝 Si algo no funciona:
echo    docker-compose logs -f
echo    docker-compose restart

pause