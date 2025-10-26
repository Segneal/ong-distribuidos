# Sistema de Gestión para Red de ONGs - "Empuje Comunitario"

## La Historia Detrás del Proyecto

Imaginate que trabajás en una ONG y todos los días te enfrentás a los mismos problemas: tenés donaciones que no sabés bien cómo organizar, eventos que planificar, voluntarios que coordinar, y lo peor de todo... sabés que hay otras ONGs cerca tuyo que podrían ayudarte, pero no tenés forma de comunicarte con ellas de manera eficiente.

Eso es exactamente lo que nos pasó cuando empezamos este proyecto. Queríamos crear algo que no solo ayudara a "Empuje Comunitario" a organizarse mejor internamente, sino que también les permitiera conectarse con otras organizaciones para hacer más impacto social trabajando juntos.

## ¿Qué Construimos?

Básicamente, armamos una plataforma web que es como el "WhatsApp de las ONGs" pero con superpoderes. Te permite:

### Para el día a día de tu ONG:
- **Manejar tu inventario**: Sabés exactamente qué donaciones tenés, cuántas, y quién las trajo
- **Organizar eventos**: Desde una jornada de vacunación hasta una entrega de útiles escolares
- **Gestionar voluntarios**: Quién puede hacer qué, quién se anotó para cada evento
- **Ver reportes**: Entender qué está funcionando y qué no

### Para colaborar con otras ONGs (la parte más copada):
- **Pedir ayuda**: "Necesito 50 abrigos para el invierno, ¿alguien tiene?"
- **Ofrecer lo que te sobra**: "Tengo 100 cuadernos, ¿alguna ONG los necesita?"
- **Transferir donaciones**: Enviar directamente recursos a quien los necesita
- **Eventos colaborativos**: "Hacemos una feria de salud juntos?"

## ¿Cómo Funciona Por Dentro?

Acá viene la parte técnica, pero te la explico como si fuéramos amigos tomando un café:

### La Arquitectura (o "Cómo Organizamos Todo")

Pensá en el sistema como una empresa con diferentes departamentos:

```
Frontend (La Cara Bonita) ←→ API Gateway (El Portero) ←→ Microservicios (Los Especialistas)
                                                                    ↓
                                                            Base de Datos (La Memoria)
                                                                    ↓
                                                            Kafka (El Mensajero)
```

**El Frontend** es lo que ves cuando entrás a la página. Está hecho en React (que es como el WordPress de las aplicaciones modernas) y se ve lindo gracias a Material-UI.

**El API Gateway** es como el portero de un edificio. Todas las peticiones pasan por ahí, él verifica que tengas permisos y te manda al departamento correcto.

**Los Microserviios** son como especialistas:
- **User Service**: El de RRHH, maneja usuarios y permisos
- **Inventory Service**: El del depósito, controla las donaciones
- **Events Service**: El coordinador de eventos
- **Messaging Service**: El que habla con otras ONGs
- **Reports Service**: El contador, hace todos los reportes

**La Base de Datos** es donde guardamos todo. Usamos MySQL porque es confiable y fácil de manejar.

**Kafka** es el sistema de mensajería. Imaginate que es como un WhatsApp grupal gigante donde todas las ONGs pueden mandarse mensajes, pero de forma súper organizada y confiable.

## Las Funcionalidades Que Más Nos Enorgullecen

### 1. El Sistema de Roles (Porque No Todos Pueden Hacer Todo)
- **Presidente**: Puede hacer de todo, es el admin
- **Vocal**: Maneja donaciones y puede autorizar transferencias
- **Coordinador**: Organiza eventos y maneja voluntarios
- **Voluntario**: Participa en eventos y ve información básica

### 2. La Red de ONGs (La Joya de la Corona)
Esto es lo que hace especial al sistema. Imaginate que tu ONG necesita abrigos para el invierno:

1. Creás una "solicitud" en el sistema
2. El sistema la publica en la red (via Kafka)
3. Otras ONGs la ven y pueden responder
4. Si alguien tiene abrigos, puede hacer una "transferencia"
5. Vos recibís una notificación y coordinás la entrega

Todo queda registrado, es transparente, y funciona 24/7.

