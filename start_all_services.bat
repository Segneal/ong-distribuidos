@echo off
echo 🚀 Iniciando todos los servicios del sistema ONG...
echo.

echo 📊 Iniciando Reports Service en puerto 8002...
start "Reports Service" cmd /k "cd reports-service && python start_server.py"
timeout /t 3

echo 🌐 Iniciando API Gateway en puerto 3001...
start "API Gateway" cmd /k "cd api-gateway && npm start"
timeout /t 3

echo ✅ Servicios iniciados:
echo   - Reports Service: http://localhost:8002
echo   - API Gateway: http://localhost:3001
echo.
echo 🔍 Health checks:
echo   - Reports Service: http://localhost:8002/health
echo   - API Gateway: http://localhost:3001/health
echo.
echo 🧪 Test endpoints:
echo   - Reports Service: http://localhost:8002/api/reports/test
echo.
echo Presiona cualquier tecla para continuar...
pause