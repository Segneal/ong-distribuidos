# Test con autenticación

Write-Host "🔐 Probando con autenticación..." -ForegroundColor Yellow

# 1. Hacer login para obtener token
Write-Host "1. Haciendo login..." -ForegroundColor Cyan

$loginBody = @{
    email = "admin@empujecomunitario.org"
    password = "admin123"
} | ConvertTo-Json

$loginHeaders = @{
    'Content-Type' = 'application/json'
}

try {
    $loginResponse = Invoke-WebRequest -Uri "http://localhost:3000/api/auth/login" -Method POST -Body $loginBody -Headers $loginHeaders -UseBasicParsing
    $loginData = $loginResponse.Content | ConvertFrom-Json
    
    if ($loginData.success) {
        $token = $loginData.token
        Write-Host "✅ Login exitoso, token obtenido" -ForegroundColor Green
        
        # 2. Probar endpoint de eventos externos con token
        Write-Host "2. Probando eventos externos con token..." -ForegroundColor Cyan
        
        $eventsBody = @{
            activeOnly = $true
        } | ConvertTo-Json
        
        $eventsHeaders = @{
            'Content-Type' = 'application/json'
            'Authorization' = "Bearer $token"
        }
        
        $eventsResponse = Invoke-WebRequest -Uri "http://localhost:3000/api/messaging/external-events" -Method POST -Body $eventsBody -Headers $eventsHeaders -UseBasicParsing
        $eventsData = $eventsResponse.Content | ConvertFrom-Json
        
        Write-Host "✅ Status: $($eventsResponse.StatusCode)" -ForegroundColor Green
        Write-Host "Success: $($eventsData.success)" -ForegroundColor White
        
        if ($eventsData.success) {
            Write-Host "✅ Eventos encontrados: $($eventsData.events.Count)" -ForegroundColor Green
            
            # Mostrar algunos eventos
            if ($eventsData.events.Count -gt 0) {
                Write-Host "📅 Primeros eventos:" -ForegroundColor Cyan
                for ($i = 0; $i -lt [Math]::Min(3, $eventsData.events.Count); $i++) {
                    $event = $eventsData.events[$i]
                    Write-Host "  - $($event.name) ($($event.organization_id))" -ForegroundColor White
                }
            }
        } else {
            Write-Host "❌ Error: $($eventsData.error)" -ForegroundColor Red
        }
        
    } else {
        Write-Host "❌ Error en login: $($loginData.error)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode
        Write-Host "Status Code: $statusCode" -ForegroundColor Red
    }
}