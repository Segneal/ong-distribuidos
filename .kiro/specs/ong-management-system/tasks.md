# Plan de Implementación - Sistema de Gestión ONG "Empuje Comunitario"

- [x] 1. Configurar estructura del proyecto y herramientas base





  - Crear estructura de directorios para microservicios, API Gateway y frontend
  - Configurar Docker Compose con PostgreSQL, Kafka y Zookeeper
  - Crear archivos de configuración base (.env, package.json, requirements.txt)
  - _Requisitos: 13.1, 13.2, 13.7_

- [x] 2. Implementar base de datos y modelos




- [x] 2.1 Crear esquemas de base de datos PostgreSQL


  - Escribir scripts SQL para tablas de usuarios, donaciones, eventos
  - Crear tablas para red de ONGs (solicitudes_externas, eventos_externos)
  - Implementar constraints y relaciones entre tablas
  - _Requisitos: 2.2, 4.1, 5.1, 6.1_

- [x] 2.2 Crear modelos de datos Python


  - Implementar clases modelo para User, Donation, Event
  - Crear funciones de conexión a PostgreSQL
  - Implementar funciones básicas de CRUD para cada modelo
  - _Requisitos: 2.2, 4.1, 5.1_

- [x] 3. Implementar microservicio de usuarios con gRPC





- [x] 3.1 Definir protocolo gRPC para usuarios


  - Crear archivo users.proto con servicios y mensajes
  - Generar código Python desde protobuf
  - Definir enums para roles (PRESIDENTE, VOCAL, COORDINADOR, VOLUNTARIO)
  - _Requisitos: 1.1, 2.1, 13.1_

- [x] 3.2 Implementar servidor gRPC de usuarios


  - Crear UserService con métodos CreateUser, GetUser, UpdateUser, DeleteUser, ListUsers
  - Implementar AuthenticateUser para login
  - Integrar generación de contraseñas aleatorias
  - Configurar servidor gRPC en puerto 50051
  - _Requisitos: 2.2, 2.3, 2.4, 2.6, 2.7, 3.1, 3.2_

- [x] 3.3 Implementar envío de emails con Nodemailer


  - Configurar Nodemailer con SMTP
  - Crear función para enviar contraseñas por email
  - Implementar archivo de log para testing (/testing/usuarios/passlogs.txt)
  - _Requisitos: 2.3, 2.5, 14.4_

- [x] 3.4 Implementar encriptación de contraseñas


  - Integrar bcrypt para hash de contraseñas
  - Crear funciones de verificación de contraseñas
  - Implementar validación de credenciales
  - _Requisitos: 2.4, 3.3, 3.4_

- [x] 4. Implementar microservicio de inventario con gRPC




- [x] 4.1 Definir protocolo gRPC para inventario


  - Crear archivo inventory.proto con servicios y mensajes
  - Generar código Python desde protobuf
  - Definir enums para categorías (ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES)
  - _Requisitos: 4.1, 13.1_

- [x] 4.2 Implementar servidor gRPC de inventario


  - Crear InventoryService con métodos CRUD para donaciones
  - Implementar validación de cantidades no negativas
  - Agregar campos de auditoría automáticos
  - Configurar servidor gRPC en puerto 50052
  - _Requisitos: 4.2, 4.3, 4.4, 4.5_

- [x] 4.3 Implementar baja lógica de donaciones


  - Crear método DeleteDonation con confirmación
  - Implementar flag de eliminado en lugar de borrado físico
  - Registrar auditoría de eliminación
  - _Requisitos: 4.6, 4.7_

- [x] 5. Implementar microservicio de eventos con gRPC





- [x] 5.1 Definir protocolo gRPC para eventos


  - Crear archivo events.proto con servicios y mensajes
  - Generar código Python desde protobuf
  - Definir estructuras para eventos y participantes
  - _Requisitos: 5.1, 13.1_



- [ ] 5.2 Implementar servidor gRPC de eventos
  - Crear EventsService con métodos CRUD para eventos
  - Implementar validación de fechas futuras para creación
  - Agregar gestión de participantes (asignar/quitar miembros)
  - Configurar servidor gRPC en puerto 50053


  - _Requisitos: 5.1, 5.2, 5.3, 5.7_

- [ ] 5.3 Implementar registro de donaciones repartidas
  - Crear funcionalidad para registrar donaciones en eventos pasados


  - Implementar descuento automático del inventario
  - Registrar usuario que hace la modificación
  - _Requisitos: 5.4, 5.5_

