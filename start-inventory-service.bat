@echo off
echo Iniciando Inventory Service...

REM Variables de entorno
set DB_HOST=localhost
set DB_NAME=ong_management
set DB_USER=ong_user
set DB_PASSWORD=ong_pass
set DB_PORT=5432
set GRPC_PORT=50052
set ORGANIZATION_ID=empuje-comunitario

echo Variables configuradas:
echo   DB_HOST: %DB_HOST%
echo   GRPC_PORT: %GRPC_PORT%
echo.

cd inventory-service
echo Iniciando Inventory Service en puerto 50052...
python src/server.py

pause