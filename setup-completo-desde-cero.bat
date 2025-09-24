@echo off
echo 🚀 SETUP COMPLETO DEL SISTEMA ONG DESDE CERO
echo ================================================

echo.
echo 📋 PASO 1: Verificacion de prerrequisitos
echo 🔍 Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no esta instalado
    echo    Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo 🔍 Verificando Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose no esta disponible
    pause
    exit /b 1
)

echo 🔍 Verificando que Docker este corriendo...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no esta corriendo. Inicia Docker Desktop
    pause
    exit /b 1
)

echo ✅ Todos los prerrequisitos OK

echo.
echo 🧹 PASO 2: Limpieza de contenedores anteriores
echo 🔄 Deteniendo contenedores existentes...
docker-compose down --remove-orphans >nul 2>&1

echo 🗑️ Eliminando imagenes anteriores...
for /f "tokens=*" %%i in ('docker images --format "{{.Repository}}:{{.Tag}}" ^| findstr "ong-management\|user-service\|inventory-service\|events-service\|api-gateway\|frontend"') do (
    docker rmi %%i --force >nul 2>&1
)

echo 🧽 Limpiando volumenes...
docker volume prune -f >nul 2>&1

echo ✅ Limpieza completada

echo.
echo 🏗️ PASO 3: Construccion de imagenes desde cero
echo 📦 Construyendo todas las imagenes (esto puede tomar varios minutos)...
docker-compose build --no-cache

if %errorlevel% neq 0 (
    echo ❌ Error en la construccion de imagenes
    pause
    exit /b 1
)

echo ✅ Imagenes construidas exitosamente

echo.
echo 🚀 PASO 4: Iniciando todos los servicios
echo 🔄 Levantando servicios...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Error al iniciar servicios
    echo    Ejecuta 'docker-compose logs' para ver errores
    pause
    exit /b 1
)

echo ✅ Servicios iniciados

echo.
echo ⏳ PASO 5: Esperando que los servicios esten listos
echo 🗄️ Esperando base de datos...
timeout /t 15 /nobreak >nul

echo 🔧 Esperando microservicios...
timeout /t 20 /nobreak >nul

echo 🌐 Verificando API Gateway...
:check_api
curl -s http://localhost:3001/health >nul 2>&1
if %errorlevel% neq 0 (
    echo    Esperando API Gateway...
    timeout /t 3 /nobreak >nul
    goto check_api
)
echo ✅ API Gateway listo

echo 🖥️ Verificando Frontend...
:check_frontend
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% neq 0 (
    echo    Esperando Frontend...
    timeout /t 3 /nobreak >nul
    goto check_frontend
)
echo ✅ Frontend listo

echo.
echo 🧪 PASO 6: Prueba rapida del sistema
echo 🔐 Probando autenticacion...
curl -s -X POST http://localhost:3001/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"usernameOrEmail\":\"admin\",\"password\":\"admin123\"}" ^
  -o login_test.json

if %errorlevel% equ 0 (
    echo ✅ Autenticacion OK
) else (
    echo ❌ Error en autenticacion
)

echo.
echo 📊 PASO 7: Estado final del sistema
docker-compose ps

echo.
echo 🎯 SISTEMA LISTO PARA USAR!
echo ================================

echo.
echo 🌐 URLs de acceso:
echo    Frontend:     http://localhost:3000
echo    API Gateway:  http://localhost:3001
echo    Health Check: http://localhost:3001/health

echo.
echo 🔐 Credenciales de prueba:
echo    Admin:       admin / admin123
echo    Coordinador: coord1 / admin123
echo    Voluntario:  vol1 / admin123

echo.
echo 📝 Proximos pasos:
echo    1. Abre http://localhost:3000 en tu navegador
echo    2. Haz login con admin/admin123
echo    3. Explora las funcionalidades del sistema

echo.
echo 🛠️ Comandos utiles:
echo    Ver logs:     docker-compose logs -f
echo    Reiniciar:    docker-compose restart
echo    Detener:      docker-compose down
echo    Estado:       docker-compose ps

echo.
echo ✨ Sistema completamente operativo!

if exist login_test.json del login_test.json
pause