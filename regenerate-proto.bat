@echo off
echo 🔄 Regenerando archivos protobuf...
echo.

echo 🔧 Regenerando User Service...
cd user-service
pip install --upgrade protobuf==4.25.1
pip install -r requirements.txt
python -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/users.proto
if errorlevel 1 (
    echo ❌ Error regenerando User Service
) else (
    echo ✅ User Service completado
)
cd ..

echo.
echo 🔧 Regenerando Inventory Service...
cd inventory-service
pip install --upgrade protobuf==4.25.1
pip install -r requirements.txt
python -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/inventory.proto
if errorlevel 1 (
    echo ❌ Error regenerando Inventory Service
) else (
    echo ✅ Inventory Service completado
)
cd ..

echo.
echo 🔧 Regenerando Events Service...
cd events-service
pip install --upgrade protobuf==4.25.1
pip install -r requirements.txt
python -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/events.proto
if errorlevel 1 (
    echo ❌ Error regenerando Events Service
) else (
    echo ✅ Events Service completado
)
cd ..

echo.
echo 🎉 Regeneración de protobuf completada!
echo Ahora puedes ejecutar los servicios con:
echo   .\start-services.bat
echo.
pause