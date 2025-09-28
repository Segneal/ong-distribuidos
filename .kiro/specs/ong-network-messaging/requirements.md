# Requirements Document

## Introduction

Este documento define los requerimientos para implementar un sistema de mensajería basado en Apache Kafka que permita a nuestra organización participar en una red de ONGs. El sistema facilitará la colaboración interorganizacional mediante el intercambio de solicitudes de donaciones, transferencias, ofertas, eventos y notificaciones entre organizaciones de la red.

## Requirements

### Requirement 1

**Historia de Usuario:** Como administrador de ONG, quiero poder solicitar donaciones a otras organizaciones de la red, para que puedan conocer nuestras necesidades y potencialmente ayudarnos.

#### Criterios de Aceptación

1. CUANDO el administrador crea una solicitud de donación ENTONCES el sistema DEBE publicar un mensaje en el topic "/solicitud-donaciones" con ID de organización, ID de solicitud y lista de donaciones requeridas
2. CUANDO se especifica una donación requerida ENTONCES el sistema DEBE incluir categoría y descripción en el mensaje
3. CUANDO se procesa una solicitud externa ENTONCES el sistema DEBE verificar que no esté dada de baja antes de mostrarla
4. CUANDO se recibe una solicitud de donación ENTONCES el sistema DEBE almacenar la información para consulta posterior

### Requirement 2

**Historia de Usuario:** Como administrador de ONG, quiero poder transferir donaciones a organizaciones que las han solicitado, para que puedan recibir la ayuda que necesitan.

#### Criterios de Aceptación

1. CUANDO el administrador selecciona transferir donaciones ENTONCES el sistema DEBE publicar un mensaje en el topic "/transferencia-donaciones/id-organizacion-solicitante"
2. CUANDO se confirma una transferencia ENTONCES el sistema DEBE incluir ID de solicitud, ID de organización donante, y lista de donaciones con categoría, descripción y cantidad
3. CUANDO se realiza una transferencia ENTONCES el sistema DEBE descontar la cantidad del inventario de la organización donante
4. CUANDO nuestra organización recibe una donación ENTONCES el sistema DEBE sumar la cantidad al inventario local
5. CUANDO no hay suficiente inventario ENTONCES el sistema DEBE mostrar un error y no permitir la transferencia

### Requirement 3

**Historia de Usuario:** Como administrador de ONG, quiero poder ofrecer donaciones disponibles a la red, para que otras organizaciones puedan conocer lo que tenemos disponible.

#### Criterios de Aceptación

1. CUANDO el administrador crea una oferta de donación ENTONCES el sistema DEBE publicar un mensaje en el topic "/oferta-donaciones"
2. CUANDO se publica una oferta ENTONCES el sistema DEBE incluir ID de oferta, ID de organización donante, y lista de donaciones con categoría, descripción y cantidad
3. CUANDO se reciben ofertas externas ENTONCES el sistema DEBE permitir consultar las donaciones ofrecidas por otras organizaciones
4. CUANDO se visualizan ofertas ENTONCES el sistema DEBE mostrar solo ofertas vigentes de otras organizaciones

### Requirement 4

**Historia de Usuario:** Como administrador de ONG, quiero poder dar de baja solicitudes de donación, para que otras organizaciones sepan que ya no necesito esas donaciones.

#### Criterios de Aceptación

1. CUANDO el administrador da de baja una solicitud ENTONCES el sistema DEBE publicar un mensaje en el topic "/baja-solicitud-donaciones"
2. CUANDO se publica una baja ENTONCES el sistema DEBE incluir ID de organización solicitante e ID de solicitud
3. CUANDO se procesa una baja de solicitud externa ENTONCES el sistema DEBE actualizar el estado de la solicitud en el sistema local
4. CUANDO se consultan solicitudes ENTONCES el sistema DEBE filtrar las solicitudes dadas de baja

### Requirement 5

