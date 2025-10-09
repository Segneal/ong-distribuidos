-- Tablas faltantes para el sistema de red de ONGs

-- Tabla para solicitudes de donaciones
CREATE TABLE IF NOT EXISTS solicitudes_donaciones (
    solicitud_id INT AUTO_INCREMENT PRIMARY KEY,
    organizacion_solicitante VARCHAR(100) NOT NULL DEFAULT 'empuje-comunitario',
    donaciones JSON NOT NULL,
    estado ENUM('ACTIVA', 'COMPLETADA', 'CANCELADA') DEFAULT 'ACTIVA',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    notas TEXT
);

-- Tabla para eventos de red
CREATE TABLE IF NOT EXISTS eventos_red (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evento_id INT NOT NULL,
    organizacion_origen VARCHAR(100) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_evento DATETIME NOT NULL,
    fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT true,
    UNIQUE(evento_id, organizacion_origen)
);

-- Agregar columna expuesto_red a la tabla events si no existe
ALTER TABLE events ADD COLUMN IF NOT EXISTS expuesto_red BOOLEAN DEFAULT false;

-- Índices para optimizar consultas
CREATE INDEX idx_solicitudes_organizacion ON solicitudes_donaciones(organizacion_solicitante);
CREATE INDEX idx_solicitudes_estado ON solicitudes_donaciones(estado);
CREATE INDEX idx_solicitudes_fecha ON solicitudes_donaciones(fecha_creacion);

CREATE INDEX idx_eventos_red_organizacion ON eventos_red(organizacion_origen);
CREATE INDEX idx_eventos_red_activo ON eventos_red(activo);
CREATE INDEX idx_eventos_red_fecha ON eventos_red(fecha_evento);

-- Datos de prueba para solicitudes de donaciones
INSERT IGNORE INTO solicitudes_donaciones (organizacion_solicitante, donaciones, estado, notas) VALUES
('fundacion-esperanza', '[{"categoria": "ALIMENTOS", "descripcion": "Leche en polvo", "cantidad": "10 kg"}]', 'ACTIVA', 'Urgente para programa de nutrición infantil'),
('ong-solidaria', '[{"categoria": "ROPA", "descripcion": "Ropa de invierno", "cantidad": "50 prendas"}]', 'ACTIVA', 'Para familias en situación de vulnerabilidad'),
('centro-comunitario', '[{"categoria": "MEDICAMENTOS", "descripcion": "Medicamentos básicos", "cantidad": "Kit completo"}]', 'ACTIVA', 'Para botiquín comunitario');