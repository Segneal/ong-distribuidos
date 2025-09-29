-- Crear datos de prueba para solicitudes y ofertas externas

-- Insertar solicitudes externas de donaciones
INSERT INTO solicitudes_externas (
    organizacion_solicitante,
    solicitud_id,
    donaciones,
    activa
) VALUES
(
    'fundacion-esperanza',
    'REQ-FUND-001',
    '[{"category": "MEDICAMENTOS", "description": "Alcohol en gel y barbijos"}, {"category": "ALIMENTOS", "description": "Leche en polvo para bebés"}]'::jsonb,
    true
),
(
    'ong-solidaria',
    'REQ-SOLID-002',
    '[{"category": "ROPA", "description": "Abrigos para invierno talle adulto"}, {"category": "ALIMENTOS", "description": "Conservas y alimentos no perecederos"}]'::jsonb,
    true
),
(
    'ayuda-vecinal',
    'REQ-AYUDA-003',
    '[{"category": "JUGUETES", "description": "Juguetes para niños de 3 a 10 años"}, {"category": "LIBROS", "description": "Libros de cuentos infantiles"}]'::jsonb,
    true
),
(
    'educacion-popular',
    'REQ-EDUC-004',
    '[{"category": "UTILES_ESCOLARES", "description": "Cuadernos y útiles escolares"}, {"category": "LIBROS", "description": "Libros de texto para primaria"}]'::jsonb,
    true
)
ON CONFLICT (organizacion_solicitante, solicitud_id) DO NOTHING;

-- Insertar ofertas externas de donaciones
INSERT INTO ofertas_externas (
    organizacion_donante,
    oferta_id,
    donaciones,
    activa
) VALUES
(
    'fundacion-esperanza',
    'OFF-FUND-001',
    '[{"category": "ROPA", "description": "Ropa de bebé en buen estado", "quantity": "50 prendas"}, {"category": "JUGUETES", "description": "Juguetes didácticos", "quantity": "20 unidades"}]'::jsonb,
    true
),
(
    'educacion-popular',
    'OFF-EDUC-002',
    '[{"category": "LIBROS", "description": "Libros de texto escolares", "quantity": "100 libros"}, {"category": "UTILES_ESCOLARES", "description": "Cuadernos y útiles", "quantity": "200 unidades"}]'::jsonb,
    true
),
(
    'ong-solidaria',
    'OFF-SOLID-003',
    '[{"category": "ALIMENTOS", "description": "Conservas variadas", "quantity": "80 latas"}, {"category": "MEDICAMENTOS", "description": "Medicamentos básicos", "quantity": "Varios"}]'::jsonb,
    true
),
(
    'ayuda-vecinal',
    'OFF-AYUDA-004',
    '[{"category": "ROPA", "description": "Ropa de invierno para adultos", "quantity": "30 prendas"}, {"category": "ALIMENTOS", "description": "Productos de limpieza", "quantity": "25 unidades"}]'::jsonb,
    true
)
ON CONFLICT (organizacion_donante, oferta_id) DO NOTHING;

-- Verificar que se insertaron correctamente
SELECT 'Solicitudes externas insertadas:' as info, COUNT(*) as cantidad FROM solicitudes_externas WHERE organizacion_solicitante != 'empuje-comunitario';
SELECT 'Ofertas externas insertadas:' as info, COUNT(*) as cantidad FROM ofertas_externas WHERE organizacion_donante != 'empuje-comunitario';

-- Mostrar algunos datos de ejemplo
SELECT 'SOLICITUDES DISPONIBLES:' as tipo, solicitud_id, organizacion_solicitante, activa FROM solicitudes_externas WHERE activa = true AND organizacion_solicitante != 'empuje-comunitario' LIMIT 3;
SELECT 'OFERTAS DISPONIBLES:' as tipo, oferta_id, organizacion_donante, activa FROM ofertas_externas WHERE activa = true AND organizacion_donante != 'empuje-comunitario' LIMIT 3;