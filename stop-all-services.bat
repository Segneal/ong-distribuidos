@echo off
echo Deteniendo todos los servicios locales...

echo Cerrando procesos de Node.js...
taskkill /f /im node.exe >nul 2>&1

echo Cerrando procesos de Python...
taskkill /f /im python.exe >nul 2>&1

echo Cerrando ventanas de servicios...
taskkill /f /fi "WindowTitle eq User Service*" >nul 2>&1
taskkill /f /fi "WindowTitle eq Inventory Service*" >nul 2>&1
taskkill /f /fi "WindowTitle eq Events Service*" >nul 2>&1
taskkill /f /fi "WindowTitle eq API Gateway*" >nul 2>&1
taskkill /f /fi "WindowTitle eq Frontend*" >nul 2>&1

echo.
echo Todos los servicios locales han sido detenidos
echo La base de datos y MailHog siguen ejecutandose en Docker
echo Para detenerlos: docker-compose -f docker-compose-minimal.yml down
echo.
pause