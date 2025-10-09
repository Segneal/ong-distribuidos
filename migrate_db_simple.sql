-- Migración para agregar soporte multi-organización a inventario y eventos

USE ong_management;

-- Agregar campo organizacion a tabla donaciones
ALTER TABLE donaciones 
ADD COLUMN IF NOT EXISTS organizacion VARCHAR(100) DEFAULT 'empuje-comunitario' AFTER cantidad;

-- Agregar campo organizacion a tabla eventos  
ALTER TABLE eventos 
ADD COLUMN IF NOT EXISTS organizacion VARCHAR(100) DEFAULT 'empuje-comunitario' AFTER descripcion;

-- Actualizar datos existentes
UPDATE donaciones 
SET organizacion = 'empuje-comunitario' 
WHERE organizacion IS NULL OR organizacion = '';

UPDATE eventos 
SET organizacion = 'empuje-comunitario' 
WHERE organizacion IS NULL OR organizacion = '';

-- Crear datos de prueba para otras organizaciones

-- Donaciones para Fundación Esperanza
INSERT INTO donaciones (categoria, descripcion, cantidad, organizacion, usuario_alta) VALUES
('ALIMENTOS', 'Leche en polvo', 40, 'fundacion-esperanza', 1),
('ROPA', 'Abrigos de invierno', 15, 'fundacion-esperanza', 1),
('JUGUETES', 'Libros infantiles', 25, 'fundacion-esperanza', 1);

-- Eventos para Fundación Esperanza
INSERT INTO eventos (nombre, descripcion, organizacion, fecha_evento) VALUES
('Campaña de Abrigo', 'Distribución de ropa de invierno', 'fundacion-esperanza', '2025-01-25 11:00:00'),
('Lectura en el Parque', 'Actividad de lectura para niños', 'fundacion-esperanza', '2025-02-05 16:00:00');

-- Donaciones para ONG Solidaria
INSERT INTO donaciones (categoria, descripcion, cantidad, organizacion, usuario_alta) VALUES
('UTILES_ESCOLARES', 'Mochilas escolares', 30, 'ong-solidaria', 1),
('JUGUETES', 'Juegos didácticos', 20, 'ong-solidaria', 1),
('ALIMENTOS', 'Cereales variados', 35, 'ong-solidaria', 1);

-- Eventos para ONG Solidaria
INSERT INTO eventos (nombre, descripcion, organizacion, fecha_evento) VALUES
('Preparación Escolar', 'Entrega de útiles escolares', 'ong-solidaria', '2025-01-30 10:00:00'),
('Taller de Juegos', 'Actividades lúdicas educativas', 'ong-solidaria', '2025-02-08 14:00:00');

-- Donaciones para Centro Comunitario
INSERT INTO donaciones (categoria, descripcion, cantidad, organizacion, usuario_alta) VALUES
('ALIMENTOS', 'Conservas variadas', 50, 'centro-comunitario', 1),
('ROPA', 'Ropa deportiva', 25, 'centro-comunitario', 1);

-- Eventos para Centro Comunitario
INSERT INTO eventos (nombre, descripcion, organizacion, fecha_evento) VALUES
('Jornada Deportiva', 'Actividades deportivas comunitarias', 'centro-comunitario', '2025-02-12 09:00:00');

-- Verificar resultados
SELECT 'DONACIONES POR ORGANIZACIÓN' as tipo;
SELECT organizacion, COUNT(*) as total FROM donaciones GROUP BY organizacion;

SELECT 'EVENTOS POR ORGANIZACIÓN' as tipo;
SELECT organizacion, COUNT(*) as total FROM eventos GROUP BY organizacion;