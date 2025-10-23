-- Migración para tablas del servicio de reportes
-- Tablas para filtros guardados y archivos Excel

-- Tabla para filtros guardados
CREATE TABLE IF NOT EXISTS filtros_guardados (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    nombre VARCHAR(255) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('DONACIONES', 'EVENTOS')),
    configuracion JSONB NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para archivos Excel generados
CREATE TABLE IF NOT EXISTS archivos_excel (
    id VARCHAR(36) PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_filtros_guardados_usuario ON filtros_guardados(usuario_id);
CREATE INDEX IF NOT EXISTS idx_filtros_guardados_tipo ON filtros_guardados(tipo);
CREATE INDEX IF NOT EXISTS idx_archivos_excel_usuario ON archivos_excel(usuario_id);
CREATE INDEX IF NOT EXISTS idx_archivos_excel_expiracion ON archivos_excel(fecha_expiracion);

-- Trigger para actualizar fecha_actualizacion en filtros_guardados
CREATE OR REPLACE FUNCTION update_fecha_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_filtros_guardados_fecha_actualizacion ON filtros_guardados;
CREATE TRIGGER trigger_filtros_guardados_fecha_actualizacion
    BEFORE UPDATE ON filtros_guardados
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_actualizacion();

-- Insertar algunos filtros de prueba
INSERT INTO filtros_guardados (usuario_id, nombre, tipo, configuracion) VALUES
(1, 'Alimentos del último mes', 'DONACIONES', '{"categoria": "ALIMENTOS", "fechaDesde": "2024-12-01", "eliminado": false}'),
(2, 'Ropa eliminada', 'DONACIONES', '{"categoria": "ROPA", "eliminado": true}'),
(1, 'Eventos futuros', 'EVENTOS', '{"fechaDesde": "2025-01-01"}');