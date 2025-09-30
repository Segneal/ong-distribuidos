# Script para iniciar el Events Service
Write-Host "Iniciando Events Service..." -ForegroundColor Green

# Variables de entorno
$env:DB_HOST = "localhost"
$env:DB_NAME = "ong_management"
$env:DB_USER = "ong_user"
$env:DB_PASSWORD = "ong_pass"
$env:DB_PORT = "5432"
$env:EVENTS_SERVICE_PORT = "50053"
$env:ORGANIZATION_ID = "empuje-comunitario"

# Cambiar al directorio del servicio
Set-Location events-service

Write-Host "Variables de entorno configuradas:" -ForegroundColor Yellow
Write-Host "   DB_HOST: $env:DB_HOST" -ForegroundColor White
Write-Host "   EVENTS_SERVICE_PORT: $env:EVENTS_SERVICE_PORT" -ForegroundColor White

Write-Host ""
Write-Host "Iniciando Events Service en puerto 50053..." -ForegroundColor Cyan

# Iniciar el servicio
python src/events_service.py