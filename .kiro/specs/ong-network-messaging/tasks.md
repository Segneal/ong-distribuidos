# Plan de Implementación - Sistema de Mensajería para Red de ONGs

- [x] 1. Configurar infraestructura base para mensajería

  - Crear estructura del nuevo messaging-service con configuración básica de Kafka+

  - Implementar clases base para productores y consumidores de mensajes
  - Configurar conexión a Kafka con manejo de errores y reconexión automática
  - _Requerimientos: 8.1, 8.2, 8.3, 8.4_

- [x] 2. Implementar modelos de datos para mensajería

  - Crear modelos Python para todos los tipos de mensajes (DonationRequest, DonationTransfer, etc.)
  - Implementar validadores JSON Schema para cada tipo de mensaje
  - Crear funciones de serialización/deserialización para mensajes Kafka
  - _Requerimientos: 1.1, 2.2, 3.2, 5.2, 7.2_

- [x] 3. Extender base de datos con tablas para red de ONGs




  - Ejecutar scripts SQL para crear nuevas tablas (ofertas_externas, adhesiones_eventos_externos, etc.)
  - Implementar repositorios para gestionar datos de red de ONGs
  - Crear índices y optimizaciones para consultas de red
  - _Requerimientos: 9.1, 9.2_

- [x] 4. Implementar funcionalidad de solicitudes de donaciones





- [x] 4.1 Crear productor para solicitudes de donaciones


  - Implementar método para publicar solicitudes en topic "/solicitud-donaciones"
  - Integrar con inventory-service para validar donaciones solicitadas
  - Crear endpoint en API Gateway para crear solicitudes
  - _Requerimientos: 1.1, 1.2_

- [x] 4.2 Crear consumidor para solicitudes externas


  - Implementar consumidor para procesar solicitudes de otras organizaciones
  - Almacenar solicitudes externas en base de datos local
  - Filtrar solicitudes propias y validar formato de mensajes
  - _Requerimientos: 1.3, 1.4_

- [x] 4.3 Implementar gestión de bajas de solicitudes


  - Crear productor para publicar bajas en topic "/baja-solicitud-donaciones"
  - Implementar consumidor para procesar bajas de solicitudes externas
  - Actualizar estado de solicitudes en base de datos local
  - _Requerimientos: 4.1, 4.2, 4.3, 4.4_

- [ ] 5. Implementar funcionalidad de transferencias de donaciones
- [ ] 5.1 Crear sistema de transferencias salientes
  - Implementar productor para topic "/transferencia-donaciones/{org-id}"
  - Validar disponibilidad de inventario antes de transferir
  - Descontar cantidades del inventario local al confirmar transferencia
  - _Requerimientos: 2.1, 2.2, 2.3, 2.5_

- [ ] 5.2 Crear sistema de transferencias entrantes
  - Implementar consumidor para recibir transferencias dirigidas a nuestra organización
  - Sumar cantidades recibidas al inventario local
  - Registrar historial de transferencias en base de datos
  - _Requerimientos: 2.4_

- [ ] 6. Implementar funcionalidad de ofertas de donaciones
- [ ] 6.1 Crear sistema de publicación de ofertas
  - Implementar productor para topic "/oferta-donaciones"
  - Crear endpoint para que administradores publiquen ofertas
  - Validar disponibilidad de donaciones antes de ofrecer
  - _Requerimientos: 3.1, 3.2_

- [ ] 6.2 Crear sistema de consulta de ofertas externas
  - Implementar consumidor para procesar ofertas de otras organizaciones
  - Almacenar ofertas externas en base de datos local
  - Crear endpoint para consultar ofertas disponibles
  - _Requerimientos: 3.3, 3.4_

- [ ] 7. Implementar funcionalidad de eventos solidarios
- [ ] 7.1 Crear sistema de publicación de eventos
  - Implementar productor para topic "/eventossolidarios"
  - Integrar con events-service para publicar eventos automáticamente
  - Crear endpoint para publicación manual de eventos
  - _Requerimientos: 5.1, 5.2_

