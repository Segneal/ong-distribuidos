# Documento de Requisitos - Sistema de Gestión ONG "Empuje Comunitario"

## Introducción

El sistema de gestión para la ONG "Empuje Comunitario" es una plataforma web integral que permite administrar usuarios, inventario de donaciones y eventos solidarios. El sistema incluye integración con una red de ONGs mediante colas de mensajes Kafka para facilitar la colaboración interorganizacional. La arquitectura utiliza microservicios con gRPC, un API Gateway en Node.js/Express, y una interfaz web moderna en React.

## Requisitos

### Requisito 1 - Sistema de Autenticación y Roles

**Historia de Usuario:** Como administrador del sistema, quiero un sistema de roles bien definido para controlar el acceso a las diferentes funcionalidades según el tipo de usuario.

#### Criterios de Aceptación

1. CUANDO el sistema se inicializa ENTONCES DEBE definir cuatro roles: Presidente, Vocal, Coordinador y Voluntario
2. CUANDO un usuario tiene rol Presidente ENTONCES DEBE tener acceso a todas las funcionalidades del sistema
3. CUANDO un usuario tiene rol Vocal ENTONCES DEBE tener acceso únicamente al inventario de donaciones
4. CUANDO un usuario tiene rol Coordinador ENTONCES DEBE tener acceso a la gestión de eventos solidarios
5. CUANDO un usuario tiene rol Voluntario ENTONCES DEBE tener acceso de solo lectura a eventos solidarios y poder participar en ellos

### Requisito 2 - Gestión de Usuarios

**Historia de Usuario:** Como Presidente de la ONG, quiero gestionar los usuarios del sistema para mantener actualizada la información de los miembros de la organización.

#### Criterios de Aceptación

1. CUANDO accedo como Presidente ENTONCES DEBE mostrar una vista de ABM de usuarios
2. CUANDO creo un usuario ENTONCES DEBE requerir nombre de usuario único, nombre, apellido y email único
3. CUANDO creo un usuario ENTONCES DEBE generar una contraseña aleatoria y enviarla por email usando Nodemailer
4. CUANDO creo un usuario ENTONCES DEBE encriptar la contraseña antes de guardarla en la base de datos
5. CUANDO creo un usuario en entorno de testing ENTONCES DEBE escribir usuario y contraseña en archivo /testing/usuarios/passlogs.txt
6. CUANDO modifico un usuario ENTONCES DEBE permitir cambiar todos los campos excepto la contraseña
7. CUANDO elimino un usuario ENTONCES DEBE aplicar baja lógica marcándolo como inactivo
8. CUANDO un usuario está inactivo ENTONCES DEBE removerlo automáticamente de eventos futuros

### Requisito 3 - Sistema de Login

**Historia de Usuario:** Como usuario del sistema, quiero poder iniciar sesión de forma segura para acceder a las funcionalidades según mi rol.

#### Criterios de Aceptación

1. CUANDO ingreso credenciales ENTONCES DEBE permitir login con nombre de usuario o email
2. CUANDO las credenciales son incorrectas ENTONCES DEBE mostrar mensaje específico del error
3. CUANDO el usuario no existe ENTONCES DEBE mostrar mensaje "Usuario/email inexistente"
4. CUANDO la contraseña es incorrecta ENTONCES DEBE mostrar mensaje "Credenciales incorrectas"
5. CUANDO el usuario está inactivo ENTONCES DEBE denegar el acceso con mensaje apropiado
6. CUANDO el login es exitoso ENTONCES DEBE redirigir según el rol del usuario

### Requisito 4 - Inventario de Donaciones

**Historia de Usuario:** Como Vocal o Presidente, quiero gestionar el inventario de donaciones para mantener un registro actualizado de los recursos disponibles.

#### Criterios de Aceptación

