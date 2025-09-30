# Script maestro para iniciar todos los servicios localmente
Write-Host "=== INICIANDO SISTEMA COMPLETO LOCALMENTE ===" -ForegroundColor Green
Write-Host ""

# Verificar que la base de datos esté corriendo
Write-Host "1. Verificando base de datos..." -ForegroundColor Yellow
try {
    $testConnection = Test-NetConnection -ComputerName localhost -Port 5432 -InformationLevel Quiet
    if (-not $testConnection) {
        Write-Host "   ERROR: La base de datos no está disponible" -ForegroundColor Red
        Write-Host "   Ejecuta: docker-compose -f docker-compose-minimal.yml up -d" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "   Base de datos OK" -ForegroundColor Green
} catch {
    Write-Host "   ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "2. Iniciando servicios en orden..." -ForegroundColor Yellow

# Función para iniciar servicio en nueva ventana
function Start-ServiceWindow {
    param(
        [string]$Title,
        [string]$Script
    )
    
    Write-Host "   Iniciando $Title..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { Set-Location '$PWD'; .\$Script }" -WindowStyle Normal
    Start-Sleep -Seconds 3
}

# Iniciar servicios
Start-ServiceWindow "User Service" "start-user-service.ps1"
Start-ServiceWindow "Inventory Service" "start-inventory-service.ps1"
Start-ServiceWindow "Events Service" "start-events-service.ps1"
Start-ServiceWindow "API Gateway" "start-api-gateway-only.ps1"
Start-ServiceWindow "Frontend" "start-frontend.ps1"

Write-Host ""
Write-Host "=== TODOS LOS SERVICIOS INICIADOS ===" -ForegroundColor Green
Write-Host ""
Write-Host "Servicios disponibles:" -ForegroundColor Yellow
Write-Host "   Base de datos: localhost:5432" -ForegroundColor White
Write-Host "   MailHog UI: http://localhost:8025" -ForegroundColor White
Write-Host "   User Service: localhost:50051 (gRPC)" -ForegroundColor White
Write-Host "   Inventory Service: localhost:50052 (gRPC)" -ForegroundColor White
Write-Host "   Events Service: localhost:50053 (gRPC)" -ForegroundColor White
Write-Host "   API Gateway: http://localhost:3000" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3001" -ForegroundColor White
Write-Host ""
Write-Host "Para detener todos los servicios:" -ForegroundColor Yellow
Write-Host "   .\stop-local-services.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Presiona cualquier tecla para continuar..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")