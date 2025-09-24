#!/usr/bin/env pwsh
# Script rápido para levantar el sistema ONG (sin limpieza)

Write-Host "🚀 INICIANDO SISTEMA ONG" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

# Función para esperar que un servicio esté listo
function Wait-ForService {
    param(
        [string]$Url,
        [string]$ServiceName,
        [int]$MaxAttempts = 20
    )
    
    Write-Host "⏳ Esperando $ServiceName..." -ForegroundColor Yellow
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $response = Invoke-RestMethod -Uri $Url -TimeoutSec 3 -ErrorAction Stop
            Write-Host "✅ $ServiceName listo!" -ForegroundColor Green
            return $true
        }
        catch {
            Write-Host "   Intento $i/$MaxAttempts..." -ForegroundColor Gray
            Start-Sleep -Seconds 2
        }
    }
    
    Write-Host "❌ $ServiceName no respondió" -ForegroundColor Red
    return $false
}

Write-Host "`n📋 Verificando Docker..." -ForegroundColor Cyan
try {
    docker ps | Out-Null
    Write-Host "✅ Docker OK" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker no está corriendo. Inicia Docker Desktop" -ForegroundColor Red
    exit 1
}

Write-Host "`n🏗️ Construyendo imágenes..." -ForegroundColor Cyan
docker-compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error en build" -ForegroundColor Red
    exit 1
}

Write-Host "`n🚀 Iniciando servicios..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al iniciar servicios" -ForegroundColor Red
    exit 1
}

Write-Host "`n⏳ Esperando servicios..." -ForegroundColor Cyan

# Esperar base de datos
Write-Host "🗄️ Esperando PostgreSQL..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Esperar microservicios
Write-Host "🔧 Esperando microservicios..." -ForegroundColor Yellow
Start-Sleep -Seconds 12

# Verificar API Gateway
if (-not (Wait-ForService -Url "http://localhost:3001/health" -ServiceName "API Gateway")) {
    Write-Host "⚠️ API Gateway tardó en responder, pero puede estar iniciando..." -ForegroundColor Yellow
}

# Verificar Frontend
if (-not (Wait-ForService -Url "http://localhost:3000" -ServiceName "Frontend")) {
    Write-Host "⚠️ Frontend tardó en responder, pero puede estar iniciando..." -ForegroundColor Yellow
}

Write-Host "`n🧪 Prueba rápida..." -ForegroundColor Cyan
try {
    $loginBody = @{
        usernameOrEmail = "admin"
        password = "admin123"
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "http://localhost:3001/auth/login" -Method POST -Body $loginBody -ContentType "application/json" -TimeoutSec 10
    
    if ($loginResponse.token) {
        Write-Host "✅ Sistema funcionando correctamente!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Sistema iniciado, pero login falló" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠️ Sistema iniciado, verificando manualmente..." -ForegroundColor Yellow
}

Write-Host "`n📊 Estado de servicios:" -ForegroundColor Cyan
docker-compose ps

Write-Host "`n🎯 SISTEMA INICIADO!" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green

Write-Host "`n🌐 URLs:" -ForegroundColor Blue
Write-Host "   Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "   API Gateway: http://localhost:3001" -ForegroundColor White

Write-Host "`n🔐 Login:" -ForegroundColor Blue
Write-Host "   Usuario: admin" -ForegroundColor White
Write-Host "   Contraseña: admin123" -ForegroundColor White

Write-Host "`n📝 Si algo no funciona:" -ForegroundColor Yellow
Write-Host "   docker-compose logs -f" -ForegroundColor White
Write-Host "   docker-compose restart" -ForegroundColor White