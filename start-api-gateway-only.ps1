# Script para iniciar solo el API Gateway con las rutas de messaging arregladas
Write-Host "Iniciando API Gateway con rutas de messaging arregladas..." -ForegroundColor Green

# Variables de entorno
$env:DB_HOST = "localhost"
$env:DB_NAME = "ong_management"
$env:DB_USER = "ong_user"
$env:DB_PASSWORD = "ong_pass"
$env:DB_PORT = "5432"
$env:JWT_SECRET = "your-secret-key-change-in-production"
$env:JWT_EXPIRES_IN = "15m"
$env:REFRESH_TOKEN_EXPIRES_IN = "7d"
$env:USER_SERVICE_URL = "localhost:50051"
$env:INVENTORY_SERVICE_URL = "localhost:50052"
$env:EVENTS_SERVICE_URL = "localhost:50053"
$env:EMAIL_SERVICE_URL = "http://localhost:3002"

# Cambiar al directorio del API Gateway
Set-Location api-gateway

Write-Host "Variables de entorno configuradas:" -ForegroundColor Yellow
Write-Host "   DB_HOST: $env:DB_HOST" -ForegroundColor White
Write-Host "   DB_PORT: $env:DB_PORT" -ForegroundColor White
Write-Host "   JWT_SECRET: [CONFIGURADO]" -ForegroundColor White

Write-Host ""
Write-Host "Iniciando API Gateway en puerto 3000..." -ForegroundColor Cyan

# Iniciar el API Gateway
npm start