@echo off
echo Iniciando Frontend...

REM Variables de entorno para React
set PORT=3001
set REACT_APP_API_URL=http://localhost:3000/api

echo Variables configuradas:
echo   PORT: %PORT% (Frontend React)
echo   API_URL: %REACT_APP_API_URL%
echo.

cd frontend
echo Iniciando React en puerto 3001...
npm start

pause