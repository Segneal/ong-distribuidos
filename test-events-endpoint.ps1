# Test simple del endpoint de eventos externos

Write-Host "🧪 Probando endpoint de eventos externos..." -ForegroundColor Yellow

# Crear body de la request
$body = @{
    activeOnly = $true
} | ConvertTo-Json

# Headers básicos (sin autenticación por ahora)
$headers = @{
    'Content-Type' = 'application/json'
}

try {
    Write-Host "Llamando a: http://localhost:3000/api/messaging/external-events" -ForegroundColor Cyan
    Write-Host "Body: $body" -ForegroundColor White
    
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/messaging/external-events" -Method POST -Body $body -Headers $headers -UseBasicParsing -TimeoutSec 10
    
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor White
    Write-Host $response.Content -ForegroundColor Gray
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode
        Write-Host "Status Code: $statusCode" -ForegroundColor Red
        
        try {
            $errorStream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorStream)
            $errorContent = $reader.ReadToEnd()
            Write-Host "Error Content: $errorContent" -ForegroundColor Red
        } catch {
            Write-Host "No se pudo leer el contenido del error" -ForegroundColor Red
        }
    }
}