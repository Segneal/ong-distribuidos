@echo off
echo 🔍 Verificando estado del sistema Docker...
echo.

echo 📋 Estado de los contenedores:
docker-compose ps
echo.

echo 🚨 Verificando errores recientes:
echo.
echo === USER SERVICE ===
docker-compose logs --tail=10 user-service | findstr /i "error"
echo.

echo === API GATEWAY ===
docker-compose logs --tail=10 api-gateway | findstr /i "error"
echo.

echo === FRONTEND ===
docker-compose logs --tail=10 frontend | findstr /i "error"
echo.

echo === POSTGRES ===
docker-compose logs --tail=5 postgres | findstr /i "error"
echo.

echo 📊 Últimos logs de cada servicio:
echo.
echo === USER SERVICE (últimas 5 líneas) ===
docker-compose logs --tail=5 user-service
echo.

echo === API GATEWAY (últimas 5 líneas) ===
docker-compose logs --tail=5 api-gateway
echo.

echo 🌐 Probando conectividad:
echo.
curl -s http://localhost:3000/health || echo "❌ API Gateway no responde"
curl -s http://localhost:3001 || echo "❌ Frontend no responde"
echo.

pause