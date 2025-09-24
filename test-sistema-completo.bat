@echo off
echo 🚀 Iniciando prueba rapida del sistema ONG...

REM Configuracion
set API_BASE=http://localhost:3001

echo.
echo 📋 FASE 1: Verificacion de servicios basicos
echo 🔍 Probando Health Check...
curl -s %API_BASE%/health
if %errorlevel% equ 0 (
    echo ✅ Health Check OK
) else (
    echo ❌ Health Check FAILED
)

echo.
echo 🔐 FASE 2: Autenticacion
echo 🔍 Probando login como admin...
curl -s -X POST %API_BASE%/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"usernameOrEmail\":\"admin\",\"password\":\"admin123\"}" ^
  -o login_response.json

if %errorlevel% equ 0 (
    echo ✅ Login OK
    REM Extraer token (simplificado)
    for /f "tokens=2 delims=:" %%a in ('findstr "token" login_response.json') do set TOKEN=%%a
    set TOKEN=%TOKEN:"=%
    set TOKEN=%TOKEN:,=%
    set TOKEN=%TOKEN: =%
) else (
    echo ❌ Login FAILED
    goto :end
)

echo.
echo 👥 FASE 3: Gestion de Usuarios
echo 🔍 Probando listar usuarios...
curl -s %API_BASE%/users -H "Authorization: Bearer %TOKEN%"
if %errorlevel% equ 0 (
    echo ✅ Listar usuarios OK
) else (
    echo ❌ Listar usuarios FAILED
)

echo.
echo 📦 FASE 4: Gestion de Inventario
echo 🔍 Probando listar inventario...
curl -s %API_BASE%/inventory -H "Authorization: Bearer %TOKEN%"
if %errorlevel% equ 0 (
    echo ✅ Listar inventario OK
) else (
    echo ❌ Listar inventario FAILED
)

echo.
echo 🎉 FASE 5: Gestion de Eventos
echo 🔍 Probando listar eventos...
curl -s %API_BASE%/events -H "Authorization: Bearer %TOKEN%"
if %errorlevel% equ 0 (
    echo ✅ Listar eventos OK
) else (
    echo ❌ Listar eventos FAILED
)

echo.
echo 🔍 Probando crear evento...
curl -s -X POST %API_BASE%/events ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Evento de Prueba\",\"description\":\"Evento creado para pruebas\",\"event_date\":\"2024-12-25T10:00:00Z\",\"location\":\"Centro Comunitario\",\"max_participants\":50,\"event_type\":\"DISTRIBUCION\"}"

if %errorlevel% equ 0 (
    echo ✅ Crear evento OK
) else (
    echo ❌ Crear evento FAILED
)

echo.
echo 🎯 RESUMEN DE PRUEBAS COMPLETADO
echo ✅ Sistema probado con funcionalidades basicas
echo 🌐 Frontend disponible en: http://localhost:3000
echo 🔗 API Gateway disponible en: http://localhost:3001

echo.
echo 📝 CREDENCIALES DE PRUEBA:
echo Admin: admin / admin123
echo Coordinador: coord1 / admin123
echo Voluntario: vol1 / admin123

:end
if exist login_response.json del login_response.json
pause