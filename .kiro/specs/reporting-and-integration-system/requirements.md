# Documento de Requerimientos

## Introducción

Este documento describe los requerimientos para implementar un sistema integral de reportes e integración para la plataforma de gestión de ONGs. El sistema proporcionará reportes de donaciones, reportes de participación en eventos, gestión de filtros personalizados, capacidades de exportación a Excel, e integración SOAP para consultar datos de la red externa de ONGs. La implementación utilizará los protocolos REST, GraphQL y SOAP según se especifica para cada funcionalidad.

## Requerimientos

### Requerimiento 1

**Historia de Usuario:** Como Presidente o Vocal, quiero ver reportes de donaciones con capacidades de filtrado, para poder analizar patrones de donaciones y tomar decisiones informadas sobre las actividades de donación de nuestra organización.

#### Criterios de Aceptación

1. CUANDO un Presidente o Vocal accede a la pantalla de reporte de donaciones ENTONCES el sistema DEBE mostrar una interfaz GraphQL para consultar donaciones
2. CUANDO se proporcionan opciones de filtrado ENTONCES el sistema DEBE soportar filtrado por categoría, rango de fechas de Alta, y estado de eliminado (sí, no, o ambos)
3. CUANDO no se aplican filtros ENTONCES el sistema DEBE mostrar todos los registros de donaciones
4. CUANDO se aplican filtros ENTONCES el sistema DEBE retornar resultados agrupados por categoría y estado de eliminado
5. CUANDO se muestran resultados ENTONCES el sistema DEBE mostrar la suma total de cantidades recibidas o donadas para cada categoría
6. CUANDO se combinan múltiples filtros ENTONCES el sistema DEBE aplicar todos los filtros simultáneamente usando lógica AND

### Requerimiento 2

**Historia de Usuario:** Como cualquier usuario con acceso al reporte de donaciones, quiero guardar y gestionar configuraciones de filtros personalizados, para poder reutilizar rápidamente criterios de búsqueda frecuentes sin tener que reconfigurarlos cada vez.

#### Criterios de Aceptación

1. CUANDO un usuario configura filtros en el reporte de donaciones ENTONCES el sistema DEBE proporcionar un botón "Guardar Filtro"
2. CUANDO se guarda un filtro ENTONCES el sistema DEBE requerir que el usuario proporcione un nombre descriptivo para la configuración del filtro
3. CUANDO se guarda un filtro ENTONCES el sistema DEBE almacenar la configuración del filtro asociada con la cuenta del usuario usando mutaciones GraphQL
4. CUANDO se accede a la pantalla de reporte de donaciones ENTONCES el sistema DEBE mostrar todos los filtros guardados para el usuario actual
5. CUANDO se selecciona un filtro guardado ENTONCES el sistema DEBE aplicar automáticamente la configuración del filtro almacenada
6. CUANDO se gestionan filtros guardados ENTONCES el sistema DEBE permitir a los usuarios editar nombres y configuraciones de filtros existentes
7. CUANDO se gestionan filtros guardados ENTONCES el sistema DEBE permitir a los usuarios eliminar configuraciones de filtros no deseadas
8. CUANDO se elimina un filtro ENTONCES el sistema DEBE removerlo permanentemente de los filtros guardados del usuario

### Requerimiento 3

**Historia de Usuario:** Como usuario viendo reportes de donaciones, quiero exportar los datos detallados a formato Excel, para poder realizar análisis adicionales o compartir la información con stakeholders fuera del sistema.

#### Criterios de Aceptación

1. CUANDO se visualizan reportes de donaciones ENTONCES el sistema DEBE proporcionar una opción "Exportar a Excel" vía API REST
2. CUANDO se exporta a Excel ENTONCES el sistema DEBE crear hojas de trabajo separadas para cada categoría de donación
3. CUANDO se generan hojas de Excel ENTONCES cada hoja DEBE contener registros detallados sin sumarización
4. CUANDO se muestran detalles de donaciones ENTONCES cada registro DEBE incluir: fecha de Alta, Descripción, Cantidad, estado de Eliminado, usuario de Creación, y usuario de Modificación
5. CUANDO se genera el archivo Excel ENTONCES el sistema DEBE proporcionar un enlace de descarga para el archivo
6. CUANDO existen filtros aplicados ENTONCES la exportación Excel DEBE respetar los mismos criterios de filtrado que el reporte en pantalla
7. CUANDO se completa la exportación ENTONCES el sistema DEBE retornar un archivo Excel correctamente formateado con encabezados apropiados

### Requerimiento 4

**Historia de Usuario:** Como cualquier usuario del sistema, quiero ver reportes de participación en eventos no cancelados, para poder rastrear el compromiso de los miembros y la efectividad de eventos dentro de nuestra organización.

#### Criterios de Aceptación

1. CUANDO cualquier usuario accede al reporte de participación en eventos ENTONCES el sistema DEBE mostrar una interfaz GraphQL para consultar participación en eventos
2. CUANDO se proporcionan opciones de filtrado ENTONCES el sistema DEBE soportar filtrado por rango de fechas, usuario, y estado de reparto de donaciones (sí, no, o ambos)
3. CUANDO un Presidente o Coordinador aplica filtros de usuario ENTONCES el sistema DEBE permitir selección de cualquier usuario en la organización
4. CUANDO un no-Presidente/Coordinador aplica filtros de usuario ENTONCES el sistema DEBE restringir la selección solo a su propia cuenta de usuario
5. CUANDO se accede al reporte ENTONCES el filtro de usuario DEBE ser obligatorio y no puede dejarse vacío
6. CUANDO se muestran resultados ENTONCES el sistema DEBE agrupar datos por mes
7. CUANDO se muestran datos mensuales ENTONCES cada mes DEBE mostrar detalles del evento incluyendo: día, nombre del evento, descripción, y donaciones asociadas
8. CUANDO se consultan eventos ENTONCES el sistema DEBE excluir eventos cancelados de todos los resultados

