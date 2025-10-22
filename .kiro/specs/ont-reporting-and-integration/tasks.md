# Plan de Implementación

## Backend (Completado)
- [x] 1. Configurar estructura del proyecto y dependencias básicas
  - Crear directorio `reports-service` con estructura de carpetas
  - Configurar `requirements.txt` con FastAPI, Strawberry GraphQL, SQLAlchemy, openpyxl, zeep
  - Crear archivo de configuración básica y variables de entorno
  - _Requerimientos: 8.1, 8.4_

- [x] 2. Implementar modelos de datos y conexión a base de datos
  - [x] 2.1 Crear modelos SQLAlchemy para tablas existentes (usuarios, donaciones, eventos)
    - Implementar modelo User con campos básicos y rol
    - Implementar modelo Donation con categoría, descripción, cantidad, eliminado
    - Implementar modelo Event con nombre, descripción, fecha
    - _Requerimientos: 1.1, 4.1_

  - [x] 2.2 Crear nuevas tablas para filtros guardados y archivos Excel
    - Implementar migración SQL para tabla `filtros_guardados`
    - Implementar migración SQL para tabla `archivos_excel`
    - Crear modelos SQLAlchemy SavedFilter y ExcelFile
    - _Requerimientos: 2.3, 3.5, 5.3_

  - [x] 2.3 Configurar conexión a base de datos MySQL
    - Implementar configuración de SQLAlchemy con MySQL
    - Crear funciones de conexión y sesión de base de datos
    - _Requerimientos: 8.5_

- [x] 3. Implementar servicios de lógica de negocio
  - [x] 3.1 Crear servicio de reportes de donaciones
    - Implementar función para filtrar donaciones por categoría, fecha, eliminado
    - Implementar agrupación por categoría y estado de eliminado
    - Implementar cálculo de sumas totales por categoría
    - _Requerimientos: 1.2, 1.3, 1.4, 1.5_

  - [x] 3.2 Crear servicio de reportes de eventos
    - Implementar función para filtrar eventos por fecha y usuario
    - Implementar validación de permisos por rol de usuario
    - Implementar agrupación por mes con detalles de eventos
    - _Requerimientos: 4.2, 4.3, 4.4, 4.6, 4.7_

  - [x] 3.3 Crear servicio de gestión de filtros
    - Implementar funciones CRUD para filtros guardados
    - Implementar validación de nombres únicos por usuario
    - Implementar serialización/deserialización de configuraciones de filtros
    - _Requerimientos: 2.2, 2.4, 2.5, 2.6, 2.7, 5.2, 5.4, 5.5, 5.6, 5.7_

- [x] 4. Implementar APIs GraphQL
  - [x] 4.1 Configurar servidor Strawberry GraphQL
    - Configurar FastAPI con Strawberry GraphQL
    - Implementar middleware de autenticación JWT
    - Crear tipos GraphQL básicos (User, Donation, Event)
    - _Requerimientos: 1.1, 4.1_

  - [x] 4.2 Implementar resolvers para reportes de donaciones
    - Crear resolver `donationReport` con parámetros de filtrado
    - Implementar validación de permisos para Presidentes y Vocales
    - Implementar agrupación y sumarización de resultados
    - _Requerimientos: 1.2, 1.4, 1.5, 1.6_

  - [x] 4.3 Implementar resolvers para reportes de eventos
    - Crear resolver `eventParticipationReport` con filtros
    - Implementar validación de usuario obligatorio
    - Implementar restricciones de acceso por rol
    - _Requerimientos: 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_

  - [x] 4.4 Implementar mutations para gestión de filtros de donaciones
    - Crear mutations `saveDonationFilter`, `updateDonationFilter`, `deleteDonationFilter`
    - Implementar validación de nombres y configuraciones
    - _Requerimientos: 2.1, 2.2, 2.3, 2.6, 2.7, 2.8_

- [x] 5. Implementar APIs REST
  - [x] 5.1 Crear endpoints para exportación Excel
    - Implementar endpoint POST `/api/reports/donations/excel`
    - Crear servicio de generación de archivos Excel con openpyxl
    - Implementar hojas separadas por categoría con datos detallados
    - Implementar endpoint GET para descarga de archivos
    - _Requerimientos: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [x] 5.2 Crear endpoints para gestión de filtros de eventos
    - Implementar endpoints CRUD para filtros de eventos
    - Implementar validación de datos y permisos
    - _Requerimientos: 5.1, 5.2, 5.3, 5.6, 5.7, 5.8_

  - [x]* 5.3 Configurar documentación Swagger
    - Configurar FastAPI para generar documentación automática
    - Añadir descripciones y ejemplos a endpoints REST
    - _Requerimientos: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 6. Implementar cliente SOAP
  - [x] 6.1 Configurar cliente SOAP con zeep
    - Configurar cliente zeep para el WSDL de la red de ONGs
    - Implementar funciones para consultar datos de presidentes
    - Implementar funciones para consultar datos de organizaciones
    - _Requerimientos: 6.3, 6.4, 6.5, 6.6_

  - [x] 6.2 Crear endpoint REST para consulta SOAP
    - Implementar endpoint POST `/api/network/consultation`
    - Implementar validación de permisos solo para Presidentes
    - Implementar manejo de errores SOAP
    - _Requerimientos: 6.1, 6.2, 6.7, 6.8_

