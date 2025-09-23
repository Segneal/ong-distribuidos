@echo off
echo 🚀 Iniciando User Service...

cd user-service

REM Configurar variables de entorno para UTF-8
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set LC_ALL=C.UTF-8
set LANG=C.UTF-8

echo 📋 Configuración:
echo   PYTHONIOENCODING=%PYTHONIOENCODING%
echo   PYTHONUTF8=%PYTHONUTF8%
echo.

echo 🔄 Iniciando servidor gRPC en puerto 50051...
python src/server.py

pause