### 3. Los Reportes Inteligentes
No son solo números aburridos. Podés ver:
- Qué donaciones recibiste este mes vs el anterior
- Cuánta gente participó en tus eventos
- Qué tan activa está tu ONG en la red
- Y exportar todo a Excel para presentaciones

## Las Tecnologías Que Usamos (Y Por Qué)

### Frontend: React + Material-UI
**¿Por qué React?** Porque es lo que usa todo el mundo, hay mucha documentación, y es fácil encontrar gente que lo sepa.

**¿Por qué Material-UI?** Porque queríamos que se vea profesional sin tener que diseñar todo desde cero.

### Backend: Python + gRPC
**¿Por qué Python?** Porque es fácil de leer, rápido de desarrollar, y tiene librerías para todo.

**¿Por qué gRPC?** Porque es súper rápido para comunicación entre servicios y maneja bien los errores.

### Base de Datos: MySQL
**¿Por qué MySQL?** Porque es confiable, conocido, y funciona bien en Windows (que es donde desarrollamos).

### Mensajería: Apache Kafka
**¿Por qué Kafka?** Porque cuando mandás un mensaje a otra ONG, querés estar seguro de que llegue. Kafka garantiza eso.

## Los Desafíos Que Enfrentamos

### 1. La Migración de PostgreSQL a MySQL
Al principio usábamos PostgreSQL, pero tuvimos problemas de encoding en Windows. Migrar toda la base de datos fue un dolor de cabeza, pero valió la pena.

### 2. Sincronizar los JWT Secrets
Los tokens de autenticación no funcionaban entre servicios porque cada uno tenía su propia "clave secreta". Tardamos un día entero en darnos cuenta.

### 3. La UI de la Red de ONGs
Al principio no se distinguía qué solicitudes eran tuyas y cuáles de otras ONGs. Los usuarios se confundían. Tuvimos que agregar colores y badges para que fuera más claro.

## Cómo Probarlo

### Datos de Prueba
Creamos usuarios de ejemplo para que puedas probar todo:
- **admin/admin123**: El presidente, puede hacer todo
- **vocal1/admin123**: Maneja inventario
- **coord1/admin123**: Organiza eventos
- **vol1/admin123**: Voluntario básico

### Escenarios de Prueba
1. **Logueate como admin** y creá una donación nueva
2. **Cambiá a coordinador** y organizá un evento
3. **Agregá participantes** al evento
4. **Registrá donaciones repartidas** en el evento
5. **Probá la red de ONGs** creando una solicitud

## Lo Que Aprendimos

### Técnico
- **Los microservicios están buenos**, pero hay que pensarlos bien desde el principio
- **Kafka es poderoso**, pero también complejo. Vale la pena para casos como este
- **La consistencia es clave**: nombres de campos, estilos de código, todo tiene que ser coherente

### De Producto
- **Los usuarios necesitan feedback visual inmediato**. Si hacés click en algo, tiene que pasar algo visible
- **Los roles y permisos son críticos** en este tipo de sistemas
- **La documentación es tan importante como el código**

## El Impacto Esperado

### Para una ONG individual:
- Menos tiempo perdido en administración
- Mejor control de recursos
- Eventos más organizados
- Reportes para conseguir más fondos

### Para la red de ONGs:
- Menos desperdicio de recursos
- Más colaboración
- Mayor impacto social
- Transparencia en las operaciones

## Próximos Pasos

Si tuviéramos más tiempo, agregaríamos:
- **App móvil** para voluntarios
- **Integración con redes sociales** para promocionar eventos
- **Sistema de reputación** para ONGs en la red
- **Inteligencia artificial** para sugerir colaboraciones

## Reflexión Final

Este proyecto nos enseñó que la tecnología puede ser una herramienta poderosa para el bien social, pero solo si se diseña pensando en las personas que la van a usar. No se trata de usar la tecnología más nueva o más compleja, sino de resolver problemas reales de manera simple y efectiva.

Al final del día, si una ONG puede ayudar a más gente gracias a nuestro sistema, entonces hicimos bien nuestro trabajo.

---

*"La tecnología es mejor cuando acerca a las personas"* - Matt Mullenweg

Y eso es exactamente lo que quisimos hacer: acercar a las ONGs para que juntas puedan hacer más por su comunidad.