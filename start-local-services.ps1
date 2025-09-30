# Script para iniciar todos los servicios localmente
Write-Host "🚀 Iniciando servicios localmente..." -ForegroundColor Green

# Variables de entorno comunes
$env:DB_HOST = "localhost"
$env:DB_NAME = "ong_management"
$env:DB_USER = "ong_user"
$env:DB_PASSWORD = "ong_pass"
$env:DB_PORT = "5432"
$env:JWT_SECRET = "your-secret-key-change-in-production"
$env:ORGANIZATION_ID = "empuje-comunitario"

# Verificar que la base de datos esté corriendo
Write-Host "📊 Verificando conexión a la base de datos..." -ForegroundColor Yellow
try {
    $testConnection = Test-NetConnection -ComputerName localhost -Port 5432 -InformationLevel Quiet
    if (-not $testConnection) {
        Write-Host "❌ Error: La base de datos no está disponible en puerto 5432" -ForegroundColor Red
        Write-Host "   Ejecuta: docker-compose -f docker-compose-minimal.yml up -d" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Base de datos disponible" -ForegroundColor Green
} catch {
    Write-Host "❌ Error verificando la base de datos: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Función para iniciar un servicio en background
function Start-ServiceInBackground {
    param(
        [string]$ServiceName,
        [string]$WorkingDirectory,
        [string]$Command,
        [hashtable]$EnvVars = @{}
    )
    
    Write-Host "🔄 Iniciando $ServiceName..." -ForegroundColor Cyan
    
    # Crear un nuevo proceso PowerShell para ejecutar el servicio
    $processArgs = @{
        FilePath = "powershell.exe"
        ArgumentList = @(
            "-NoProfile",
            "-WindowStyle", "Minimized",
            "-Command", "cd '$WorkingDirectory'; $Command"
        )
        PassThru = $true
        WindowStyle = "Minimized"
    }
    
    # Agregar variables de entorno si se proporcionan
    if ($EnvVars.Count -gt 0) {
        $envString = ($EnvVars.GetEnumerator() | ForEach-Object { "`$env:$($_.Key) = '$($_.Value)'" }) -join "; "
        $processArgs.ArgumentList[3] = "$envString; cd '$WorkingDirectory'; $Command"
    }
    
    $process = Start-Process @processArgs
    Write-Host "✅ $ServiceName iniciado (PID: $($process.Id))" -ForegroundColor Green
    return $process
}

# Iniciar servicios
$processes = @()

# 1. User Service (gRPC en puerto 50051)
$userEnv = @{
    "GRPC_PORT" = "50051"
}
$processes += Start-ServiceInBackground -ServiceName "User Service" -WorkingDirectory "user-service" -Command "python src/user_service.py" -EnvVars $userEnv

Start-Sleep -Seconds 2

# 2. Inventory Service (gRPC en puerto 50052)
$inventoryEnv = @{
    "GRPC_PORT" = "50052"
}
$processes += Start-ServiceInBackground -ServiceName "Inventory Service" -WorkingDirectory "inventory-service" -Command "python src/inventory_service.py" -EnvVars $inventoryEnv

Start-Sleep -Seconds 2

# 3. Events Service (gRPC en puerto 50053)
$eventsEnv = @{
    "EVENTS_SERVICE_PORT" = "50053"
}
$processes += Start-ServiceInBackground -ServiceName "Events Service" -WorkingDirectory "events-service" -Command "python src/events_service.py" -EnvVars $eventsEnv

Start-Sleep -Seconds 2

# 4. API Gateway (HTTP en puerto 3000)
$gatewayEnv = @{
    "USER_SERVICE_URL" = "localhost:50051"
    "INVENTORY_SERVICE_URL" = "localhost:50052"
    "EVENTS_SERVICE_URL" = "localhost:50053"
    "EMAIL_SERVICE_URL" = "http://localhost:3002"
    "JWT_EXPIRES_IN" = "15m"
    "REFRESH_TOKEN_EXPIRES_IN" = "7d"
}
$processes += Start-ServiceInBackground -ServiceName "API Gateway" -WorkingDirectory "api-gateway" -Command "npm start" -EnvVars $gatewayEnv

Start-Sleep -Seconds 3

# 5. Frontend (React en puerto 3001)
$processes += Start-ServiceInBackground -ServiceName "Frontend" -WorkingDirectory "frontend" -Command "npm start"

Write-Host ""
Write-Host "🎉 Todos los servicios han sido iniciados!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Servicios disponibles:" -ForegroundColor Yellow
Write-Host "   • Base de datos: localhost:5432" -ForegroundColor White
Write-Host "   • MailHog UI: http://localhost:8025" -ForegroundColor White
Write-Host "   • User Service: localhost:50051 (gRPC)" -ForegroundColor White
Write-Host "   • Inventory Service: localhost:50052 (gRPC)" -ForegroundColor White
Write-Host "   • Events Service: localhost:50053 (gRPC)" -ForegroundColor White
Write-Host "   • API Gateway: http://localhost:3000" -ForegroundColor White
Write-Host "   • Frontend: http://localhost:3001" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Para detener todos los servicios, ejecuta: .\stop-local-services.ps1" -ForegroundColor Yellow
Write-Host ""

# Esperar a que el usuario presione una tecla para salir
Write-Host "Presiona cualquier tecla para salir (los servicios seguirán ejecutándose)..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Guardar los PIDs para poder detenerlos después
$processes | ForEach-Object { $_.Id } | Out-File -FilePath "service-pids.txt" -Encoding UTF8