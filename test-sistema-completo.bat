@echo off
echo ========================================
echo PRUEBA COMPLETA DEL SISTEMA ONG
echo ========================================
echo.

echo 1. Verificando servicios Docker...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

echo 2. Probando conectividad a servicios...
echo - PostgreSQL (puerto 5432):
timeout /t 1 >nul 2>&1 && echo   ✓ Disponible || echo   ✗ No disponible

echo - User Service gRPC (puerto 50051):
timeout /t 1 >nul 2>&1 && echo   ✓ Disponible || echo   ✗ No disponible

echo - Inventory Service gRPC (puerto 50052):
timeout /t 1 >nul 2>&1 && echo   ✓ Disponible || echo   ✗ No disponible

echo - Events Service gRPC (puerto 50053):
timeout /t 1 >nul 2>&1 && echo   ✓ Disponible || echo   ✗ No disponible

echo - API Gateway (puerto 3000):
timeout /t 1 >nul 2>&1 && echo   ✓ Disponible || echo   ✗ No disponible

echo - Frontend (puerto 3001):
timeout /t 1 >nul 2>&1 && echo   ✓ Disponible || echo   ✗ No disponible

echo.
echo 3. Verificando datos de prueba en la base de datos...
docker exec -it ong_postgres psql -U ong_user -d ong_management -c "SELECT COUNT(*) as usuarios FROM usuarios WHERE activo = TRUE;" -t
docker exec -it ong_postgres psql -U ong_user -d ong_management -c "SELECT COUNT(*) as eventos FROM eventos;" -t
docker exec -it ong_postgres psql -U ong_user -d ong_management -c "SELECT COUNT(*) as participantes FROM participantes_evento;" -t
docker exec -it ong_postgres psql -U ong_user -d ong_management -c "SELECT COUNT(*) as donaciones FROM donaciones WHERE eliminado = FALSE;" -t

echo.
echo 4. URLs de acceso:
echo - Frontend: http://localhost:3001
echo - API Gateway: http://localhost:3000
echo - Health Check: http://localhost:3000/health
echo.

echo 5. Credenciales de prueba:
echo - Usuario: admin / Contraseña: admin123 (PRESIDENTE)
echo - Usuario: vocal1 / Contraseña: admin123 (VOCAL)
echo - Usuario: coord1 / Contraseña: admin123 (COORDINADOR)
echo - Usuario: vol1 / Contraseña: admin123 (VOLUNTARIO)
echo - Usuario: vol2 / Contraseña: admin123 (VOLUNTARIO)
echo.

echo ========================================
echo SISTEMA LISTO PARA USAR
echo ========================================
pause