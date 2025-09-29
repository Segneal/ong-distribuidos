# Script para iniciar el sistema ONG con Docker Compose
Write-Host "🐳 Iniciando Sistema ONG con Docker Compose..." -ForegroundColor Green
Write-Host ""

# Verificar Docker
Write-Host "🔍 Verificando Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    Write-Host "✅ $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está instalado o no está ejecutándose" -ForegroundColor Red
    Write-Host "💡 Por favor instala Docker Desktop y asegúrate de que esté ejecutándose" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

try {
    $composeVersion = docker-compose --version 2>$null
    Write-Host "✅ $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose no está disponible" -ForegroundColor Red
    Write-Host "💡 Por favor instala Docker Compose" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""

# Detener contenedores existentes
Write-Host "🛑 Deteniendo contenedores existentes..." -ForegroundColor Yellow
docker-compose down 2>$null

Write-Host ""
Write-Host "🏗️  Construyendo e iniciando servicios..." -ForegroundColor Yellow
Write-Host "⏳ Esto puede tomar varios minutos la primera vez..." -ForegroundColor Cyan

# Iniciar servicios
docker-compose up --build -d

Write-Host ""
Write-Host "📋 Verificando estado de los servicios..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
docker-compose ps

Write-Host ""
Write-Host "🎉 Sistema iniciado!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Servicios disponibles:" -ForegroundColor Cyan
Write-Host "  🗄️  PostgreSQL:     localhost:5432" -ForegroundColor White
Write-Host "  📨 Kafka:          localhost:9092" -ForegroundColor White
Write-Host "  👥 User Service:    localhost:50051 (gRPC)" -ForegroundColor White
Write-Host "  📦 Inventory:       localhost:50052 (gRPC)" -ForegroundColor White
Write-Host "  📅 Events:          localhost:50053 (gRPC)" -ForegroundColor White
Write-Host "  💬 Messaging:       localhost:50054 (HTTP)" -ForegroundColor White
Write-Host "  📧 Email Service:   localhost:3002" -ForegroundColor White
Write-Host "  📬 MailHog UI:      http://localhost:8025" -ForegroundColor White
Write-Host "  🌐 API Gateway:     http://localhost:3000" -ForegroundColor White
Write-Host "  💻 Frontend:        http://localhost:3001" -ForegroundColor White
Write-Host ""
Write-Host "🔍 Verificando servicios..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
docker-compose logs --tail=5 user-service
docker-compose logs --tail=5 api-gateway
Write-Host ""
Write-Host "🔧 Comandos útiles:" -ForegroundColor Cyan
Write-Host "  Ver logs:           docker-compose logs -f" -ForegroundColor White
Write-Host "  Ver logs específicos: docker-compose logs -f [servicio]" -ForegroundColor White
Write-Host "  Detener sistema:    docker-compose down" -ForegroundColor White
Write-Host "  Reiniciar:          docker-compose restart" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Abre tu navegador en: http://localhost:3001" -ForegroundColor Green
Write-Host ""

# Preguntar si quiere ver los logs
$response = Read-Host "¿Quieres ver los logs en tiempo real? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Host "📊 Mostrando logs... (Presiona Ctrl+C para salir)" -ForegroundColor Yellow
    docker-compose logs -f
}