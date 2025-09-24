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
sys.path.append('/app/src')
from database_fixed import get_db_connection
db = get_db_connection()
conn = db.connect()
if conn:
    print('✅ Conexión a la base de datos exitosa')
    db.close()
else:
    print('❌ Error de conexión a la base de datos')
    sys.exit(1)
"

echo "🚀 Iniciando Events Service..."
exec python src/server.py