# Script para iniciar el User Service
Write-Host "Iniciando User Service..." -ForegroundColor Green

# Variables de entorno
$env:DB_HOST = "localhost"
$env:DB_NAME = "ong_management"
$env:DB_USER = "ong_user"
$env:DB_PASSWORD = "ong_pass"
$env:DB_PORT = "5432"
$env:GRPC_PORT = "50051"
$env:JWT_SECRET = "your-secret-key-change-in-production"
$env:ORGANIZATION_ID = "empuje-comunitario"

# Cambiar al directorio del servicio
Set-Location user-service

Write-Host "Variables de entorno configuradas:" -ForegroundColor Yellow
Write-Host "   DB_HOST: $env:DB_HOST" -ForegroundColor White
Write-Host "   GRPC_PORT: $env:GRPC_PORT" -ForegroundColor White

Write-Host ""
Write-Host "Iniciando User Service en puerto 50051..." -ForegroundColor Cyan

# Iniciar el servicio
python src/user_service.py