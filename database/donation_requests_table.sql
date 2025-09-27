-- Tabla para solicitudes de donaciones propias
-- Esta tabla almacena las solicitudes que nuestra organización hace a la red

CREATE TABLE IF NOT EXISTS solicitudes_donaciones (
    id SERIAL PRIMARY KEY,
    solicitud_id VARCHAR(100) UNIQUE NOT NULL,
    donaciones JSONB NOT NULL,
    estado VARCHAR(20) DEFAULT 'ACTIVA' CHECK (estado IN ('ACTIVA', 'DADA_DE_BAJA', 'COMPLETADA')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER REFERENCES usuarios(id),
    usuario_actualizacion INTEGER REFERENCES usuarios(id),
    notas TEXT
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_solicitudes_donaciones_estado ON solicitudes_donaciones(estado);
CREATE INDEX IF NOT EXISTS idx_solicitudes_donaciones_fecha ON solicitudes_donaciones(fecha_creacion);
CREATE INDEX IF NOT EXISTS idx_solicitudes_donaciones_gin ON solicitudes_donaciones USING gin(donaciones);

-- Trigger para actualizar fecha_actualizacion
CREATE TRIGGER IF NOT EXISTS trigger_solicitudes_donaciones_fecha_actualizacion
    BEFORE UPDATE ON solicitudes_donaciones
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_actualizacion();

COMMENT ON TABLE solicitudes_donaciones IS 'Almacena las solicitudes de donaciones que nuestra organización publica en la red de ONGs';