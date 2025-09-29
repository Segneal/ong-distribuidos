#!/usr/bin/env pwsh
# Script para probar las funcionalidades de solicitudes de donaciones (Task 4)

Write-Host "🧪 Iniciando pruebas de Task 4 - Solicitudes de Donaciones" -ForegroundColor Green

$baseUrl = "http://localhost:3000"
$headers = @{
    "Content-Type" = "application/json"
}

# Función para hacer login y obtener token
function Get-AuthToken {
    Write-Host "🔐 Obteniendo token de autenticación..." -ForegroundColor Yellow
    
    $loginData = @{
        email = "admin@empujecomunitario.org"
        password = "admin123"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" -Method POST -Body $loginData -Headers $headers
        return $response.token
    } catch {
        Write-Host "❌ Error en login: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Función para crear una solicitud de donación
function Test-CreateDonationRequest {
    param($token)
    
    Write-Host "📝 Probando creación de solicitud de donación..." -ForegroundColor Yellow
    
    $authHeaders = $headers.Clone()
    $authHeaders["Authorization"] = "Bearer $token"
    
    $requestData = @{
        donations = @(
            @{
                categoria = "ALIMENTOS"
                descripcion = "Conservas de atún"
                cantidad = "20 latas"
            },
            @{
                categoria = "ROPA"
                descripcion = "Abrigos de invierno"
                cantidad = "10 prendas"
            }
        )
        urgencia = "MEDIA"
        notas = "Solicitud de prueba para Task 4"
    } | ConvertTo-Json -Depth 3
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/donation-requests" -Method POST -Body $requestData -Headers $authHeaders
        Write-Host "✅ Solicitud creada exitosamente:" -ForegroundColor Green
        Write-Host "   ID: $($response.requestId)" -ForegroundColor Cyan
        Write-Host "   Estado: $($response.status)" -ForegroundColor Cyan
        return $response.requestId
    } catch {
        Write-Host "❌ Error creando solicitud: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            $errorBody = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorBody)
            $errorText = $reader.ReadToEnd()
            Write-Host "   Detalles: $errorText" -ForegroundColor Red
        }
        return $null
    }
}

# Función para obtener solicitudes propias
function Test-GetOwnRequests {
    param($token)
    
    Write-Host "📋 Probando obtención de solicitudes propias..." -ForegroundColor Yellow
    
    $authHeaders = $headers.Clone()
    $authHeaders["Authorization"] = "Bearer $token"
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/donation-requests" -Method GET -Headers $authHeaders
        Write-Host "✅ Solicitudes propias obtenidas:" -ForegroundColor Green
        Write-Host "   Total: $($response.requests.Count)" -ForegroundColor Cyan
        
        foreach ($request in $response.requests) {
            Write-Host "   - ID: $($request.id), Estado: $($request.estado), Fecha: $($request.fecha_creacion)" -ForegroundColor White
        }
        
        return $response.requests
    } catch {
        Write-Host "❌ Error obteniendo solicitudes: $($_.Exception.Message)" -ForegroundColor Red
        return @()
    }
}

# Función para obtener solicitudes externas
function Test-GetExternalRequests {
    param($token)
    
    Write-Host "🌐 Probando obtención de solicitudes externas..." -ForegroundColor Yellow
    
    $authHeaders = $headers.Clone()
    $authHeaders["Authorization"] = "Bearer $token"
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/donation-requests/external" -Method GET -Headers $authHeaders
        Write-Host "✅ Solicitudes externas obtenidas:" -ForegroundColor Green
        Write-Host "   Total: $($response.requests.Count)" -ForegroundColor Cyan
        
        foreach ($request in $response.requests) {
            Write-Host "   - Org: $($request.organizacion_solicitante), ID: $($request.solicitud_id), Estado: $($request.activa)" -ForegroundColor White
        }
        
        return $response.requests
    } catch {
        Write-Host "❌ Error obteniendo solicitudes externas: $($_.Exception.Message)" -ForegroundColor Red
        return @()
    }
}

# Función para cancelar una solicitud
function Test-CancelRequest {
    param($token, $requestId)
    
    if (-not $requestId) {
        Write-Host "⚠️ No hay ID de solicitud para cancelar" -ForegroundColor Yellow
        return
    }
    
    Write-Host "❌ Probando cancelación de solicitud ID: $requestId..." -ForegroundColor Yellow
    
    $authHeaders = $headers.Clone()
    $authHeaders["Authorization"] = "Bearer $token"
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/donation-requests/$requestId/cancel" -Method POST -Headers $authHeaders
        Write-Host "✅ Solicitud cancelada exitosamente:" -ForegroundColor Green
        Write-Host "   Estado: $($response.status)" -ForegroundColor Cyan
        Write-Host "   Mensaje: $($response.message)" -ForegroundColor Cyan
    } catch {
        Write-Host "❌ Error cancelando solicitud: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            $errorBody = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorBody)
            $errorText = $reader.ReadToEnd()
            Write-Host "   Detalles: $errorText" -ForegroundColor Red
        }
    }
}

# Función para verificar datos en base de datos
function Test-DatabaseData {
    Write-Host "🗄️ Verificando datos en base de datos..." -ForegroundColor Yellow
    
    try {
        # Verificar solicitudes externas
        $result = docker exec ong_postgres psql -U ong_user -d ong_management -c "SELECT COUNT(*) as total FROM solicitudes_externas;" -t
        Write-Host "✅ Solicitudes externas en BD: $($result.Trim())" -ForegroundColor Green
        
        # Verificar ofertas externas
        $result = docker exec ong_postgres psql -U ong_user -d ong_management -c "SELECT COUNT(*) as total FROM ofertas_externas;" -t
        Write-Host "✅ Ofertas externas en BD: $($result.Trim())" -ForegroundColor Green
        
        # Verificar configuración
        $result = docker exec ong_postgres psql -U ong_user -d ong_management -c "SELECT clave, valor FROM configuracion_organizacion;" -t
        Write-Host "✅ Configuración de organización:" -ForegroundColor Green
        Write-Host "$result" -ForegroundColor White
        
    } catch {
        Write-Host "❌ Error verificando base de datos: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Ejecutar todas las pruebas
Write-Host "=" * 60 -ForegroundColor Blue

# 1. Verificar datos en BD
Test-DatabaseData

Write-Host "=" * 60 -ForegroundColor Blue

# 2. Obtener token
$token = Get-AuthToken
if (-not $token) {
    Write-Host "❌ No se pudo obtener token. Terminando pruebas." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Token obtenido exitosamente" -ForegroundColor Green

# 3. Crear solicitud
$requestId = Test-CreateDonationRequest -token $token

Write-Host "=" * 60 -ForegroundColor Blue

# 4. Obtener solicitudes propias
$ownRequests = Test-GetOwnRequests -token $token

Write-Host "=" * 60 -ForegroundColor Blue

# 5. Obtener solicitudes externas
$externalRequests = Test-GetExternalRequests -token $token

Write-Host "=" * 60 -ForegroundColor Blue

# 6. Cancelar solicitud si se creó
if ($requestId) {
    Test-CancelRequest -token $token -requestId $requestId
    
    Write-Host "=" * 60 -ForegroundColor Blue
    
    # Verificar que se canceló
    Write-Host "🔍 Verificando cancelación..." -ForegroundColor Yellow
    Test-GetOwnRequests -token $token
}

Write-Host "=" * 60 -ForegroundColor Blue
Write-Host "🎉 Pruebas de Task 4 completadas!" -ForegroundColor Green