@echo off
echo 🐳 Ejecutando User Service en Docker...
echo.

echo 🛑 Deteniendo contenedores existentes...
docker stop ong_user_service 2>nul
docker rm ong_user_service 2>nul

echo 🏗️  Construyendo imagen...
docker build -t ong-user-service ./user-service
if errorlevel 1 (
    echo ❌ Error construyendo imagen
    pause
    exit /b 1
)

echo 🚀 Iniciando User Service...
docker run -d ^
  --name ong_user_service ^
  --network ong-distribuidos_ong_network ^
  -p 50051:50051 ^
  -e DB_HOST=ong_postgres ^
  -e DB_NAME=ong_management ^
  -e DB_USER=ong_user ^
  -e DB_PASSWORD=ong_pass ^
  -e DB_PORT=5432 ^
  -e GRPC_PORT=50051 ^
  ong-user-service

if errorlevel 1 (
    echo ❌ Error iniciando contenedor
    pause
    exit /b 1
)

echo ✅ User Service iniciado en Docker
echo 📋 Ver logs: docker logs -f ong_user_service
echo 🛑 Detener: docker stop ong_user_service
echo.
pause