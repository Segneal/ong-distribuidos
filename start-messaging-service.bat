@echo off
echo Iniciando Messaging Service...

REM Variables de entorno
set DB_HOST=localhost
set DB_NAME=ong_management
set DB_USER=ong_user
set DB_PASSWORD=ong_pass
set DB_PORT=5432
set HTTP_PORT=8000
set SERVICE_PORT=50054
set KAFKA_BROKERS=localhost:9092
set KAFKA_GROUP_ID=empuje-comunitario-group
set ORGANIZATION_ID=empuje-comunitario
set LOG_LEVEL=INFO

echo Variables configuradas:
echo   DB_HOST: %DB_HOST%
echo   HTTP_PORT: %HTTP_PORT% (Messaging Service HTTP)
echo   SERVICE_PORT: %SERVICE_PORT% (Messaging Service gRPC)
echo   KAFKA_BROKERS: %KAFKA_BROKERS%
echo.

cd messaging-service
echo Iniciando Messaging Service en puerto 8000...
python src/server.py

pause