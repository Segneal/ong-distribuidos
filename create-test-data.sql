-- Script para crear datos de prueba para la red de ONGs
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
    'Vacunación gratuita contra la gripe para toda la comunidad. Se necesitan voluntarios para registro y organización.',
    '2024-02-15 09:00:00',
    NOW(),
    true
),
(
    'EVT-SOLID-002', 
    'ong-solidaria',
    'ONG Solidaria',
    'Campaña de Donación de Sangre',
    'Jornada de donación voluntaria de sangre en colaboración con el hospital municipal. Buscamos voluntarios para apoyo logístico.',
    '2024-02-20 08:00:00',
    NOW(),
    true
),
(
    'EVT-AYUDA-003',
    'ayuda-vecinal',
    'Ayuda Vecinal',
    'Entrega de Alimentos en Barrios Vulnerables',
    'Distribución de bolsones de alimentos en barrios de bajos recursos. Se requieren voluntarios para armado y distribución.',
    '2024-02-25 10:00:00',
    NOW(),
    true
),
(
    'EVT-EDUC-004',
    'educacion-popular',
    'Educación Popular',
    'Taller de Apoyo Escolar',
    'Taller de apoyo escolar para niños de primaria. Necesitamos voluntarios con conocimientos básicos de matemáticas y lengua.',
    '2024-03-01 14:00:00',
    NOW(),
    true
),
(
    'EVT-SALUD-005',
    'salud-comunitaria',
    'Salud Comunitaria',
    'Operativo Médico Gratuito',
    'Atención médica gratuita con especialistas. Buscamos voluntarios para recepción y organización de turnos.',
    '2024-03-05 08:30:00',
    NOW(),
    true
);

-- Insertar solicitudes de donaciones externas de prueba
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
    '[{"category": "ALIMENTOS", "description": "Leche en polvo para bebés"}, {"category": "MEDICAMENTOS", "description": "Paracetamol infantil"}]',
    NOW(),
    true
),
(
    'REQ-SOLID-002',
    'ong-solidaria', 
    'ONG Solidaria',
    '[{"category": "ROPA", "description": "Abrigos para invierno talle adulto"}, {"category": "ALIMENTOS", "description": "Conservas de atún"}]',
    NOW(),
    true
),
(
    'REQ-AYUDA-003',
    'ayuda-vecinal',
    'Ayuda Vecinal',
    '[{"category": "JUGUETES", "description": "Juguetes didácticos para niños de 3-8 años"}, {"category": "LIBROS", "description": "Libros de cuentos infantiles"}]',
    NOW(),
    true
);

-- Insertar ofertas de donaciones externas de prueba
INSERT INTO ofertas_externas (
    offer_id,
    organization_id,
    organization_name,
    donations,
    timestamp,
    activa
) VALUES
(
    'OFF-EDUC-001',
    'educacion-popular',
    'Educación Popular',
    '[{"category": "LIBROS", "description": "Libros de texto de primaria", "quantity": "50 unidades"}, {"category": "UTILES_ESCOLARES", "description": "Cuadernos y lápices", "quantity": "100 sets"}]',
    NOW(),
    true
),
(
    'OFF-SALUD-002',
    'salud-comunitaria',
    'Salud Comunitaria',
    '[{"category": "MEDICAMENTOS", "description": "Vendas y gasas", "quantity": "20 paquetes"}, {"category": "OTROS", "description": "Alcohol en gel", "quantity": "10 litros"}]',
    NOW(),
    true
);

-- Verificar que las tablas existen y tienen datos
SELECT 'Eventos externos:' as tabla, COUNT(*) as cantidad FROM eventos_externos
UNION ALL
SELECT 'Solicitudes externas:' as tabla, COUNT(*) as cantidad FROM solicitudes_externas  
UNION ALL
SELECT 'Ofertas externas:' as tabla, COUNT(*) as cantidad FROM ofertas_externas;