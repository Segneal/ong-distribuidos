#!/usr/bin/env pwsh
# Script completo para levantar el sistema ONG desde cero

Write-Host "🚀 SETUP COMPLETO DEL SISTEMA ONG DESDE CERO" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Función para verificar comandos
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Función para esperar que un servicio esté listo
function Wait-ForService {
    param(
        [string]$Url,
        [string]$ServiceName,
        [int]$MaxAttempts = 30
    )
    
    Write-Host "⏳ Esperando que $ServiceName esté listo..." -ForegroundColor Yellow
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $response = Invoke-RestMethod -Uri $Url -TimeoutSec 5 -ErrorAction Stop
            Write-Host "✅ $ServiceName está listo!" -ForegroundColor Green
            return $true
        }
        catch {
            Write-Host "   Intento $i/$MaxAttempts - Esperando..." -ForegroundColor Gray
            Start-Sleep -Seconds 2
        }
    }
    
    Write-Host "❌ $ServiceName no respondió después de $MaxAttempts intentos" -ForegroundColor Red
    return $false
}

Write-Host "`n📋 PASO 1: Verificación de prerrequisitos" -ForegroundColor Cyan

# Verificar Docker
if (-not (Test-Command "docker")) {
    Write-Host "❌ Docker no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "   Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Verificar Docker Compose
if (-not (Test-Command "docker-compose")) {
    Write-Host "❌ Docker Compose no está disponible" -ForegroundColor Red
    Write-Host "   Docker Compose debería venir con Docker Desktop" -ForegroundColor Yellow
    exit 1
}

# Verificar que Docker esté corriendo
try {
    docker ps | Out-Null
    Write-Host "✅ Docker está corriendo" -ForegroundColor Green
}
catch {
    Write-Host "❌ Docker no está corriendo. Inicia Docker Desktop" -ForegroundColor Red
    exit 1
}

Write-Host "`n🧹 PASO 2: Limpieza de contenedores anteriores" -ForegroundColor Cyan

Write-Host "🔍 Deteniendo contenedores existentes..." -ForegroundColor Yellow
docker-compose down --remove-orphans 2>$null

Write-Host "🗑️ Eliminando imágenes anteriores del proyecto..." -ForegroundColor Yellow
$images = docker images --format "{{.Repository}}:{{.Tag}}" | Where-Object { $_ -match "ong-management|user-service|inventory-service|events-service|api-gateway|frontend" }
if ($images) {
    $images | ForEach-Object { docker rmi $_ --force 2>$null }
    Write-Host "✅ Imágenes anteriores eliminadas" -ForegroundColor Green
} else {
    Write-Host "ℹ️  No hay imágenes anteriores que eliminar" -ForegroundColor Blue
}

Write-Host "🧽 Limpiando volúmenes no utilizados..." -ForegroundColor Yellow
docker volume prune -f 2>$null

Write-Host "`n🏗️ PASO 3: Construcción de imágenes desde cero" -ForegroundColor Cyan

Write-Host "📦 Construyendo todas las imágenes (esto puede tomar varios minutos)..." -ForegroundColor Yellow
$buildResult = docker-compose build --no-cache --parallel

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error en la construcción de imágenes" -ForegroundColor Red
    Write-Host "   Revisa los logs arriba para más detalles" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Todas las imágenes construidas exitosamente" -ForegroundColor Green

Write-Host "`n🚀 PASO 4: Iniciando todos los servicios" -ForegroundColor Cyan

Write-Host "🔄 Levantando servicios en segundo plano..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al iniciar los servicios" -ForegroundColor Red
    Write-Host "   Ejecuta 'docker-compose logs' para ver los errores" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n⏳ PASO 5: Esperando que los servicios estén listos" -ForegroundColor Cyan

# Esperar base de datos
Write-Host "🗄️ Esperando PostgreSQL..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Esperar microservicios (verificar logs en lugar de endpoints HTTP)
Write-Host "🔧 Esperando microservicios gRPC..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Verificar API Gateway
if (-not (Wait-ForService -Url "http://localhost:3001/health" -ServiceName "API Gateway")) {
    Write-Host "❌ API Gateway no está respondiendo" -ForegroundColor Red
    Write-Host "   Ejecutando diagnóstico..." -ForegroundColor Yellow
    docker-compose logs api-gateway --tail=20
    exit 1
}

# Verificar Frontend
if (-not (Wait-ForService -Url "http://localhost:3000" -ServiceName "Frontend")) {
    Write-Host "❌ Frontend no está respondiendo" -ForegroundColor Red
    Write-Host "   Ejecutando diagnóstico..." -ForegroundColor Yellow
    docker-compose logs frontend --tail=20
    exit 1
}

Write-Host "`n🧪 PASO 6: Prueba rápida del sistema" -ForegroundColor Cyan

# Test de login
Write-Host "🔐 Probando autenticación..." -ForegroundColor Yellow
try {
    $loginBody = @{
        usernameOrEmail = "admin"
        password = "admin123"
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "http://localhost:3001/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    
    if ($loginResponse.token) {
        Write-Host "✅ Autenticación funcionando correctamente" -ForegroundColor Green
        
        # Test rápido de endpoints
        $headers = @{ "Authorization" = "Bearer $($loginResponse.token)" }
        
        Write-Host "👥 Probando endpoint de usuarios..." -ForegroundColor Yellow
        $users = Invoke-RestMethod -Uri "http://localhost:3001/users" -Headers $headers
        Write-Host "✅ Usuarios: $($users.Count) encontrados" -ForegroundColor Green
        
        Write-Host "📦 Probando endpoint de inventario..." -ForegroundColor Yellow
        $inventory = Invoke-RestMethod -Uri "http://localhost:3001/inventory" -Headers $headers
        Write-Host "✅ Inventario: $($inventory.Count) items encontrados" -ForegroundColor Green
        
        Write-Host "🎉 Probando endpoint de eventos..." -ForegroundColor Yellow
        $events = Invoke-RestMethod -Uri "http://localhost:3001/events" -Headers $headers
        Write-Host "✅ Eventos: $($events.Count) eventos encontrados" -ForegroundColor Green
        
    } else {
        Write-Host "❌ Login falló - no se recibió token" -ForegroundColor Red
    }
}
catch {
    Write-Host "❌ Error en prueba de autenticación: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📊 PASO 7: Estado final del sistema" -ForegroundColor Cyan

Write-Host "🔍 Estado de contenedores:" -ForegroundColor Yellow
docker-compose ps

Write-Host "`n🎯 SISTEMA LISTO PARA USAR!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

Write-Host "`n🌐 URLs de acceso:" -ForegroundColor Blue
Write-Host "   Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "   API Gateway: http://localhost:3001" -ForegroundColor White
Write-Host "   Health Check: http://localhost:3001/health" -ForegroundColor White

Write-Host "`n🔐 Credenciales de prueba:" -ForegroundColor Blue
Write-Host "   Admin:       admin / admin123" -ForegroundColor White
Write-Host "   Coordinador: coord1 / admin123" -ForegroundColor White
Write-Host "   Voluntario:  vol1 / admin123" -ForegroundColor White

Write-Host "`n📝 Próximos pasos:" -ForegroundColor Yellow
Write-Host "   1. Abre http://localhost:3000 en tu navegador" -ForegroundColor White
Write-Host "   2. Haz login con admin/admin123" -ForegroundColor White
Write-Host "   3. Explora las funcionalidades del sistema" -ForegroundColor White
Write-Host "   4. Ejecuta .\test-sistema-completo.ps1 para pruebas automáticas" -ForegroundColor White

Write-Host "`n🛠️ Comandos útiles:" -ForegroundColor Yellow
Write-Host "   Ver logs:     docker-compose logs -f" -ForegroundColor White
Write-Host "   Reiniciar:    docker-compose restart" -ForegroundColor White
Write-Host "   Detener:      docker-compose down" -ForegroundColor White
Write-Host "   Estado:       docker-compose ps" -ForegroundColor White

Write-Host "`n✨ ¡Sistema completamente operativo!" -ForegroundColor Green