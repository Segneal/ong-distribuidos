# Script para levantar todos los microservicios de la ONG
Write-Host "🚀 Iniciando microservicios de ONG Empuje Comunitario..." -ForegroundColor Green

# Verificar si los puertos están disponibles
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

# Verificar puertos
$ports = @(50051, 50052, 50053)
foreach ($port in $ports) {
    if (Test-Port $port) {
        Write-Host "⚠️  Puerto $port ya está en uso. Deteniendo proceso..." -ForegroundColor Yellow
        $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
        if ($process) {
            Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
        }
    }
}

# Verificar si Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no encontrado. Por favor instala Python 3.8+" -ForegroundColor Red
    exit 1
}

# Verificar si Node.js está instalado
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js no encontrado. Por favor instala Node.js" -ForegroundColor Red
    exit 1
}

# Función para iniciar un servicio Python en background
function Start-PythonService {
    param(
        [string]$ServiceName,
        [string]$ServicePath,
        [string]$Port
    )
    
    Write-Host "🔄 Iniciando $ServiceName en puerto $Port..." -ForegroundColor Yellow
    
    # Cambiar al directorio del servicio
    Push-Location $ServicePath
    
    # Instalar dependencias si es necesario
    if (Test-Path "requirements.txt") {
        Write-Host "📦 Instalando dependencias para $ServiceName..." -ForegroundColor Cyan
        pip install -r requirements.txt | Out-Null
    }
    
    # Iniciar el servicio en background
    $job = Start-Job -ScriptBlock {
        param($path)
        Set-Location $path
        python src/server.py
    } -ArgumentList (Get-Location).Path
    
    Pop-Location
    
    Write-Host "✅ $ServiceName iniciado (Job ID: $($job.Id))" -ForegroundColor Green
    return $job
}

# Array para almacenar los jobs
$jobs = @()

# Iniciar User Service (Puerto 50051)
$userServiceJob = Start-PythonService -ServiceName "User Service" -ServicePath "user-service" -Port "50051"
$jobs += $userServiceJob

# Esperar un poco entre servicios
Start-Sleep -Seconds 2

# Iniciar Inventory Service (Puerto 50052)
$inventoryServiceJob = Start-PythonService -ServiceName "Inventory Service" -ServicePath "inventory-service" -Port "50052"
$jobs += $inventoryServiceJob

# Esperar un poco entre servicios
Start-Sleep -Seconds 2

# Iniciar Events Service (Puerto 50053)
$eventsServiceJob = Start-PythonService -ServiceName "Events Service" -ServicePath "events-service" -Port "50053"
$jobs += $eventsServiceJob

# Esperar un poco para que los servicios se inicien
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "🎉 Todos los microservicios han sido iniciados!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Servicios ejecutándose:" -ForegroundColor Cyan
Write-Host "  • User Service:      localhost:50051" -ForegroundColor White
Write-Host "  • Inventory Service: localhost:50052" -ForegroundColor White
Write-Host "  • Events Service:    localhost:50053" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Para iniciar el API Gateway:" -ForegroundColor Yellow
Write-Host "  cd api-gateway" -ForegroundColor White
Write-Host "  npm start" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Para iniciar el Frontend:" -ForegroundColor Yellow
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  npm start" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Para detener todos los servicios, presiona Ctrl+C" -ForegroundColor Red
Write-Host ""

# Función para limpiar jobs al salir
function Stop-AllServices {
    Write-Host ""
    Write-Host "🛑 Deteniendo todos los servicios..." -ForegroundColor Yellow
    
    foreach ($job in $jobs) {
        if ($job.State -eq "Running") {
            Stop-Job $job
            Remove-Job $job
            Write-Host "✅ Servicio detenido (Job ID: $($job.Id))" -ForegroundColor Green
        }
    }
    
    Write-Host "👋 Todos los servicios han sido detenidos." -ForegroundColor Green
}

# Registrar el handler para Ctrl+C
Register-EngineEvent PowerShell.Exiting -Action { Stop-AllServices }

# Mantener el script ejecutándose y mostrar el estado de los jobs
try {
    while ($true) {
        Start-Sleep -Seconds 10
        
        # Verificar el estado de los jobs
        $runningJobs = $jobs | Where-Object { $_.State -eq "Running" }
        $failedJobs = $jobs | Where-Object { $_.State -eq "Failed" }
        
        if ($failedJobs.Count -gt 0) {
            Write-Host "❌ Algunos servicios han fallado:" -ForegroundColor Red
            foreach ($job in $failedJobs) {
                $error = Receive-Job $job 2>&1
                Write-Host "  Job ID $($job.Id): $error" -ForegroundColor Red
            }
        }
        
        if ($runningJobs.Count -eq 0) {
            Write-Host "⚠️  Todos los servicios se han detenido." -ForegroundColor Yellow
            break
        }
    }
} catch {
    Write-Host "🛑 Script interrumpido por el usuario." -ForegroundColor Yellow
} finally {
    Stop-AllServices
}