@echo off
echo Iniciando API Gateway...

REM Variables de entorno
set DB_HOST=localhost
set DB_NAME=ong_management
set DB_USER=ong_user
set DB_PASSWORD=ong_pass
set DB_PORT=5432
set PORT=3000
set JWT_SECRET=your-secret-key-change-in-production
set JWT_EXPIRES_IN=15m
set REFRESH_TOKEN_EXPIRES_IN=7d
set USER_SERVICE_URL=localhost:50051
set INVENTORY_SERVICE_URL=localhost:50052
set EVENTS_SERVICE_URL=localhost:50053
set EMAIL_SERVICE_URL=http://localhost:3002

echo Variables configuradas:
echo   DB_HOST: %DB_HOST%
echo   PORT: %PORT% (API Gateway)
echo   JWT_SECRET: [CONFIGURADO]
echo.

cd api-gateway
echo Iniciando API Gateway en puerto 3000...
npm start

pause