### Requerimiento 5

**Historia de Usuario:** Como cualquier usuario con acceso al reporte de participación en eventos, quiero guardar y gestionar configuraciones de filtros personalizados para reportes de eventos, para poder reutilizar eficientemente patrones de búsqueda comunes.

#### Criterios de Aceptación

1. CUANDO un usuario configura filtros en el reporte de participación en eventos ENTONCES el sistema DEBE proporcionar un botón "Guardar Filtro" vía API REST
2. CUANDO se guarda un filtro de eventos ENTONCES el sistema DEBE requerir que el usuario proporcione un nombre descriptivo para la configuración del filtro
3. CUANDO se guarda un filtro de eventos ENTONCES el sistema DEBE almacenar la configuración del filtro asociada con la cuenta del usuario
4. CUANDO se accede a la pantalla de reporte de participación en eventos ENTONCES el sistema DEBE mostrar todos los filtros de eventos guardados para el usuario actual
5. CUANDO se selecciona un filtro de eventos guardado ENTONCES el sistema DEBE aplicar automáticamente la configuración del filtro almacenada
6. CUANDO se gestionan filtros de eventos guardados ENTONCES el sistema DEBE permitir a los usuarios editar nombres y configuraciones de filtros existentes
7. CUANDO se gestionan filtros de eventos guardados ENTONCES el sistema DEBE permitir a los usuarios eliminar configuraciones de filtros no deseadas
8. CUANDO se elimina un filtro de eventos ENTONCES el sistema DEBE removerlo permanentemente de los filtros guardados del usuario

### Requerimiento 6

**Historia de Usuario:** Como Presidente, quiero consultar información sobre otros presidentes de ONGs y organizaciones en nuestra red vía integración SOAP, para poder acceder a datos centralizados de la red para coordinación y propósitos de colaboración.

#### Criterios de Aceptación

1. CUANDO un Presidente accede a la pantalla de consulta de red ENTONCES el sistema DEBE proporcionar una interfaz para consultas basadas en SOAP
2. CUANDO se consultan datos de red ENTONCES el sistema DEBE proporcionar un campo de entrada para ingresar una lista de IDs de organizaciones
3. CUANDO se envían IDs de organizaciones ENTONCES el sistema DEBE llamar al servicio SOAP en https://soap-applatest.onrender.com/?wsdl
4. CUANDO se realizan llamadas SOAP ENTONCES el sistema DEBE recuperar tanto datos de presidentes como datos de organizaciones para cada ID proporcionado
5. CUANDO se reciben respuestas SOAP ENTONCES el sistema DEBE mostrar la información del presidente para cada organización
6. CUANDO se reciben respuestas SOAP ENTONCES el sistema DEBE mostrar los detalles de la organización para cada ID consultado
7. CUANDO ocurren errores del servicio SOAP ENTONCES el sistema DEBE manejar errores graciosamente y mostrar mensajes de error apropiados
8. CUANDO se proporcionan IDs de organizaciones inválidos ENTONCES el sistema DEBE mostrar mensajes de validación apropiados

### Requerimiento 7

**Historia de Usuario:** Como desarrollador, quiero documentación API comprensiva para los nuevos endpoints REST, para poder entender e integrar con el sistema efectivamente.

#### Criterios de Aceptación

1. CUANDO se implementan endpoints REST ENTONCES el sistema DEBE proporcionar documentación Swagger para todas las nuevas APIs REST
2. CUANDO se accede a documentación API ENTONCES Swagger DEBE incluir descripciones detalladas de endpoints, parámetros, y esquemas de respuesta
3. CUANDO se documentan endpoints ENTONCES Swagger DEBE cubrir endpoints de exportación Excel y gestión de filtros personalizados
4. CUANDO se genera documentación API ENTONCES DEBE ser accesible a través de una interfaz Swagger UI estándar
5. CUANDO cambian endpoints ENTONCES la documentación Swagger DEBE actualizarse automáticamente para reflejar las especificaciones API actuales

### Requerimiento 8

**Historia de Usuario:** Como arquitecto de sistemas, quiero que los nuevos módulos sean desplegables independientemente, para que puedan ser desarrollados y mantenidos separadamente de los componentes existentes del sistema.

#### Criterios de Aceptación

1. CUANDO se implementa nueva funcionalidad ENTONCES el sistema DEBE soportar despliegue como microservicios independientes
2. CUANDO se despliegan servicios ENTONCES cada tipo de protocolo (REST/GraphQL/SOAP) PUEDE ser implementado como microservicios separados
3. CUANDO se despliegan servicios ENTONCES toda la nueva funcionalidad PUEDE ser consolidada en un solo proyecto independiente
4. CUANDO se despliegan nuevos módulos ENTONCES DEBEN ser completamente independientes de los componentes existentes del sistema
5. CUANDO se integra con datos existentes ENTONCES los nuevos módulos DEBEN acceder a bases de datos compartidas y recursos a través de interfaces bien definidas