- [ ] 5.4 Implementar eliminación física de eventos futuros
  - Crear validación para eliminar solo eventos futuros
  - Implementar eliminación física de base de datos
  - Remover participantes automáticamente
  - _Requisitos: 5.6_

- [x] 6. Configurar API Gateway y Frontend base





- [x] 6.1 Configurar servidor Express básico


  - Crear servidor Express en puerto 3000
  - Configurar middleware básico (CORS, JSON parsing)
  - Implementar estructura de rutas modular
  - _Requisitos: 13.3_

- [x] 6.2 Configurar proyecto React base


  - Crear proyecto React con Create React App
  - Configurar React Router para navegación
  - Instalar Axios para comunicación HTTP
  - Configurar estructura de componentes
  - _Requisitos: 13.4_

- [x] 6.3 Implementar clientes gRPC en API Gateway



  - Crear conexiones gRPC a los tres microservicios
  - Implementar funciones de transformación REST ↔ gRPC
  - Configurar manejo básico de errores gRPC
  - _Requisitos: 13.1, 13.2_

- [x] 7. Implementar módulo de autenticación completo





- [x] 7.1 Implementar endpoints de autenticación


  - Crear POST /api/auth/login con validación de credenciales
  - Implementar generación de JWT tokens
  - Crear POST /api/auth/logout
  - _Requisitos: 3.1, 3.2, 3.5, 3.6_

- [x] 7.2 Implementar componentes de autenticación


  - Crear LoginForm con validación básica
  - Implementar Context para manejo de autenticación
  - Crear ProtectedRoute para rutas privadas
  - Implementar logout y manejo de tokens
  - _Requisitos: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_


- [x] 7.3 Implementar middleware de autorización

  - Crear middleware para verificar JWT tokens
  - Implementar verificación de roles por endpoint
  - Agregar manejo de errores de autorización
  - _Requisitos: 1.2, 1.3, 1.4, 1.5_

- [ ] 8. Implementar módulo de gestión de usuarios completo
- [ ] 8.1 Implementar endpoints de gestión de usuarios
  - Crear GET /api/users (solo PRESIDENTE)
  - Crear POST /api/users para alta de usuarios
  - Crear PUT /api/users/:id para modificación
  - Crear DELETE /api/users/:id para baja lógica
  - _Requisitos: 2.1, 2.2, 2.6, 2.7_

- [ ] 8.2 Implementar componentes de gestión de usuarios
  - Crear UserList para mostrar usuarios (solo PRESIDENTE)
  - Crear UserForm para alta y modificación de usuarios
  - Implementar confirmación para baja de usuarios
  - Agregar validación de formularios
  - _Requisitos: 2.1, 2.2, 2.6, 2.7_

- [ ] 9. Implementar módulo de inventario completo
- [ ] 9.1 Implementar endpoints de inventario
  - Crear GET /api/inventory (PRESIDENTE, VOCAL)
  - Crear POST /api/inventory para registrar donaciones
  - Crear PUT /api/inventory/:id para modificar donaciones
  - Crear DELETE /api/inventory/:id para baja lógica
  - _Requisitos: 4.1, 4.2, 4.5, 4.6_

- [ ] 9.2 Implementar componentes de inventario
  - Crear InventoryList con filtros por categoría
  - Crear DonationForm para registrar/modificar donaciones
  - Implementar validación de cantidades
  - Agregar confirmación para eliminación
  - _Requisitos: 4.1, 4.2, 4.3, 4.5, 4.6, 4.7_

- [ ] 10. Implementar módulo de eventos completo
- [ ] 10.1 Implementar endpoints de eventos
  - Crear GET /api/events con filtros por rol
  - Crear POST /api/events (PRESIDENTE, COORDINADOR)
  - Crear PUT /api/events/:id para modificar eventos
  - Crear DELETE /api/events/:id para eliminar eventos
  - Crear POST/DELETE /api/events/:id/participants para gestión de participantes
  - _Requisitos: 5.1, 5.2, 5.3, 5.6, 5.7_

- [ ] 10.2 Implementar componentes de eventos
  - Crear EventList con diferentes vistas por rol
  - Crear EventForm para crear/modificar eventos
  - Implementar ParticipantManager para gestión de miembros
  - Agregar funcionalidad para registrar donaciones repartidas
  - _Requisitos: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ] 11. Implementar integración con Kafka para red de ONGs
