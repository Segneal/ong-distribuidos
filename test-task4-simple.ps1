# Script simple para probar Task 4 - Solicitudes de Donaciones

Write-Host "Iniciando pruebas de Task 4 - Solicitudes de Donaciones" -ForegroundColor Green

$baseUrl = "http://localhost:3000"

# 1. Verificar datos en base de datos
Write-Host "Verificando datos en base de datos..." -ForegroundColor Yellow

try {
    $result = docker exec ong_postgres psql -U ong_user -d ong_management -c "SELECT COUNT(*) as total FROM solicitudes_externas;" -t
    Write-Host "Solicitudes externas en BD: $($result.Trim())" -ForegroundColor Green
    
    $result = docker exec ong_postgres psql -U ong_user -d ong_management -c "SELECT COUNT(*) as total FROM ofertas_externas;" -t
    Write-Host "Ofertas externas en BD: $($result.Trim())" -ForegroundColor Green
    
    Write-Host "Configuracion de organizacion:" -ForegroundColor Green
    docker exec ong_postgres psql -U ong_user -d ong_management -c "SELECT clave, valor FROM configuracion_organizacion LIMIT 5;"
    
} catch {
    Write-Host "Error verificando base de datos: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "============================================" -ForegroundColor Blue

# 2. Obtener token de autenticacion
Write-Host "Obteniendo token de autenticacion..." -ForegroundColor Yellow

$loginData = @{
    usernameOrEmail = "admin@empujecomunitario.org"
    password = "admin123"
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" -Method POST -Body $loginData -Headers $headers
    $token = $response.token
    Write-Host "Token obtenido exitosamente" -ForegroundColor Green
} catch {
    Write-Host "Error en login: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "============================================" -ForegroundColor Blue

# 3. Crear solicitud de donacion
Write-Host "Creando solicitud de donacion..." -ForegroundColor Yellow

$authHeaders = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $token"
}

$requestData = @{
    donations = @(
        @{
            categoria = "ALIMENTOS"
            descripcion = "Conservas de atun"
            cantidad = "20 latas"
        }
    )
    urgencia = "MEDIA"
    notas = "Solicitud de prueba para Task 4"
} | ConvertTo-Json -Depth 3

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/donation-requests" -Method POST -Body $requestData -Headers $authHeaders
    Write-Host "Solicitud creada exitosamente:" -ForegroundColor Green
    Write-Host "ID: $($response.requestId)" -ForegroundColor Cyan
    $requestId = $response.requestId
} catch {
    Write-Host "Error creando solicitud: $($_.Exception.Message)" -ForegroundColor Red
    $requestId = $null
}

Write-Host "============================================" -ForegroundColor Blue

# 4. Obtener solicitudes propias
Write-Host "Obteniendo solicitudes propias..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/donation-requests" -Method GET -Headers $authHeaders
    Write-Host "Solicitudes propias obtenidas:" -ForegroundColor Green
    Write-Host "Total: $($response.requests.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "Error obteniendo solicitudes: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "============================================" -ForegroundColor Blue

# 5. Obtener solicitudes externas
Write-Host "Obteniendo solicitudes externas..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/donation-requests/external" -Method GET -Headers $authHeaders
    Write-Host "Solicitudes externas obtenidas:" -ForegroundColor Green
    Write-Host "Total: $($response.requests.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "Error obteniendo solicitudes externas: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "============================================" -ForegroundColor Blue

# 6. Cancelar solicitud si se creo
if ($requestId) {
    Write-Host "Cancelando solicitud ID: $requestId..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/donation-requests/$requestId/cancel" -Method POST -Headers $authHeaders
        Write-Host "Solicitud cancelada exitosamente" -ForegroundColor Green
    } catch {
        Write-Host "Error cancelando solicitud: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "============================================" -ForegroundColor Blue
Write-Host "Pruebas de Task 4 completadas!" -ForegroundColor Green