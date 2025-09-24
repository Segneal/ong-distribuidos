#!/usr/bin/env pwsh
# Script de prueba rápida del sistema ONG

Write-Host "🚀 Iniciando prueba rápida del sistema ONG..." -ForegroundColor Green

# Función para hacer peticiones HTTP
function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [string]$Body = $null,
        [string]$Description
    )
    
    Write-Host "🔍 Probando: $Description" -ForegroundColor Yellow
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $Headers
            ContentType = "application/json"
        }
        
        if ($Body) {
            $params.Body = $Body
        }
        
        $response = Invoke-RestMethod @params
        Write-Host "✅ OK: $Description" -ForegroundColor Green
        return $response
    }
    catch {
        Write-Host "❌ ERROR: $Description - $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Variables
$API_BASE = "http://localhost:3001"
$token = $null

Write-Host "`n📋 FASE 1: Verificación de servicios básicos" -ForegroundColor Cyan

# 1. Health Check
Test-Endpoint -Url "$API_BASE/health" -Description "Health Check del API Gateway"

# 2. Login y obtener token
Write-Host "`n🔐 FASE 2: Autenticación" -ForegroundColor Cyan
$loginBody = @{
    usernameOrEmail = "admin"
    password = "admin123"
} | ConvertTo-Json

$loginResponse = Test-Endpoint -Url "$API_BASE/auth/login" -Method "POST" -Body $loginBody -Description "Login como admin"

if ($loginResponse -and $loginResponse.token) {
    $token = $loginResponse.token
    $headers = @{ "Authorization" = "Bearer $token" }
    Write-Host "✅ Token obtenido correctamente" -ForegroundColor Green
} else {
    Write-Host "❌ No se pudo obtener el token. Abortando pruebas." -ForegroundColor Red
    exit 1
}

Write-Host "`n👥 FASE 3: Gestión de Usuarios" -ForegroundColor Cyan

# 3. Listar usuarios
Test-Endpoint -Url "$API_BASE/users" -Headers $headers -Description "Listar usuarios"

# 4. Obtener perfil actual
Test-Endpoint -Url "$API_BASE/users/profile" -Headers $headers -Description "Obtener perfil del usuario actual"

Write-Host "`n📦 FASE 4: Gestión de Inventario" -ForegroundColor Cyan

# 5. Listar inventario
Test-Endpoint -Url "$API_BASE/inventory" -Headers $headers -Description "Listar inventario"

# 6. Crear donación de prueba
$donationBody = @{
    donor_name = "Donante de Prueba"
    donor_email = "prueba@test.com"
    donor_phone = "123456789"
    items = @(
        @{
            name = "Arroz"
            quantity = 10
            unit = "kg"
            category = "ALIMENTOS"
            expiry_date = "2024-12-31"
        }
    )
} | ConvertTo-Json -Depth 3

$donationResponse = Test-Endpoint -Url "$API_BASE/inventory/donations" -Method "POST" -Headers $headers -Body $donationBody -Description "Crear donación de prueba"

Write-Host "`n🎉 FASE 5: Gestión de Eventos" -ForegroundColor Cyan

# 7. Listar eventos
Test-Endpoint -Url "$API_BASE/events" -Headers $headers -Description "Listar eventos"

# 8. Crear evento de prueba
$eventBody = @{
    name = "Evento de Prueba"
    description = "Evento creado para pruebas del sistema"
    event_date = "2024-12-25T10:00:00Z"
    location = "Centro Comunitario"
    max_participants = 50
    event_type = "DISTRIBUCION"
} | ConvertTo-Json

$eventResponse = Test-Endpoint -Url "$API_BASE/events" -Method "POST" -Headers $headers -Body $eventBody -Description "Crear evento de prueba"

if ($eventResponse -and $eventResponse.id) {
    $eventId = $eventResponse.id
    
    # 9. Obtener detalles del evento creado
    Test-Endpoint -Url "$API_BASE/events/$eventId" -Headers $headers -Description "Obtener detalles del evento creado"
    
    # 10. Inscribirse al evento
    Test-Endpoint -Url "$API_BASE/events/$eventId/participate" -Method "POST" -Headers $headers -Description "Inscribirse al evento"
    
    # 11. Ver participantes del evento
    Test-Endpoint -Url "$API_BASE/events/$eventId/participants" -Headers $headers -Description "Ver participantes del evento"
}

Write-Host "`n🔄 FASE 6: Pruebas con diferentes roles" -ForegroundColor Cyan

# 12. Login como coordinador
$coordLoginBody = @{
    usernameOrEmail = "coord1"
    password = "admin123"
} | ConvertTo-Json

$coordLoginResponse = Test-Endpoint -Url "$API_BASE/auth/login" -Method "POST" -Body $coordLoginBody -Description "Login como coordinador"

if ($coordLoginResponse -and $coordLoginResponse.token) {
    $coordHeaders = @{ "Authorization" = "Bearer $($coordLoginResponse.token)" }
    
    # 13. Coordinador intenta acceder a usuarios (debería fallar)
    Test-Endpoint -Url "$API_BASE/users" -Headers $coordHeaders -Description "Coordinador intenta acceder a usuarios (debería fallar)"
    
    # 14. Coordinador accede a eventos (debería funcionar)
    Test-Endpoint -Url "$API_BASE/events" -Headers $coordHeaders -Description "Coordinador accede a eventos"
}

# 15. Login como voluntario
$volLoginBody = @{
    usernameOrEmail = "vol1"
    password = "admin123"
} | ConvertTo-Json

$volLoginResponse = Test-Endpoint -Url "$API_BASE/auth/login" -Method "POST" -Body $volLoginBody -Description "Login como voluntario"

if ($volLoginResponse -and $volLoginResponse.token) {
    $volHeaders = @{ "Authorization" = "Bearer $($volLoginResponse.token)" }
    
    # 16. Voluntario ve eventos (solo lectura)
    Test-Endpoint -Url "$API_BASE/events" -Headers $volHeaders -Description "Voluntario ve eventos"
    
    # 17. Voluntario intenta crear evento (debería fallar)
    Test-Endpoint -Url "$API_BASE/events" -Method "POST" -Headers $volHeaders -Body $eventBody -Description "Voluntario intenta crear evento (debería fallar)"
}

Write-Host "`n🧹 FASE 7: Limpieza (opcional)" -ForegroundColor Cyan

# Limpiar datos de prueba si se crearon
if ($eventResponse -and $eventResponse.id) {
    Test-Endpoint -Url "$API_BASE/events/$($eventResponse.id)" -Method "DELETE" -Headers $headers -Description "Eliminar evento de prueba"
}

if ($donationResponse -and $donationResponse.donation_id) {
    # Nota: Implementar endpoint de eliminación de donaciones si es necesario
    Write-Host "ℹ️  Donación de prueba creada con ID: $($donationResponse.donation_id)" -ForegroundColor Blue
}

Write-Host "`n🎯 RESUMEN DE PRUEBAS COMPLETADO" -ForegroundColor Green
Write-Host "✅ Sistema probado con múltiples roles y funcionalidades" -ForegroundColor Green
Write-Host "🌐 Frontend disponible en: http://localhost:3000" -ForegroundColor Blue
Write-Host "🔗 API Gateway disponible en: http://localhost:3001" -ForegroundColor Blue

Write-Host "`n📝 CREDENCIALES DE PRUEBA:" -ForegroundColor Yellow
Write-Host "Admin: admin / admin123" -ForegroundColor White
Write-Host "Coordinador: coord1 / admin123" -ForegroundColor White
Write-Host "Voluntario: vol1 / admin123" -ForegroundColor White