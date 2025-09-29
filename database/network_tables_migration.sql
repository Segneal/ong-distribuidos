-- Migración para agregar tablas faltantes de la red de ONGs
-- Ejecutar después de la inicialización básica de la base de datos

-- Tabla para ofertas de donaciones externas
CREATE TABLE IF NOT EXISTS ofertas_externas (
    id SERIAL PRIMARY KEY,
    organizacion_donante VARCHAR(100) NOT NULL,
    oferta_id VARCHAR(100) NOT NULL,
    donaciones JSONB NOT NULL,
    activa BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organizacion_donante, oferta_id)
);

-- Tabla para adhesiones a eventos externos
CREATE TABLE IF NOT EXISTS adhesiones_eventos_externos (
    id SERIAL PRIMARY KEY,
    evento_externo_id INTEGER REFERENCES eventos_externos(id) ON DELETE CASCADE,
    voluntario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha_adhesion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'CONFIRMADA', 'CANCELADA')),
    datos_voluntario JSONB, -- Para almacenar datos del voluntario externo si es necesario
    UNIQUE(evento_externo_id, voluntario_id)
);

-- Tabla para historial de transferencias de donaciones
CREATE TABLE IF NOT EXISTS transferencias_donaciones (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('ENVIADA', 'RECIBIDA')),
    organizacion_contraparte VARCHAR(100) NOT NULL,
    solicitud_id VARCHAR(100),
    donaciones JSONB NOT NULL,
    estado VARCHAR(20) DEFAULT 'COMPLETADA' CHECK (estado IN ('PENDIENTE', 'COMPLETADA', 'CANCELADA')),
    fecha_transferencia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_registro INTEGER REFERENCES usuarios(id),
    notas TEXT
);

