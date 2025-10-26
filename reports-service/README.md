# Reports Service

Sistema de Reportes e Integración para la plataforma de gestión de ONGs.

## Características

- **GraphQL API**: Para reportes de donaciones y eventos
- **REST API**: Para exportación Excel y gestión de filtros
- **SOAP Client**: Para integración con red externa de ONGs
- **Exportación Excel**: Generación de reportes detallados
- **Filtros Personalizados**: Gestión de filtros guardados por usuario

## Estructura del Proyecto

```
reports-service/
├── src/
│   ├── gql/              # GraphQL schemas y resolvers
│   ├── rest/             # Endpoints REST
│   ├── soap/             # Cliente SOAP
│   ├── services/         # Lógica de negocio
│   ├── models/           # Modelos de datos
│   ├── utils/            # Utilidades
│   ├── config.py         # Configuración
│   └── main.py           # Aplicación principal
├── storage/              # Almacenamiento de archivos Excel
├── tests/                # Pruebas unitarias e integración
├── migrations/           # Migraciones de base de datos
├── requirements.txt      # Dependencias Python
├── Dockerfile           # Configuración Docker
├── .env                 # Variables de entorno
└── README.md           # Documentación
```

## Requisitos del Sistema

- **Python**: 3.9 o superior
- **MySQL**: 5.7 o superior
- **Memoria RAM**: Mínimo 512MB, recomendado 1GB
- **Espacio en disco**: Mínimo 100MB para archivos Excel temporales

## Instalación y Configuración

### 1. Preparación del Entorno

```bash
# Clonar el repositorio (si aplica)
cd reports-service

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configuración de Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con los valores correctos para tu entorno
```

**Variables de entorno importantes:**

- `DATABASE_URL`: URL de conexión a MySQL (ej: `mysql+pymysql://user:password@localhost:3306/ong_management`)
- `JWT_SECRET_KEY`: Clave secreta para JWT (generar una clave segura para producción)
- `SOAP_SERVICE_URL`: URL del servicio SOAP externo
- `EXCEL_STORAGE_PATH`: Ruta para archivos Excel temporales

### 4. Preparar Base de Datos

```bash
# Asegurarse de que MySQL esté ejecutándose
# Crear la base de datos si no existe
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS ong_management;"

# Ejecutar migraciones (si existen)
python -c "from src.models import init_database; init_database()"
```

### 5. Crear Directorios Necesarios

```bash
# Crear directorio para archivos Excel
mkdir -p storage/excel

# Asegurar permisos correctos
chmod 755 storage/excel
```

## Ejecución

### Desarrollo Local

```bash
# Método 1: Ejecutar directamente
python -m src.main

# Método 2: Con uvicorn (más control)
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Método 3: Con configuración de desarrollo
DEBUG=true python -m src.main
```

### Producción

```bash
# Con múltiples workers (recomendado para producción)
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

# Con gunicorn (alternativa)
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Con Docker

```bash
# Construir imagen
docker build -t reports-service .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file .env reports-service

# Con docker-compose (si está configurado)
docker-compose up reports-service
```

## Verificación del Sistema

### 1. Health Check

```bash
# Verificar que el servicio esté ejecutándose
curl http://localhost:8000/health

# Respuesta esperada:
# {
#   "status": "healthy",
#   "service": "reports-service",
#   "database": {
#     "database_connected": true,
#     "connection_pool_size": 10
#   }
# }
```

### 2. Verificar GraphQL

```bash
# Acceder a GraphQL Playground
# Abrir en navegador: http://localhost:8000/api/graphql
```

### 3. Verificar REST API

```bash
# Acceder a documentación Swagger
# Abrir en navegador: http://localhost:8000/docs
```

### 4. Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
python run_tests.py

# Ejecutar pruebas específicas
pytest tests/test_basic_validation.py -v

# Ejecutar validación del sistema
python validate_system.py
```

## Integración con el Sistema Completo

### 1. API Gateway

El servicio debe integrarse con el API Gateway existente. Asegúrate de que las siguientes rutas estén configuradas:

```javascript
// En api-gateway/src/routes/reports.js
app.use('/api/graphql', proxy('http://localhost:8000/api/graphql'));
app.use('/api/reports', proxy('http://localhost:8000/api/reports'));
app.use('/api/filters', proxy('http://localhost:8000/api/filters'));
app.use('/api/network', proxy('http://localhost:8000/api/network'));
```

