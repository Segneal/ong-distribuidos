@echo off
echo 🚀 Iniciando microservicios de ONG Empuje Comunitario...
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Por favor instala Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Crear ventanas separadas para cada servicio
echo 🔄 Iniciando User Service en puerto 50051...
start "User Service" cmd /k "cd user-service && python src/server.py"

timeout /t 3 /nobreak >nul

echo 🔄 Iniciando Inventory Service en puerto 50052...
start "Inventory Service" cmd /k "cd inventory-service && python src/server.py"

timeout /t 3 /nobreak >nul

echo 🔄 Iniciando Events Service en puerto 50053...
start "Events Service" cmd /k "cd events-service && python src/server.py"

timeout /t 3 /nobreak >nul

echo 🔄 Iniciando Messaging Service en puerto 50054...
start "Messaging Service" cmd /k "cd messaging-service && python src/main.py"

echo.
echo 🎉 Todos los microservicios han sido iniciados en ventanas separadas!
echo.
echo 📋 Servicios ejecutándose:
echo   • User Service:      localhost:50051
echo   • Inventory Service: localhost:50052
echo   • Events Service:    localhost:50053
echo   • Messaging Service: localhost:50054
echo.
echo 🔧 Para iniciar el API Gateway:
echo   cd api-gateway
echo   npm start
echo.
echo 🌐 Para iniciar el Frontend:
echo   cd frontend
echo   npm start
echo.
echo ⚠️  Para detener los servicios, cierra las ventanas correspondientes
echo.
pause