1. CUANDO accedo al inventario ENTONCES DEBE mostrar donaciones categorizadas por ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES
2. CUANDO registro una donación ENTONCES DEBE requerir categoría y permitir descripción y cantidad
3. CUANDO registro una donación ENTONCES DEBE validar que la cantidad no sea negativa
4. CUANDO registro una donación ENTONCES DEBE guardar campos de auditoría automáticamente
5. CUANDO modifico una donación ENTONCES DEBE permitir cambiar descripción y cantidad únicamente
6. CUANDO elimino una donación ENTONCES DEBE aplicar baja lógica con confirmación
7. CUANDO elimino una donación ENTONCES DEBE registrar la acción en auditoría

### Requisito 5 - Eventos Solidarios

**Historia de Usuario:** Como Coordinador o Presidente, quiero gestionar eventos solidarios para organizar las actividades de la ONG.

#### Criterios de Aceptación

1. CUANDO creo un evento ENTONCES DEBE requerir nombre, descripción y fecha futura
2. CUANDO creo un evento ENTONCES DEBE permitir asignar miembros activos al evento
3. CUANDO modifico un evento futuro ENTONCES DEBE permitir cambiar nombre, fecha y miembros
4. CUANDO modifico un evento pasado ENTONCES DEBE permitir registrar donaciones repartidas
5. CUANDO registro donaciones repartidas ENTONCES DEBE descontar del inventario automáticamente
6. CUANDO elimino un evento ENTONCES DEBE permitir eliminación física solo de eventos futuros
7. CUANDO un Voluntario accede ENTONCES DEBE poder agregarse o quitarse de eventos únicamente

### Requisito 6 - Solicitud de Donaciones (Red de ONGs)

**Historia de Usuario:** Como miembro de la red de ONGs, quiero solicitar donaciones a otras organizaciones para cubrir nuestras necesidades.

#### Criterios de Aceptación

1. CUANDO solicito donaciones ENTONCES DEBE publicar en tópico "/solicitud-donaciones"
2. CUANDO publico solicitud ENTONCES DEBE incluir ID organización, ID solicitud y lista de donaciones
3. CUANDO especifico donaciones ENTONCES DEBE incluir categoría y descripción
4. CUANDO recibo solicitudes externas ENTONCES DEBE cotejar con bajas de solicitudes
5. CUANDO una solicitud fue dada de baja ENTONCES DEBE descartarla del sistema

### Requisito 7 - Transferencia de Donaciones

**Historia de Usuario:** Como organización donante, quiero transferir donaciones a otras ONGs para colaborar con sus necesidades.

#### Criterios de Aceptación

1. CUANDO transfiero donaciones ENTONCES DEBE publicar en tópico "/transferencia-donaciones/id-organizacion-solicitante"
2. CUANDO publico transferencia ENTONCES DEBE incluir ID solicitud, ID organización donante y lista de donaciones
3. CUANDO especifico donaciones ENTONCES DEBE incluir categoría, descripción y cantidad
4. CUANDO transfiero donaciones ENTONCES DEBE descontar del inventario propio
5. CUANDO recibo donaciones ENTONCES DEBE sumar al inventario propio automáticamente

### Requisito 8 - Oferta de Donaciones

**Historia de Usuario:** Como organización, quiero ofrecer donaciones disponibles para que otras ONGs puedan solicitarlas.

#### Criterios de Aceptación

1. CUANDO ofrezco donaciones ENTONCES DEBE publicar en tópico "/oferta-donaciones"
2. CUANDO publico oferta ENTONCES DEBE incluir ID oferta, ID organización y lista de donaciones
3. CUANDO especifico donaciones ENTONCES DEBE incluir categoría, descripción y cantidad
4. CUANDO consulto ofertas externas ENTONCES DEBE mostrar todas las ofertas disponibles

### Requisito 9 - Gestión de Solicitudes de Donación

**Historia de Usuario:** Como organización, quiero poder dar de baja mis solicitudes de donación cuando ya no las necesite.

#### Criterios de Aceptación

1. CUANDO doy de baja una solicitud ENTONCES DEBE publicar en tópico "/baja-solicitud-donaciones"
2. CUANDO publico baja ENTONCES DEBE incluir ID organización solicitante e ID solicitud
3. CUANDO proceso bajas externas ENTONCES DEBE actualizar el estado de solicitudes en el sistema
4. CUANDO una solicitud es dada de baja ENTONCES DEBE removerla de las solicitudes activas

