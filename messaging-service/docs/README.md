# Documentación del Sistema de Mensajería

Bienvenido a la documentación completa del Sistema de Mensajería para Red de ONGs.

## 📚 Documentos Disponibles

### 1. [API Documentation](api-documentation.yaml)
**Formato**: OpenAPI 3.0 (Swagger)  
**Descripción**: Documentación completa de todos los endpoints REST del sistema de mensajería.

**Contenido**:
- Especificación completa de endpoints
- Esquemas de request/response
- Códigos de error y respuestas
- Ejemplos de uso
- Autenticación y autorización

**Cómo usar**:
```bash
# Ver en Swagger UI
npx swagger-ui-serve api-documentation.yaml

# O importar en Postman/Insomnia
```

### 2. [Guía de Configuración para Administradores](admin-configuration-guide.md)
**Descripción**: Guía completa para configurar, desplegar y mantener el sistema de mensajería.

**Contenido**:
- Requisitos del sistema
- Configuración inicial paso a paso
- Variables de entorno
- Configuración de Kafka y PostgreSQL
- Deployment con Docker
- Monitoreo y troubleshooting
- Mantenimiento y backup

**Audiencia**: Administradores de sistemas, DevOps

### 3. [Formatos de Mensajes Kafka](kafka-message-formats.md)
**Descripción**: Especificación detallada de todos los formatos de mensajes utilizados en la red de ONGs.

**Contenido**:
- Estructura base de mensajes
- Esquemas JSON para cada tipo de mensaje
- Topics de Kafka y su propósito
- Ejemplos prácticos de flujos completos
- Validación de mensajes
- Versionado de esquemas

**Audiencia**: Desarrolladores, integradores de sistemas

## 🚀 Inicio Rápido

### Para Administradores
1. Leer [Guía de Configuración](admin-configuration-guide.md)
2. Configurar variables de entorno
3. Ejecutar `docker-compose up -d`
4. Verificar estado con `curl http://localhost:8000/health`

### Para Desarrolladores
1. Revisar [API Documentation](api-documentation.yaml)
2. Estudiar [Formatos de Mensajes](kafka-message-formats.md)
3. Ejecutar tests: `python -m pytest tests/ -v`
4. Implementar integración usando los endpoints documentados

### Para Usuarios Finales
1. El sistema se integra automáticamente con el frontend
2. Las funcionalidades están disponibles en la sección "Red de ONGs"
3. No requiere configuración adicional por parte del usuario

## 🔧 Herramientas de Desarrollo

### Validación de API
```bash
# Validar especificación OpenAPI
npx swagger-codegen-cli validate -i api-documentation.yaml

# Generar cliente
npx swagger-codegen-cli generate -i api-documentation.yaml -l python -o client/
```

### Testing de Mensajes
```bash
# Validar formato de mensaje
python -c "
import json
from messaging.models.validation import validate_message
message = json.load(open('example-message.json'))
print(validate_message(message))
"
```

## 📋 Checklist de Implementación

### Configuración Inicial
- [ ] Configurar ID único de organización
- [ ] Configurar conexión a Kafka
- [ ] Configurar base de datos PostgreSQL
- [ ] Ejecutar migraciones de base de datos
- [ ] Configurar variables de entorno
- [ ] Verificar conectividad con otros servicios

### Testing
- [ ] Ejecutar tests unitarios
- [ ] Ejecutar tests de integración
- [ ] Probar conectividad Kafka
- [ ] Probar endpoints de API
- [ ] Verificar validación de mensajes

### Deployment
- [ ] Configurar Docker Compose
- [ ] Configurar monitoreo
- [ ] Configurar logs
- [ ] Configurar backup de base de datos
- [ ] Documentar procedimientos de mantenimiento

### Integración
- [ ] Integrar con API Gateway
- [ ] Integrar con Frontend
- [ ] Configurar autenticación JWT
- [ ] Probar flujos end-to-end

## 🆘 Soporte

### Recursos de Ayuda
- **Issues**: Crear issue en el repositorio del proyecto
- **Email**: dev@empujecomunitario.org
- **Documentación**: Esta carpeta `docs/`

### Información de Debug
Al reportar problemas, incluir:
- Logs del servicio (`docker logs ong_messaging_service`)
- Configuración de variables de entorno (sin passwords)
- Versión del sistema
- Pasos para reproducir el problema

### Logs Útiles
```bash
# Logs del messaging service
docker logs ong_messaging_service -f

# Logs de Kafka
docker logs ong_kafka -f

# Logs de PostgreSQL
docker logs ong_postgres -f

# Estado de todos los servicios
docker-compose ps
```

## 📈 Roadmap

### Versión Actual (1.0.0)
- ✅ Solicitudes de donaciones
- ✅ Transferencias de donaciones
- ✅ Ofertas de donaciones
- ✅ Eventos solidarios
- ✅ Adhesiones a eventos
- ✅ API REST completa
- ✅ Validación de mensajes

### Próximas Versiones

#### v1.1.0 (Planificado)
- [ ] Métricas avanzadas de Kafka
- [ ] Dashboard de monitoreo
- [ ] Notificaciones push
- [ ] Filtros avanzados de búsqueda

#### v1.2.0 (Futuro)
- [ ] Integración con sistemas externos
- [ ] API GraphQL
- [ ] Webhooks para eventos
- [ ] Análisis de datos de red

#### v2.0.0 (Futuro)
- [ ] Soporte multi-región
- [ ] Encriptación end-to-end
- [ ] Blockchain para trazabilidad
- [ ] IA para matching automático

## 🔄 Actualizaciones de Documentación

Esta documentación se actualiza con cada release del sistema. 

**Última actualización**: Enero 2024  
**Versión de la documentación**: 1.0.0  
**Compatible con sistema**: v1.0.0+

### Historial de Cambios
- **v1.0.0** (Enero 2024): Documentación inicial completa
  - API Documentation con OpenAPI 3.0
  - Guía de configuración para administradores
  - Especificación de formatos de mensajes Kafka
  - README principal del sistema

---

Para contribuir a la documentación, seguir las mismas pautas que para el código:
1. Fork del repositorio
2. Crear rama: `git checkout -b docs/mejora-documentacion`
3. Realizar cambios en archivos de `docs/`
4. Commit: `git commit -am 'Mejorar documentación de X'`
5. Push y crear Pull Request