- [ ] 7.2 Crear sistema de gestión de eventos externos
  - Implementar consumidor para procesar eventos de otras organizaciones
  - Filtrar eventos propios y almacenar solo eventos externos
  - Verificar vigencia de eventos y filtrar eventos dados de baja
  - Crear pantalla de "Eventos Externos" en frontend
  - _Requerimientos: 5.3, 5.4, 5.5_

- [ ] 7.3 Implementar gestión de bajas de eventos
  - Crear productor para topic "/baja-evento-solidario"
  - Implementar consumidor para procesar bajas de eventos externos
  - Actualizar estado de eventos en base de datos local
  - _Requerimientos: 6.1, 6.2, 6.3, 6.4_

- [ ] 8. Implementar funcionalidad de adhesiones a eventos
- [ ] 8.1 Crear sistema de adhesiones salientes
  - Implementar productor para topic "/adhesion-evento/{org-id}"
  - Crear endpoint para que voluntarios se adhieran a eventos externos
  - Validar datos de voluntario antes de enviar adhesión
  - _Requerimientos: 7.1, 7.2_

- [ ] 8.2 Crear sistema de adhesiones entrantes
  - Implementar consumidor para recibir adhesiones a nuestros eventos
  - Notificar a administradores sobre nuevas adhesiones
  - Registrar adhesiones en base de datos local
  - _Requerimientos: 7.3, 7.4_

- [ ] 9. Implementar interfaces de usuario para red de ONGs
- [ ] 9.1 Crear componentes React para solicitudes de donaciones
  - Crear formulario para solicitar donaciones a la red
  - Crear lista de solicitudes externas disponibles
  - Implementar funcionalidad para dar de baja solicitudes propias
  - _Requerimientos: 1.1, 1.3, 4.1_

- [ ] 9.2 Crear componentes React para transferencias
  - Crear interfaz para seleccionar y transferir donaciones
  - Mostrar historial de transferencias enviadas y recibidas
  - Implementar validaciones de inventario en frontend
  - _Requerimientos: 2.1, 2.3, 2.4_

- [ ] 9.3 Crear componentes React para ofertas
  - Crear formulario para publicar ofertas de donaciones
  - Crear catálogo de ofertas externas disponibles
  - Implementar filtros y búsqueda de ofertas
  - _Requerimientos: 3.1, 3.3_

- [ ] 9.4 Crear componentes React para eventos de red
  - Extender pantalla de eventos para mostrar eventos externos
  - Crear funcionalidad de adhesión a eventos externos
  - Mostrar estado de adhesiones de voluntarios
  - _Requerimientos: 5.5, 7.1, 7.4_

- [ ] 10. Implementar sistema de monitoreo y logging
- [ ] 10.1 Crear sistema de métricas de Kafka
  - Implementar recolección de métricas de throughput y latencia
  - Crear dashboard básico de estado de conectividad
  - Configurar alertas para fallos de conexión
  - _Requerimientos: 8.3, 8.5_

- [ ] 10.2 Implementar logging detallado
  - Crear logs estructurados para todas las operaciones de mensajería
  - Implementar logs de auditoría para operaciones de red
  - Configurar rotación y retención de logs
  - _Requerimientos: 8.5_

- [ ] 11. Crear suite de tests para mensajería
- [ ] 11.1 Implementar tests unitarios
  - Crear tests para productores y consumidores de mensajes
  - Implementar mocks de Kafka para testing aislado
  - Crear tests de validación de formatos de mensajes
  - _Requerimientos: 8.1, 8.2, 8.4, 8.5_

- [ ] 11.2 Implementar tests de integración
  - Crear tests con Kafka embebido para flujos completos
  - Implementar tests de sincronización con base de datos
  - Crear tests de manejo de errores y recuperación
  - _Requerimientos: 9.1, 9.2, 9.3, 9.4_

- [ ] 12. Configurar deployment y documentación
- [ ] 12.1 Actualizar configuración de Docker
  - Agregar messaging-service al docker-compose.yml
  - Configurar variables de entorno para todos los servicios
  - Actualizar scripts de inicio para incluir nuevos servicios
  - _Requerimientos: 8.1, 8.2_

- [ ] 12.2 Crear documentación de API
  - Documentar nuevos endpoints en Swagger/OpenAPI
  - Crear guía de configuración para administradores
  - Documentar formatos de mensajes Kafka
  - _Requerimientos: Todos los requerimientos_