## Integración y Frontend (Pendiente)

- [ ] 7. Extender API Gateway con nuevas rutas
  - Añadir proxy para `/api/graphql` hacia servicio de reportes
  - Añadir proxy para `/api/reports/*` hacia servicio de reportes  
  - Añadir proxy para `/api/filters/*` hacia servicio de reportes
  - Añadir proxy para `/api/network/*` hacia servicio de reportes
  - Configurar middleware de autenticación JWT para nuevas rutas
  - _Requerimientos: 8.1, 8.2, 8.3_

- [ ] 8. Implementar componentes frontend para reportes de donaciones
  - [ ] 8.1 Crear componente `DonationReports` con filtros
    - Implementar formulario de filtros (categoría, fechas, eliminado)
    - Integrar con GraphQL query `donationReport`
    - Mostrar resultados agrupados por categoría y estado
    - Implementar botón de exportación Excel
    - _Requerimientos: 1.1, 1.2, 1.3, 1.4, 1.5, 3.1_

  - [ ] 8.2 Crear componente `DonationFilters` para gestión de filtros guardados
    - Implementar lista de filtros guardados del usuario
    - Añadir funcionalidad para guardar filtro actual
    - Implementar edición y eliminación de filtros
    - Integrar con mutations GraphQL para filtros
    - _Requerimientos: 2.1, 2.4, 2.5, 2.6, 2.7, 2.8_

- [ ] 9. Implementar componentes frontend para reportes de eventos
  - [ ] 9.1 Crear componente `EventParticipationReports`
    - Implementar formulario de filtros (fechas, usuario, reparto donaciones)
    - Validar que usuario_id sea obligatorio
    - Implementar restricciones de acceso por rol
    - Mostrar resultados agrupados por mes
    - Integrar con GraphQL query `eventParticipationReport`
    - _Requerimientos: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [ ] 9.2 Crear componente `EventFilters` para gestión de filtros de eventos
    - Implementar gestión de filtros guardados para eventos
    - Integrar con endpoints REST para CRUD de filtros
    - _Requerimientos: 5.1, 5.4, 5.5, 5.6, 5.7, 5.8_

- [ ] 10. Implementar componente frontend para consulta SOAP
  - Crear componente `NetworkConsultation` solo para Presidentes
  - Implementar input para lista de IDs de organizaciones
  - Mostrar resultados de presidentes y organizaciones
  - Implementar manejo de errores SOAP en UI
  - Integrar con endpoint REST `/api/network/consultation`
  - _Requerimientos: 6.1, 6.2, 6.5, 6.6, 6.7, 6.8_

- [ ] 11. Configurar Apollo Client para GraphQL
  - Extender configuración existente de Apollo Client
  - Añadir queries para reportes de donaciones y eventos
  - Añadir mutations para gestión de filtros de donaciones
  - Configurar endpoint GraphQL `/api/graphql`
  - _Requerimientos: 1.1, 2.3, 4.1, 4.4_

- [ ] 12. Integrar componentes en aplicación React existente
  - Verificar que componentes estén correctamente importados en Reports.jsx
  - Asegurar que la navegación por tabs funcione correctamente
  - Validar permisos de acceso por rol en la UI
  - _Requerimientos: 1.1, 4.1, 6.1_

- [ ]* 13. Testing y validación
  - [ ]* 13.1 Crear pruebas unitarias para componentes React
    - Escribir pruebas para componentes de reportes
    - Probar integración con GraphQL y REST APIs
    - _Requerimientos: Todos_

  - [ ] 13.2 Crear pruebas de integración frontend-backend
    - Probar flujo completo de reportes de donaciones
    - Probar flujo completo de reportes de eventos
    - Probar consulta SOAP desde frontend
    - _Requerimientos: Todos_

- [ ] 14. Configuración final y deployment
  - [ ] 14.1 Aplicar migraciones de base de datos
    - Ejecutar migración `001_create_filtros_guardados.sql`
    - Ejecutar migración `002_create_archivos_excel.sql`
    - Verificar que las tablas se crearon correctamente
    - _Requerimientos: 2.3, 3.5, 5.3_

  - [ ] 14.2 Configurar variables de entorno
    - Configurar variables de entorno para reports-service
    - Documentar proceso de instalación y ejecución
    - Probar funcionamiento completo del sistema
    - _Requerimientos: 8.1, 8.4, 8.5_

  - [ ]* 14.3 Preparar containerización (opcional)
    - Crear Dockerfile para servicio de reportes
    - Integrar con docker-compose existente si es necesario
    - _Requerimientos: 8.2_