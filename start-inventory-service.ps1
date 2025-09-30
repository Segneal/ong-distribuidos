# Script para iniciar el Inventory Service
Write-Host "Iniciando Inventory Service..." -ForegroundColor Green

# Variables de entorno
$env:DB_HOST = "localhost"
$env:DB_NAME = "ong_management"
$env:DB_USER = "ong_user"
$env:DB_PASSWORD = "ong_pass"
$env:DB_PORT = "5432"
$env:GRPC_PORT = "50052"
$env:ORGANIZATION_ID = "empuje-comunitario"

# Cambiar al directorio del servicio
Set-Location inventory-service

Write-Host "Variables de entorno configuradas:" -ForegroundColor Yellow
Write-Host "   DB_HOST: $env:DB_HOST" -ForegroundColor White
Write-Host "   GRPC_PORT: $env:GRPC_PORT" -ForegroundColor White

Write-Host ""
Write-Host "Iniciando Inventory Service en puerto 50052..." -ForegroundColor Cyan

# Iniciar el servicio
python src/inventory_service.py