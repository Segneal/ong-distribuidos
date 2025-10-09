-- Datos de prueba para la red de ONGs
-- Ejecutar después de que el sistema esté funcionando

-- Insertar eventos externos de prueba (simulando otras organizaciones)
INSERT INTO eventos_externos (
    event_id, 
    organization_id, 
    organization_name, 
    name, 
    description, 
    event_date, 
    timestamp, 
    active
) VALUES 
(
    'EVT-FUND-001',
    'fundacion-esperanza',
    'Fundación Esperanza',
    'Jornada de Vacunación Comunitaria',
    'Vacunación gratuita contra la gripe para toda la comunidad. Necesitamos voluntarios para registro y organización.',
    '2024-02-15 09:00:00',
    NOW(),
    true
),
(
    'EVT-SOLID-002', 
    'ong-solidaria',
    'ONG Solidaria',
    'Campaña de Donación de Sangre',
    'Jornada de donación voluntaria de sangre en el hospital municipal. Buscamos voluntarios para difusión y acompañamiento.',
    '2024-02-20 08:00:00',
    NOW(),
    true
),
(
    'EVT-AYUDA-003',
    'ayuda-vecinal',
    'Ayuda Vecinal',
    'Entrega de Alimentos en Barrios',
    'Distribución de bolsones de alimentos en barrios vulnerables. Necesitamos voluntarios para armado y entrega.',
    '2024-02-25 14:00:00',
    NOW(),
    true
),
(
    'EVT-EDUC-004',
    'educacion-popular',
    'Educación Popular',
    'Taller de Apoyo Escolar',
    'Taller de apoyo escolar para niños de primaria. Buscamos voluntarios con experiencia en educación.',
    '2024-03-01 16:00:00',
    NOW(),
    true
);

-- Insertar solicitudes externas de donaciones
INSERT INTO solicitudes_externas (
    request_id,
    organization_id,
    organization_name,
    donations,
    timestamp,
    activa
) VALUES
(
    'REQ-FUND-001',
    'fundacion-esperanza',
    'Fundación Esperanza',
    '[{"category": "MEDICAMENTOS", "description": "Alcohol en gel y barbijos"}, {"category": "ALIMENTOS", "description": "Leche en polvo para bebés"}]',
    NOW(),
    true
),
(
    'REQ-SOLID-002',
    'ong-solidaria', 
    'ONG Solidaria',
    '[{"category": "ROPA", "description": "Abrigos para invierno talle adulto"}, {"category": "ALIMENTOS", "description": "Conservas y alimentos no perecederos"}]',
    NOW(),
    true
),
(
    'REQ-AYUDA-003',
    'ayuda-vecinal',
    'Ayuda Vecinal',
    '[{"category": "JUGUETES", "description": "Juguetes para niños de 3 a 10 años"}, {"category": "LIBROS", "description": "Libros de cuentos infantiles"}]',
    NOW(),
    true
);

-- Insertar ofertas externas de donaciones
INSERT INTO ofertas_externas (
    offer_id,
    organization_id,
    organization_name,
    donations,
    timestamp,
    activa
) VALUES
(
    'OFF-FUND-001',
    'fundacion-esperanza',
    'Fundación Esperanza',
    '[{"category": "ROPA", "description": "Ropa de bebé en buen estado", "quantity": "50 prendas"}, {"category": "JUGUETES", "description": "Juguetes didácticos", "quantity": "20 unidades"}]',
    NOW(),
    true
),
(
    'OFF-EDUC-002',
    'educacion-popular',
    'Educación Popular',
    '[{"category": "LIBROS", "description": "Libros de texto escolares", "quantity": "100 libros"}, {"category": "UTILES_ESCOLARES", "description": "Cuadernos y útiles", "quantity": "200 unidades"}]',
    NOW(),
    true
);

-- Verificar que se insertaron correctamente
SELECT 'Eventos externos insertados:' as info, COUNT(*) as cantidad FROM eventos_externos;
SELECT 'Solicitudes externas insertadas:' as info, COUNT(*) as cantidad FROM solicitudes_externas;
SELECT 'Ofertas externas insertadas:' as info, COUNT(*) as cantidad FROM ofertas_externas;