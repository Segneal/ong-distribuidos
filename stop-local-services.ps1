# Script para detener todos los servicios locales
Write-Host "🛑 Deteniendo servicios locales..." -ForegroundColor Red

# Detener procesos por nombre
$serviceProcesses = @(
    "node",
    "python"
)

foreach ($processName in $serviceProcesses) {
    $processes = Get-Process -Name $processName -ErrorAction SilentlyContinue
    if ($processes) {
        Write-Host "🔄 Deteniendo procesos de $processName..." -ForegroundColor Yellow
        $processes | Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Host "✅ Procesos de $processName detenidos" -ForegroundColor Green
    }
}

# Limpiar archivo de PIDs si existe
if (Test-Path "service-pids.txt") {
    Remove-Item "service-pids.txt" -Force
}

Write-Host ""
Write-Host "✅ Todos los servicios locales han sido detenidos" -ForegroundColor Green
Write-Host "📊 La base de datos y MailHog siguen ejecutándose en Docker" -ForegroundColor Yellow
Write-Host "   Para detenerlos: docker-compose -f docker-compose-minimal.yml down" -ForegroundColor White