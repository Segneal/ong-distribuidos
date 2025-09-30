@echo off
echo Verificando configuracion de puertos...
echo.

echo Verificando puerto 3000 (API Gateway):
curl -s http://localhost:3000/health >nul 2>&1
if %errorlevel%==0 (
    echo   ✓ API Gateway corriendo en puerto 3000
) else (
    echo   ✗ API Gateway NO esta corriendo en puerto 3000
)

echo.
echo Verificando puerto 3001 (Frontend):
curl -s http://localhost:3001 >nul 2>&1
if %errorlevel%==0 (
    echo   ✓ Frontend corriendo en puerto 3001
) else (
    echo   ✗ Frontend NO esta corriendo en puerto 3001
)

echo.
echo Verificando puerto 5432 (Base de datos):
netstat -an | find "5432" >nul
if %errorlevel%==0 (
    echo   ✓ Base de datos corriendo en puerto 5432
) else (
    echo   ✗ Base de datos NO esta corriendo en puerto 5432
)

echo.
echo Configuracion esperada:
echo   Frontend: http://localhost:3001
echo   API Gateway: http://localhost:3000
echo   Base de datos: localhost:5432
echo.
pause