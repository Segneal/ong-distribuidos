#!/bin/bash

# User Service
cat > user-service/docker-entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "Esperando que PostgreSQL esté listo..."

# Esperar a que PostgreSQL esté disponible
until nc -z ${DB_HOST:-postgres} ${DB_PORT:-5432}; do
  echo "PostgreSQL no está listo - esperando..."
  sleep 2
done

echo "PostgreSQL está listo!"

# Probar la conexión a la base de datos
echo "Probando conexión a la base de datos..."
python -c "
import sys
sys.path.append('/app/src')
from database_fixed import test_connection
if test_connection():
    print('Conexión a la base de datos exitosa')
else:
    print('Error de conexión a la base de datos')
    sys.exit(1)
"

echo "Iniciando User Service..."
exec python src/server.py
EOF

# Inventory Service
cat > inventory-service/docker-entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "Esperando que PostgreSQL esté listo..."

# Esperar a que PostgreSQL esté disponible
until nc -z ${DB_HOST:-postgres} ${DB_PORT:-5432}; do
  echo "PostgreSQL no está listo - esperando..."
  sleep 2
done

echo "PostgreSQL está listo!"

# Probar la conexión a la base de datos
echo "Probando conexión a la base de datos..."
python -c "
import sys
sys.path.append('/app/shared')
from models.database import test_connection
if test_connection():
    print('Conexión a la base de datos exitosa')
else:
    print('Error de conexión a la base de datos')
    sys.exit(1)
"

echo "Iniciando Inventory Service..."
exec python src/server.py
EOF

# Events Service
cat > events-service/docker-entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "Esperando que PostgreSQL esté listo..."

# Esperar a que PostgreSQL esté disponible
until nc -z ${DB_HOST:-postgres} ${DB_PORT:-5432}; do
  echo "PostgreSQL no está listo - esperando..."
  sleep 2
done

echo "PostgreSQL está listo!"

# Probar la conexión a la base de datos
echo "Probando conexión a la base de datos..."
python -c "
import sys
sys.path.append('/app/src')
from database_fixed import get_db_connection
db = get_db_connection()
conn = db.connect()
if conn:
    print('Conexión a la base de datos exitosa')
    db.close()
else:
    print('Error de conexión a la base de datos')
    sys.exit(1)
"

echo "Iniciando Events Service..."
exec python src/server.py
EOF

chmod +x user-service/docker-entrypoint.sh
chmod +x inventory-service/docker-entrypoint.sh
chmod +x events-service/docker-entrypoint.sh

echo "Archivos docker-entrypoint.sh creados con formato Unix"