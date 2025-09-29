-- Datos de prueba para la red de ONGs (con estructura correcta)

-- Limpiar datos existentes de prueba
DELETE FROM eventos_externos WHERE organizacion_id IN ('fundacion-esperanza', 'ong-solidaria', 'ayuda-vecinal', 'educacion-popular');
DELETE FROM solicitudes_externas WHERE organizacion_id IN ('fundacion-esperanza', 'ong-solidaria', 'ayuda-vecinal', 'educacion-popular');
DELETE FROM ofertas_externas WHERE organizacion_id IN ('fundacion-esperanza', 'ong-solidaria', 'ayuda-vecinal', 'educacion-popular');

-- Insertar eventos externos de prueba
INSERT INTO eventos_externos (
    organizacion_id, 
    evento_id,
    nombre, 
    descripcion, 
    fecha_evento, 
    activo
) VALUES 
(
    'fundacion-esperanza',
    'EVT-FUND-001',
    'Jornada de Vacunación Comunitaria',
    'Vacunación gratuita contra la gripe para toda la comunidad. Necesitamos voluntarios para registro y organización.',
    '2024-02-15 09:00:00',
    true
),
(
    'ong-solidaria',
    'EVT-SOLID-002',
    'Campaña de Donación de Sangre',
    'Jornada de donación voluntaria de sangre en el hospital municipal. Buscamos voluntarios para difusión y acompañamiento.',
    '2024-02-20 08:00:00',
    true
),
(
    'ayuda-vecinal',
    'EVT-AYUDA-003',
    'Entrega de Alimentos en Barrios',
    'Distribución de bolsones de alimentos en barrios vulnerables. Necesitamos voluntarios para armado y entrega.',
    '2024-02-25 14:00:00',
    true
),
(
    'educacion-popular',
    'EVT-EDUC-004',
    'Taller de Apoyo Escolar',
    'Taller de apoyo escolar para niños de primaria. Buscamos voluntarios con experiencia en educación.',
    '2024-03-01 16:00:00',
    true
);

-- Insertar solicitudes externas de donaciones
INSERT INTO solicitudes_externas (
    organizacion_id,
    solicitud_id,
    donaciones,
    activa
) VALUES
(
    'fundacion-esperanza',
    'REQ-FUND-001',
    '[{"category": "MEDICAMENTOS", "description": "Alcohol en gel y barbijos"}, {"category": "ALIMENTOS", "description": "Leche en polvo para bebés"}]',
    true
),
(
    'ong-solidaria',
    'REQ-SOLID-002',
    '[{"category": "ROPA", "description": "Abrigos para invierno talle adulto"}, {"category": "ALIMENTOS", "description": "Conservas y alimentos no perecederos"}]',
    true
),
(
    'ayuda-vecinal',
    'REQ-AYUDA-003',
    '[{"category": "JUGUETES", "description": "Juguetes para niños de 3 a 10 años"}, {"category": "LIBROS", "description": "Libros de cuentos infantiles"}]',
    true
);

-- Insertar ofertas externas de donaciones
INSERT INTO ofertas_externas (
    organizacion_id,
    oferta_id,
    donaciones,
    activa
) VALUES
(
    'fundacion-esperanza',
    'OFF-FUND-001',
    '[{"category": "ROPA", "description": "Ropa de bebé en buen estado", "quantity": "50 prendas"}, {"category": "JUGUETES", "description": "Juguetes didácticos", "quantity": "20 unidades"}]',
    true
),
(
    'educacion-popular',
    'OFF-EDUC-002',
    '[{"category": "LIBROS", "description": "Libros de texto escolares", "quantity": "100 libros"}, {"category": "UTILES_ESCOLARES", "description": "Cuadernos y útiles", "quantity": "200 unidades"}]',
    true
);

-- Verificar que se insertaron correctamente
SELECT 'Eventos externos insertados:' as info, COUNT(*) as cantidad FROM eventos_externos WHERE organizacion_id != 'empuje-comunitario';
SELECT 'Solicitudes externas insertadas:' as info, COUNT(*) as cantidad FROM solicitudes_externas WHERE organizacion_id != 'empuje-comunitario';
SELECT 'Ofertas externas insertadas:' as info, COUNT(*) as cantidad FROM ofertas_externas WHERE organizacion_id != 'empuje-comunitario';

-- Mostrar algunos datos de ejemplo
SELECT 'EVENTOS DISPONIBLES:' as tipo, nombre, organizacion_id, fecha_evento FROM eventos_externos WHERE activo = true AND organizacion_id != 'empuje-comunitario' LIMIT 3;