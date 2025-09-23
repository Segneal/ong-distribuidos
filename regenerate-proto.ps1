# Script para regenerar archivos protobuf
Write-Host "🔄 Regenerando archivos protobuf..." -ForegroundColor Green

# Función para regenerar protobuf de un servicio
function Regenerate-Proto {
    param(
        [string]$ServiceName,
        [string]$ServicePath,
        [string]$ProtoFile
    )
    
    Write-Host "🔧 Regenerando $ServiceName..." -ForegroundColor Yellow
    
    Push-Location $ServicePath
    
    try {
        # Instalar/actualizar dependencias
        Write-Host "📦 Instalando dependencias..." -ForegroundColor Cyan
        pip install --upgrade protobuf==4.25.1 | Out-Null
        pip install -r requirements.txt | Out-Null
        
        # Regenerar archivos protobuf
        Write-Host "⚙️  Generando archivos protobuf..." -ForegroundColor Cyan
        python -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/$ProtoFile
        
        Write-Host "✅ $ServiceName completado" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Error en $ServiceName`: $($_.Exception.Message)" -ForegroundColor Red
    }
    finally {
        Pop-Location
    }
}

# Regenerar todos los servicios
Regenerate-Proto -ServiceName "User Service" -ServicePath "user-service" -ProtoFile "users.proto"
Regenerate-Proto -ServiceName "Inventory Service" -ServicePath "inventory-service" -ProtoFile "inventory.proto"
Regenerate-Proto -ServiceName "Events Service" -ServicePath "events-service" -ProtoFile "events.proto"

Write-Host ""
Write-Host "🎉 Regeneración de protobuf completada!" -ForegroundColor Green
Write-Host "Ahora puedes ejecutar los servicios con:" -ForegroundColor Cyan
Write-Host "  .\start-services.ps1" -ForegroundColor White