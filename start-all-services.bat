@echo off
echo ========================================
echo   INICIANDO SISTEMA COMPLETO LOCAL
echo ========================================
echo.

echo 1. Verificando base de datos...
netstat -an | find "5432" >nul
if errorlevel 1 (
    echo    ERROR: La base de datos no esta disponible en puerto 5432
    echo    Ejecuta: docker-compose -f docker-compose-minimal.yml up -d
    pause
    exit /b 1
) else (
    echo    Base de datos OK
)

echo.
echo 2. Iniciando servicios en ventanas separadas...

echo    Iniciando User Service...
start "User Service" cmd /k "start-user-service.bat"
timeout /t 3 /nobreak >nul

echo    Iniciando Inventory Service...
start "Inventory Service" cmd /k "start-inventory-service.bat"
timeout /t 3 /nobreak >nul

echo    Iniciando Events Service...
start "Events Service" cmd /k "start-events-service.bat"
timeout /t 3 /nobreak >nul

echo    Iniciando Messaging Service...
start "Messaging Service" cmd /k "start-messaging-service.bat"
timeout /t 3 /nobreak >nul

echo    Iniciando API Gateway...
start "API Gateway" cmd /k "start-api-gateway.bat"
timeout /t 5 /nobreak >nul

echo    Iniciando Frontend...
start "Frontend" cmd /k "start-frontend.bat"

echo.
echo ========================================
echo   TODOS LOS SERVICIOS INICIADOS
echo ========================================
echo.
echo Servicios disponibles:
echo    Base de datos: localhost:5432
echo    Kafka: localhost:9092
echo    MailHog UI: http://localhost:8025
echo    User Service: localhost:50051 (gRPC)
echo    Inventory Service: localhost:50052 (gRPC)
echo    Events Service: localhost:50053 (gRPC)
echo    Messaging Service: http://localhost:8000
echo    API Gateway: http://localhost:3000
echo    Frontend: http://localhost:3001
echo.
echo Configuracion de puertos:
echo    Frontend (3001) ---> API Gateway (3000) ---> Microservicios (50051-50053)
echo.
echo Para detener todos los servicios:
echo    stop-all-services.bat
echo.
echo Presiona cualquier tecla para continuar...
pause >nul