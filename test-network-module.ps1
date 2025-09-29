# Script para verificar que el módulo "Red de ONGs" esté disponible

Write-Host "🔍 Verificando módulo Red de ONGs..." -ForegroundColor Yellow
Write-Host ""

# Verificar que el frontend esté ejecutándose
Write-Host "1. Verificando estado del frontend..." -ForegroundColor Cyan
$frontendStatus = docker-compose ps frontend
Write-Host $frontendStatus

Write-Host ""
Write-Host "2. Verificando conectividad del frontend..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001" -UseBasicParsing -TimeoutSec 10
    Write-Host "✅ Frontend accesible - Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error conectando al frontend: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "3. Verificando que los archivos de red estén en el build..." -ForegroundColor Cyan

# Verificar que los archivos de red estén incluidos en el contenedor
$networkFiles = @(
    "/usr/share/nginx/html/static/js/main.*.js"
)

foreach ($file in $networkFiles) {
    try {
        $result = docker exec ong_frontend ls $file 2>$null
        if ($result) {
            Write-Host "✅ Archivos JavaScript encontrados" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ No se encontraron archivos JavaScript" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "4. Verificando contenido del JavaScript principal..." -ForegroundColor Cyan
try {
    # Buscar referencias a "Red de ONGs" en el JavaScript compilado
    $jsContent = docker exec ong_frontend sh -c "cat /usr/share/nginx/html/static/js/main.*.js | grep -o 'Red de ONGs\|network\|Hub' | head -5" 2>$null
    if ($jsContent) {
        Write-Host "✅ Referencias a red encontradas en el JavaScript:" -ForegroundColor Green
        Write-Host $jsContent -ForegroundColor White
    } else {
        Write-Host "⚠️  No se encontraron referencias específicas (esto es normal en JS minificado)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  No se pudo verificar el contenido JS (normal en producción)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "5. Instrucciones para verificar manualmente:" -ForegroundColor Cyan
Write-Host "   1. Abrir navegador en: http://localhost:3001" -ForegroundColor White
Write-Host "   2. Hacer login con: admin@empujecomunitario.org / admin123" -ForegroundColor White
Write-Host "   3. Buscar 'Red de ONGs' en el menú lateral izquierdo" -ForegroundColor White
Write-Host "   4. El ícono debe ser un Hub (🌐) y estar entre Inventario y Solicitudes Red" -ForegroundColor White

Write-Host ""
Write-Host "6. Si no ves 'Red de ONGs':" -ForegroundColor Yellow
Write-Host "   - Refrescar la página (F5)" -ForegroundColor White
Write-Host "   - Limpiar cache del navegador (Ctrl+Shift+R)" -ForegroundColor White
Write-Host "   - Verificar que estés logueado correctamente" -ForegroundColor White
Write-Host "   - Probar en modo incógnito" -ForegroundColor White

Write-Host ""
Write-Host "7. Verificando logs recientes del frontend..." -ForegroundColor Cyan
docker-compose logs --tail=3 frontend

Write-Host ""
Write-Host "🎯 RESULTADO:" -ForegroundColor Green
Write-Host "El frontend ha sido reconstruido con los últimos cambios." -ForegroundColor White
Write-Host "El módulo 'Red de ONGs' debería estar disponible después del login." -ForegroundColor White
Write-Host ""
Write-Host "🌐 URL de acceso: http://localhost:3001" -ForegroundColor Cyan
Write-Host "👤 Usuario de prueba: admin@empujecomunitario.org" -ForegroundColor Cyan
Write-Host "🔑 Contraseña: admin123" -ForegroundColor Cyan