- [ ] 11.1 Configurar productores Kafka en microservicios
  - Configurar cliente Kafka en cada microservicio Python
  - Crear funciones para publicar mensajes en tópicos
  - Implementar serialización JSON para mensajes
  - _Requisitos: 6.1, 7.1, 8.1, 9.1, 10.1, 11.1, 12.1_

- [ ] 11.2 Implementar solicitudes de donaciones
  - Crear endpoint para solicitar donaciones a la red
  - Publicar mensajes en tópico "/solicitud-donaciones"
  - Crear pantalla frontend para solicitar donaciones
  - _Requisitos: 6.1, 6.2, 6.3_

- [ ] 11.3 Implementar transferencia de donaciones
  - Crear endpoint para transferir donaciones
  - Publicar en tópico "/transferencia-donaciones/{org-id}"
  - Crear pantalla frontend para transferir donaciones
  - Descontar cantidades del inventario propio
  - _Requisitos: 7.1, 7.2, 7.3, 7.4_

- [ ] 11.4 Implementar ofertas de donaciones
  - Crear endpoint para ofrecer donaciones
  - Publicar en tópico "/oferta-donaciones"
  - Crear pantalla frontend para mostrar ofertas externas
  - _Requisitos: 8.1, 8.2, 8.3, 8.4_

- [ ] 11.5 Configurar consumidores Kafka
  - Implementar consumidores para cada tópico relevante
  - Procesar solicitudes externas de donaciones
  - Actualizar inventario al recibir transferencias
  - _Requisitos: 6.4, 6.5, 7.5, 9.3, 9.4_

- [ ] 11.6 Implementar gestión de bajas de solicitudes
  - Crear endpoint para dar de baja solicitudes propias
  - Publicar en tópico "/baja-solicitud-donaciones"
  - Procesar bajas externas y actualizar sistema
  - _Requisitos: 9.1, 9.2, 9.3, 9.4_

- [ ] 11.7 Implementar eventos externos
  - Publicar eventos propios en tópico "/eventossolidarios"
  - Consumir eventos externos y filtrar eventos propios
  - Crear pantalla para mostrar eventos externos
  - _Requisitos: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 11.8 Implementar adhesión a eventos externos
  - Publicar bajas de eventos en tópico "/baja-evento-solidario"
  - Procesar bajas externas de eventos
  - Implementar adhesión a eventos externos con pantalla frontend
  - _Requisitos: 11.1, 11.2, 11.3, 11.4, 12.1, 12.2, 12.3, 12.4_

- [ ] 12. Implementar navegación y layout final
- [ ] 12.1 Implementar navegación y layout
  - Crear componente Layout con navegación
  - Implementar menú dinámico según rol de usuario
  - Agregar breadcrumbs y navegación intuitiva
  - Implementar diseño responsivo básico
  - _Requisitos: 1.2, 1.3, 1.4, 1.5_

- [ ] 13. Configurar documentación y testing
- [ ] 13.1 Crear documentación Swagger
  - Documentar todos los endpoints del API Gateway
  - Incluir ejemplos de request/response
  - Documentar códigos de error
  - _Requisitos: 14.1_

- [ ] 13.2 Preparar datos de prueba
  - Crear scripts SQL para insertar usuarios de prueba
  - Insertar donaciones y eventos de ejemplo
  - Configurar datos para testing de red de ONGs
  - _Requisitos: 14.3_

- [ ] 13.3 Crear colecciones Postman
  - Crear colección para endpoints de autenticación
  - Crear colección para gestión de usuarios
  - Crear colección para inventario y eventos
  - Crear colección para funcionalidades de red de ONGs
  - _Requisitos: 14.2_

- [ ] 14. Integración final y despliegue
- [ ] 14.1 Configurar Docker Compose completo
  - Integrar todos los servicios en docker-compose.yml
  - Configurar variables de entorno
  - Agregar healthchecks básicos
  - _Requisitos: 13.7_

- [ ] 14.2 Realizar testing de integración manual
  - Probar flujos completos de usuario
  - Verificar comunicación entre microservicios
  - Probar funcionalidades de red de ONGs
  - Validar manejo de errores básico
  - _Requisitos: 14.2, 14.5, 14.6_

- [ ] 14.3 Crear documentación de despliegue
  - Escribir README con instrucciones de instalación
  - Documentar configuración de variables de entorno
  - Crear guía de uso básica
  - _Requisitos: 14.4, 14.5_