-- Tabla para configuración de la organización
CREATE TABLE IF NOT EXISTS configuracion_organizacion (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT NOT NULL,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para historial de mensajes Kafka (para auditoría)
CREATE TABLE IF NOT EXISTS historial_mensajes (
    id SERIAL PRIMARY KEY,
    topic VARCHAR(200) NOT NULL,
    tipo_mensaje VARCHAR(50) NOT NULL,
    mensaje_id VARCHAR(100),
    organizacion_origen VARCHAR(100),
    organizacion_destino VARCHAR(100),
    contenido JSONB NOT NULL,
    estado VARCHAR(20) DEFAULT 'PROCESADO' CHECK (estado IN ('PROCESADO', 'ERROR', 'PENDIENTE')),
    fecha_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_detalle TEXT
);

-- Índices para optimizar consultas de red
CREATE INDEX IF NOT EXISTS idx_ofertas_externas_activa ON ofertas_externas(activa);
CREATE INDEX IF NOT EXISTS idx_ofertas_externas_organizacion ON ofertas_externas(organizacion_donante);
CREATE INDEX IF NOT EXISTS idx_ofertas_externas_fecha ON ofertas_externas(fecha_creacion);

CREATE INDEX IF NOT EXISTS idx_adhesiones_evento_externo ON adhesiones_eventos_externos(evento_externo_id);
CREATE INDEX IF NOT EXISTS idx_adhesiones_voluntario ON adhesiones_eventos_externos(voluntario_id);
CREATE INDEX IF NOT EXISTS idx_adhesiones_estado ON adhesiones_eventos_externos(estado);

CREATE INDEX IF NOT EXISTS idx_transferencias_tipo ON transferencias_donaciones(tipo);
CREATE INDEX IF NOT EXISTS idx_transferencias_organizacion ON transferencias_donaciones(organizacion_contraparte);
CREATE INDEX IF NOT EXISTS idx_transferencias_fecha ON transferencias_donaciones(fecha_transferencia);
CREATE INDEX IF NOT EXISTS idx_transferencias_estado ON transferencias_donaciones(estado);

CREATE INDEX IF NOT EXISTS idx_configuracion_clave ON configuracion_organizacion(clave);

CREATE INDEX IF NOT EXISTS idx_historial_topic ON historial_mensajes(topic);
CREATE INDEX IF NOT EXISTS idx_historial_tipo ON historial_mensajes(tipo_mensaje);
CREATE INDEX IF NOT EXISTS idx_historial_fecha ON historial_mensajes(fecha_procesamiento);
CREATE INDEX IF NOT EXISTS idx_historial_estado ON historial_mensajes(estado);

-- Triggers para actualizar fecha_actualizacion
DROP TRIGGER IF EXISTS trigger_ofertas_externas_fecha_actualizacion ON ofertas_externas;
CREATE TRIGGER trigger_ofertas_externas_fecha_actualizacion
    BEFORE UPDATE ON ofertas_externas
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_actualizacion();

DROP TRIGGER IF EXISTS trigger_configuracion_fecha_actualizacion ON configuracion_organizacion;
CREATE TRIGGER trigger_configuracion_fecha_actualizacion
    BEFORE UPDATE ON configuracion_organizacion
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_actualizacion();

-- Insertar configuración inicial de la organización
INSERT INTO configuracion_organizacion (clave, valor, descripcion) VALUES
('ORGANIZATION_ID', 'empuje-comunitario', 'Identificador único de la organización en la red de ONGs'),
('KAFKA_ENABLED', 'true', 'Habilitar funcionalidades de mensajería Kafka'),
('AUTO_PROCESS_EXTERNAL_REQUESTS', 'true', 'Procesar automáticamente solicitudes externas'),
('MAX_TRANSFER_AMOUNT', '1000', 'Cantidad máxima permitida para transferencias automáticas')
ON CONFLICT (clave) DO NOTHING;

-- Datos de prueba para las nuevas tablas

-- Ofertas externas de prueba
INSERT INTO ofertas_externas (organizacion_donante, oferta_id, donaciones) VALUES
('fundacion-esperanza', 'OFE-2025-001', '[{"categoria": "ALIMENTOS", "descripcion": "Conservas variadas", "cantidad": "20 latas"}]'),
('ong-solidaria', 'OFE-2025-002', '[{"categoria": "ROPA", "descripcion": "Ropa de abrigo", "cantidad": "15 prendas"}, {"categoria": "JUGUETES", "descripcion": "Juegos de mesa", "cantidad": "8 unidades"}]'),
('centro-comunitario', 'OFE-2025-003', '[{"categoria": "UTILES_ESCOLARES", "descripcion": "Kits escolares completos", "cantidad": "25 kits"}]')
ON CONFLICT (organizacion_donante, oferta_id) DO NOTHING;

-- Transferencias de prueba (historial)
INSERT INTO transferencias_donaciones (tipo, organizacion_contraparte, solicitud_id, donaciones, usuario_registro, notas) VALUES
('ENVIADA', 'fundacion-esperanza', 'SOL-2024-001', '[{"categoria": "ALIMENTOS", "descripcion": "Puré de tomates", "cantidad": "10 latas"}]', 1, 'Transferencia completada exitosamente'),
('RECIBIDA', 'ong-solidaria', 'SOL-2024-002', '[{"categoria": "JUGUETES", "descripcion": "Pelotas de goma", "cantidad": "5 unidades"}]', 2, 'Donación recibida en buen estado'),
('ENVIADA', 'centro-comunitario', 'SOL-2024-003', '[{"categoria": "UTILES_ESCOLARES", "descripcion": "Cuadernos", "cantidad": "20 unidades"}]', 1, 'Entrega coordinada para inicio de clases');

-- Adhesiones a eventos externos de prueba
INSERT INTO adhesiones_eventos_externos (evento_externo_id, voluntario_id, estado) VALUES
(1, 4, 'CONFIRMADA'), -- Ana se adhiere a Maratón Solidaria
(1, 5, 'PENDIENTE'),  -- Pedro pendiente para Maratón Solidaria
(2, 3, 'CONFIRMADA'), -- Carlos confirmado para Taller de Reciclaje
(3, 4, 'PENDIENTE');  -- Ana pendiente para Feria de Salud

COMMENT ON TABLE ofertas_externas IS 'Almacena ofertas de donaciones publicadas por otras organizaciones de la red';
COMMENT ON TABLE adhesiones_eventos_externos IS 'Registra adhesiones de voluntarios locales a eventos de otras organizaciones';
COMMENT ON TABLE transferencias_donaciones IS 'Historial de transferencias de donaciones enviadas y recibidas';
COMMENT ON TABLE configuracion_organizacion IS 'Configuración general de la organización para funcionalidades de red';
COMMENT ON TABLE historial_mensajes IS 'Auditoría de mensajes Kafka procesados por el sistema';

-- Ejecutar optimizaciones de índices
\i network_indexes_optimization.sql