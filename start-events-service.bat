@echo off
echo Iniciando Events Service...

REM Variables de entorno
set DB_HOST=localhost
set DB_NAME=ong_management
set DB_USER=ong_user
set DB_PASSWORD=ong_pass
set DB_PORT=5432
set EVENTS_SERVICE_PORT=50053
set ORGANIZATION_ID=empuje-comunitario

echo Variables configuradas:
echo   DB_HOST: %DB_HOST%
echo   EVENTS_SERVICE_PORT: %EVENTS_SERVICE_PORT%
echo.

cd events-service
echo Iniciando Events Service en puerto 50053...
python src/server.py

pause