### Requisito 10 - Publicación de Eventos Externos

**Historia de Usuario:** Como organización, quiero publicar mis eventos para que voluntarios de otras ONGs puedan participar.

#### Criterios de Aceptación

1. CUANDO publico un evento ENTONCES DEBE enviar a tópico "/eventossolidarios"
2. CUANDO publico evento ENTONCES DEBE incluir ID organización, ID evento, nombre, descripción y fecha
3. CUANDO proceso eventos externos ENTONCES DEBE descartar eventos propios
4. CUANDO proceso eventos externos ENTONCES DEBE validar que estén vigentes
5. CUANDO muestro eventos externos ENTONCES DEBE tener una pantalla dedicada para visualizarlos

### Requisito 11 - Baja de Eventos Externos

**Historia de Usuario:** Como organización, quiero notificar cuando doy de baja un evento para mantener actualizada la información en la red.

#### Criterios de Aceptación

1. CUANDO doy de baja un evento ENTONCES DEBE publicar en tópico "/baja-evento-solidario"
2. CUANDO publico baja ENTONCES DEBE incluir ID organización e ID evento
3. CUANDO proceso bajas de eventos ENTONCES DEBE actualizar el estado en el sistema
4. CUANDO un evento externo es dado de baja ENTONCES DEBE removerlo de la lista de eventos disponibles

### Requisito 12 - Adhesión a Eventos Externos

**Historia de Usuario:** Como Voluntario, quiero poder adherirme a eventos de otras organizaciones para participar en actividades colaborativas.

#### Criterios de Aceptación

1. CUANDO me adhiero a un evento externo ENTONCES DEBE publicar en tópico "/adhesion-evento/id-organizador"
2. CUANDO publico adhesión ENTONCES DEBE incluir ID evento, datos del voluntario (ID, nombre, apellido, teléfono, email)
3. CUANDO publico adhesión ENTONCES DEBE incluir ID de mi organización
4. CUANDO confirmo adhesión ENTONCES DEBE registrar la participación en el sistema

### Requisito 13 - Arquitectura del Sistema

**Historia de Usuario:** Como desarrollador, quiero una arquitectura escalable y mantenible que soporte los requerimientos del sistema.

#### Criterios de Aceptación

1. CUANDO implemento la arquitectura ENTONCES DEBE usar microservicios con gRPC
2. CUANDO implemento servicios ENTONCES DEBE crear servicios independientes para usuarios, inventario y eventos
3. CUANDO implemento el API Gateway ENTONCES DEBE usar Node.js con Express
4. CUANDO implemento el frontend ENTONCES DEBE usar React con componentes funcionales
5. CUANDO implemento mensajería ENTONCES DEBE usar Apache Kafka para comunicación entre ONGs
6. CUANDO implemento envío de emails ENTONCES DEBE usar Nodemailer para notificaciones
7. CUANDO implemento la base de datos ENTONCES DEBE usar un sistema que soporte auditoría
8. CUANDO despliego el sistema ENTONCES DEBE usar Docker para containerización

### Requisito 14 - Documentación y Testing

**Historia de Usuario:** Como desarrollador y usuario final, quiero documentación completa y casos de prueba para garantizar la calidad del sistema.

#### Criterios de Aceptación

1. CUANDO desarrollo APIs ENTONCES DEBE documentar con Swagger
2. CUANDO creo casos de prueba ENTONCES DEBE usar Postman para testing de APIs
3. CUANDO preparo datos de prueba ENTONCES DEBE insertar directamente en la base de datos
4. CUANDO creo usuarios en testing ENTONCES DEBE generar archivo de log con credenciales en /testing/usuarios/passlogs.txt
5. CUANDO escribo documentación ENTONCES DEBE estar completamente en español
6. CUANDO implemento funcionalidades ENTONCES DEBE incluir casos de prueba unitarios e integración