**Historia de Usuario:** Como administrador de ONG, quiero poder publicar eventos solidarios en la red, para que voluntarios de otras organizaciones puedan conocer y participar en nuestros eventos.

#### Criterios de Aceptación

1. CUANDO el administrador publica un evento ENTONCES el sistema DEBE enviar un mensaje al topic "/eventossolidarios"
2. CUANDO se publica un evento ENTONCES el sistema DEBE incluir ID de organización, ID de evento, nombre, descripción, fecha y hora
3. CUANDO se reciben eventos externos ENTONCES el sistema DEBE descartar eventos propios y almacenar solo eventos de otras organizaciones
4. CUANDO se procesa un evento externo ENTONCES el sistema DEBE verificar que esté vigente y no haya sido dado de baja
5. CUANDO se consultan eventos externos ENTONCES el sistema DEBE mostrar una pantalla con todos los eventos disponibles de otras organizaciones

### Requirement 6

**Historia de Usuario:** Como administrador de ONG, quiero poder dar de baja eventos solidarios, para que otras organizaciones sepan que el evento ya no está disponible.

#### Criterios de Aceptación

1. CUANDO el administrador da de baja un evento ENTONCES el sistema DEBE publicar un mensaje en el topic "/baja-evento-solidario"
2. CUANDO se publica una baja de evento ENTONCES el sistema DEBE incluir ID de organización e ID de evento
3. CUANDO se procesa una baja de evento externo ENTONCES el sistema DEBE actualizar el estado del evento en el sistema local
4. CUANDO se consultan eventos externos ENTONCES el sistema DEBE filtrar los eventos dados de baja

### Requirement 7

**Historia de Usuario:** Como voluntario, quiero poder adherirme a eventos de otras organizaciones, para que puedan conocer mi interés en participar.

#### Criterios de Aceptación

1. CUANDO un voluntario confirma adhesión a un evento externo ENTONCES el sistema DEBE publicar un mensaje en el topic "/adhesion-evento/id-organizador"
2. CUANDO se confirma una adhesión ENTONCES el sistema DEBE incluir ID de evento, datos del voluntario (ID organización, ID voluntario, nombre, apellido, teléfono, email)
3. CUANDO se recibe una adhesión a nuestros eventos ENTONCES el sistema DEBE notificar al administrador de la nueva adhesión
4. CUANDO un voluntario se adhiere ENTONCES el sistema DEBE registrar la adhesión en el sistema local

### Requirement 8

**Historia de Usuario:** Como administrador del sistema, quiero que el sistema maneje la conectividad con Kafka de manera robusta, para que las operaciones de mensajería sean confiables.

#### Criterios de Aceptación

1. CUANDO el sistema inicia ENTONCES el sistema DEBE establecer conexión con el broker de Kafka
2. CUANDO hay problemas de conectividad ENTONCES el sistema DEBE implementar reintentos automáticos
3. CUANDO se pierde la conexión ENTONCES el sistema DEBE mostrar el estado de conectividad al usuario
4. CUANDO se recupera la conexión ENTONCES el sistema DEBE procesar mensajes pendientes
5. CUANDO hay errores en el procesamiento ENTONCES el sistema DEBE registrar logs detallados para debugging

### Requirement 9

**Historia de Usuario:** Como administrador de ONG, quiero que el sistema mantenga sincronización con nuestra base de datos local, para que la información esté siempre actualizada.

#### Criterios de Aceptación

1. CUANDO se reciben mensajes de Kafka ENTONCES el sistema DEBE actualizar la base de datos local correspondiente
2. CUANDO se realizan cambios locales ENTONCES el sistema DEBE publicar los mensajes apropiados en Kafka
3. CUANDO hay conflictos de datos ENTONCES el sistema DEBE implementar estrategias de resolución
4. CUANDO se procesan mensajes ENTONCES el sistema DEBE validar la integridad de los datos antes de persistir