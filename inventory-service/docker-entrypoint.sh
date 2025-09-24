#!/bin/bash
set -e

echo "🔍 Esperando que PostgreSQL esté listo..."

# Esperar a que PostgreSQL esté disponible
until nc -z ${DB_HOST:-postgres} ${DB_PORT:-5432}; do
  echo "⏳ PostgreSQL no está listo - esperando..."
  sleep 2
done

echo "✅ PostgreSQL está listo!"

# Probar la conexión a la base de datos
echo "🔍 Probando conexión a la base de datos..."
python -c "
import sys
sys.path.append('/app/shared')
from models.database import test_connection
import sys
if test_connection():
    print('✅ Conexión a la base de datos exitosa')
else:
    print('❌ Error de conexión a la base de datos')
    sys.exit(1)
"

echo "🚀 Iniciando Inventory Service..."
exec python src/server.py