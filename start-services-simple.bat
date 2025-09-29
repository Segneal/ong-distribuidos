@echo off
echo 🚀 Iniciando microservicios de ONG Empuje Comunitario...
echo.

echo 🔄 Iniciando User Service en puerto 50051...
start "User Service - Puerto 50051" cmd /k "cd user-service && set PYTHONIOENCODING=utf-8 && echo Iniciando User Service... && python src/server.py"

echo ⏳ Esperando 3 segundos...
timeout /t 3 /nobreak >nul

echo 🔄 Iniciando Inventory Service en puerto 50052...
start "Inventory Service - Puerto 50052" cmd /k "cd inventory-service && set PYTHONIOENCODING=utf-8 && echo Iniciando Inventory Service... && python src/server.py"

echo ⏳ Esperando 3 segundos...
timeout /t 3 /nobreak >nul

echo 🔄 Iniciando Events Service en puerto 50053...
start "Events Service - Puerto 50053" cmd /k "cd events-service && set PYTHONIOENCODING=utf-8 && echo Iniciando Events Service... && python src/server.py"

echo ⏳ Esperando 3 segundos...
timeout /t 3 /nobreak >nul

echo 🔄 Iniciando Messaging Service en puerto 50054...
start "Messaging Service - Puerto 50054" cmd /k "cd messaging-service && set PYTHONIOENCODING=utf-8 && echo Iniciando Messaging Service... && python src/main.py"

echo.
echo 🎉 Todos los microservicios han sido iniciados en ventanas separadas!
echo.
echo 📋 Servicios ejecutándose:
echo   • User Service:      localhost:50051
echo   • Inventory Service: localhost:50052  
echo   • Events Service:    localhost:50053
echo   • Messaging Service: localhost:50054
echo.
echo 🔧 Ahora puedes iniciar el API Gateway:
echo   cd api-gateway
echo   npm start
echo.
echo 🌐 Y luego el Frontend:
echo   cd frontend
echo   npm start
echo.
echo ⚠️  Para detener los servicios, cierra las ventanas correspondientes
echo.
pause