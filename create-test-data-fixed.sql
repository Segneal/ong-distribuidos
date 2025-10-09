-- Script corregido para crear datos de prueba para la red de ONGs

-- Limpiar datos existentes de prueba
DELETE FROM eventos_externos WHERE organizacion_id IN ('fundacion-esperanza', 'ong-solidaria', 'ayuda-vecinal', 'educacion-popular', 'salud-comunitaria');
DELETE FROM solicitudes_externas WHERE organizacion_solicitante IN ('fundacion-esperanza', 'ong-solidaria', 'ayuda-vecinal', 'educacion-popular', 'salud-comunitaria');
DELETE FROM ofertas_externas WHERE organizacion_donante IN ('fundacion-esperanza', 'ong-solidaria', 'ayuda-vecinal', 'educacion-popular', 'salud-comunitaria');

-- Insertar eventos externos de prueba (simulando otras organizaciones)
INSERT INTO eventos_externos (
    evento_id, 
    organizacion_id, 
    nombre, 
    descripcion, 
    fecha_evento, 
    activo
) VALUES 
(
    'EVT-FUND-001',
    'fundacion-esperanza',
    'Jornada de Vacunación Comunitaria',
    'Vacunación gratuita contra la gripe para toda la comunidad. Se necesitan voluntarios para registro y organización.',
    '2024-02-15 09:00:00',
    true
),
(
    'EVT-SOLID-002', 
    'ong-solidaria',
    'Campaña de Donación de Sangre',
    'Jornada de donación voluntaria de sangre en colaboración con el hospital municipal. Buscamos voluntarios para apoyo logístico.',
    '2024-02-20 08:00:00',
    true
),
(
    'EVT-AYUDA-003',
    'ayuda-vecinal',
    'Entrega de Alimentos en Barrios Vulnerables',
    'Distribución de bolsones de alimentos en barrios de bajos recursos. Se requieren voluntarios para armado y distribución.',
    '2024-02-25 10:00:00',
    true
),
(
    'EVT-EDUC-004',
    'educacion-popular',
    'Taller de Apoyo Escolar',
    'Taller de apoyo escolar para niños de primaria. Necesitamos voluntarios con conocimientos básicos de matemáticas y lengua.',
    '2024-03-01 14:00:00',
    true
),
(
    'EVT-SALUD-005',
    'salud-comunitaria',
    'Operativo Médico Gratuito',
    'Atención médica gratuita con especialistas. Buscamos voluntarios para recepción y organización de turnos.',
    '2024-03-05 08:30:00',
    true
);

-- Insertar solicitudes de donaciones externas de prueba
INSERT INTO solicitudes_externas (
    solicitud_id,
    organizacion_solicitante,
    donaciones,
    activa
) VALUES
(
    'REQ-FUND-001',
    'fundacion-esperanza',
    '[{"category": "ALIMENTOS", "description": "Leche en polvo para bebés"}, {"category": "MEDICAMENTOS", "description": "Paracetamol infantil"}]',
    true
),
(
    'REQ-SOLID-002',
    'ong-solidaria',
    '[{"category": "ROPA", "description": "Abrigos para invierno talle adulto"}, {"category": "ALIMENTOS", "description": "Conservas de atún"}]',
    true
),
(
    'REQ-AYUDA-003',
    'ayuda-vecinal',
    '[{"category": "JUGUETES", "description": "Juguetes didácticos para niños de 3-8 años"}, {"category": "LIBROS", "description": "Libros de cuentos infantiles"}]',
    true
);

-- Insertar ofertas de donaciones externas de prueba
INSERT INTO ofertas_externas (
    oferta_id,
    organizacion_donante,
    donaciones,
    activa
) VALUES
(
    'OFF-EDUC-001',
    'educacion-popular',
    '[{"category": "LIBROS", "description": "Libros de texto de primaria", "quantity": "50 unidades"}, {"category": "UTILES_ESCOLARES", "description": "Cuadernos y lápices", "quantity": "100 sets"}]',
    true
),
(
    'OFF-SALUD-002',
    'salud-comunitaria',
    '[{"category": "MEDICAMENTOS", "description": "Vendas y gasas", "quantity": "20 paquetes"}, {"category": "OTROS", "description": "Alcohol en gel", "quantity": "10 litros"}]',
    true
);

-- Verificar que las tablas tienen datos
SELECT 'Eventos externos:' as tabla, COUNT(*) as cantidad FROM eventos_externos WHERE activo = true
UNION ALL
SELECT 'Solicitudes externas:' as tabla, COUNT(*) as cantidad FROM solicitudes_externas WHERE activa = true
UNION ALL
SELECT 'Ofertas externas:' as tabla, COUNT(*) as cantidad FROM ofertas_externas WHERE activa = true;