### 2. Frontend

Los componentes React deben estar configurados para usar las nuevas rutas:

- `/reports/donations` - Reportes de donaciones
- `/reports/events` - Reportes de eventos
- `/network/consultation` - Consulta SOAP

### 3. Base de Datos

El servicio utiliza las siguientes tablas existentes:
- `usuarios`
- `donaciones`
- `eventos`

Y crea las siguientes tablas nuevas:
- `filtros_guardados`
- `archivos_excel`

## Endpoints Disponibles

### GraphQL (POST /api/graphql)
- `donationReport` - Reportes de donaciones con filtros
- `eventParticipationReport` - Reportes de participación en eventos
- `saveDonationFilter` - Guardar filtros de donaciones
- `updateDonationFilter` - Actualizar filtros de donaciones
- `deleteDonationFilter` - Eliminar filtros de donaciones

### REST API
- `POST /api/reports/donations/excel` - Exportar donaciones a Excel
- `GET /api/reports/downloads/{fileId}` - Descargar archivo Excel
- `GET /api/filters/events` - Obtener filtros de eventos guardados
- `POST /api/filters/events` - Crear filtro de eventos
- `PUT /api/filters/events/{id}` - Actualizar filtro de eventos
- `DELETE /api/filters/events/{id}` - Eliminar filtro de eventos
- `POST /api/network/consultation` - Consulta SOAP a red externa

### Documentación
- `GET /docs` - Documentación Swagger UI
- `GET /redoc` - Documentación ReDoc
- `GET /health` - Health check del servicio

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a base de datos**
   ```bash
   # Verificar que MySQL esté ejecutándose
   mysql -u root -p -e "SELECT 1;"
   
   # Verificar credenciales en .env
   # Verificar que la base de datos exista
   ```

2. **Error de permisos en storage/excel**
   ```bash
   # Crear directorio y asignar permisos
   mkdir -p storage/excel
   chmod 755 storage/excel
   ```

3. **Error de importación de módulos**
   ```bash
   # Verificar que estés en el directorio correcto
   # Verificar que el entorno virtual esté activado
   # Reinstalar dependencias
   pip install -r requirements.txt
   ```

4. **Error de SOAP timeout**
   ```bash
   # Verificar conectividad al servicio SOAP
   curl -I https://soap-applatest.onrender.com/?wsdl
   
   # Ajustar SOAP_TIMEOUT en .env si es necesario
   ```

### Logs y Debugging

```bash
# Ejecutar con logs detallados
LOG_LEVEL=DEBUG python -m src.main

# Ver logs en tiempo real
tail -f logs/reports-service.log
```

## Configuración de Producción

### Variables de Entorno para Producción

```bash
# Configuración de seguridad
JWT_SECRET_KEY=<generar-clave-segura-de-32-caracteres>
DEBUG=false

# Configuración de base de datos
DATABASE_URL=mysql+pymysql://user:secure_password@db_host:3306/ong_management
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Configuración de rendimiento
WORKERS=4
MAX_CONCURRENT_REQUESTS=200
REQUEST_TIMEOUT=120

# Configuración de logs
LOG_LEVEL=INFO
```

### Consideraciones de Seguridad

1. **Cambiar JWT_SECRET_KEY** por una clave segura
2. **Configurar CORS** solo para dominios autorizados
3. **Usar HTTPS** en producción
4. **Configurar firewall** para limitar acceso al puerto 8000
5. **Monitorear logs** para detectar actividad sospechosa

## Monitoreo y Mantenimiento

### Métricas Importantes

- Tiempo de respuesta de endpoints
- Uso de memoria y CPU
- Conexiones activas a base de datos
- Tamaño de archivos Excel generados
- Errores de SOAP timeout

### Mantenimiento Regular

1. **Limpiar archivos Excel temporales** (automático cada 24 horas)
2. **Monitorear logs de errores**
3. **Verificar conectividad SOAP**
4. **Actualizar dependencias** regularmente
5. **Backup de filtros guardados**

## Soporte

Para problemas o preguntas:

1. Revisar logs del servicio
2. Ejecutar `python validate_system.py`
3. Verificar configuración de variables de entorno
4. Consultar documentación de APIs en `/docs`