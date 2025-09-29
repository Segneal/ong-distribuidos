# Script para probar el messaging service

Write-Host "🔍 Probando Messaging Service..." -ForegroundColor Yellow
Write-Host ""

# 1. Verificar que el contenedor esté ejecutándose
Write-Host "1. Estado del contenedor:" -ForegroundColor Cyan
docker-compose ps messaging-service

Write-Host ""
Write-Host "2. Verificar puertos expuestos:" -ForegroundColor Cyan
docker port ong_messaging_service

Write-Host ""
Write-Host "3. Intentar conectar al puerto 8000:" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3
    Write-Host "✅ Puerto 8000 responde: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Puerto 8000 no responde: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "4. Intentar conectar al puerto 50054:" -ForegroundColor Cyan
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.Connect("localhost", 50054)
    $tcpClient.Close()
    Write-Host "✅ Puerto 50054 está abierto" -ForegroundColor Green
} catch {
    Write-Host "❌ Puerto 50054 no responde: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "5. Logs recientes del messaging service:" -ForegroundColor Cyan
docker-compose logs --tail=10 messaging-service

Write-Host ""
Write-Host "6. Verificar variables de entorno:" -ForegroundColor Cyan
docker exec ong_messaging_service env | Select-String -Pattern "PORT|HTTP"

Write-Host ""
Write-Host "7. Probar endpoint directo desde el contenedor:" -ForegroundColor Cyan
try {
    $result = docker exec ong_messaging_service python -c "
import requests
try:
    r = requests.get('http://localhost:8000/health', timeout=2)
    print(f'Status: {r.status_code}')
    print(f'Response: {r.text[:100]}')
except Exception as e:
    print(f'Error: {e}')
"
    Write-Host "Resultado: $result" -ForegroundColor White
} catch {
    Write-Host "❌ Error ejecutando prueba interna: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "8. Verificar si el proceso Python está ejecutándose:" -ForegroundColor Cyan
try {
    $processes = docker exec ong_messaging_service python -c "
import os
import signal
import psutil
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    if 'python' in proc.info['name'].lower():
        print(f'PID: {proc.info[\"pid\"]}, CMD: {\" \".join(proc.info[\"cmdline\"])}')
"
    Write-Host "Procesos Python: $processes" -ForegroundColor White
} catch {
    Write-Host "❌ No se pudo verificar procesos: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 DIAGNÓSTICO COMPLETO" -ForegroundColor Green