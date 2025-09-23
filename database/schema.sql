-- Schema para Sistema de Gestión ONG "Empuje Comunitario"
-- Creación de tablas principales y para red de ONGs

-- Tabla de usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('PRESIDENTE', 'VOCAL', 'COORDINADOR', 'VOLUNTARIO')),
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de donaciones (inventario)
CREATE TABLE donaciones (
    id SERIAL PRIMARY KEY,
    categoria VARCHAR(20) NOT NULL CHECK (categoria IN ('ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES')),
    descripcion TEXT,
    cantidad INTEGER NOT NULL CHECK (cantidad >= 0),
    eliminado BOOLEAN DEFAULT false,
    fecha_alta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_alta INTEGER REFERENCES usuarios(id),
    fecha_modificacion TIMESTAMP,
    usuario_modificacion INTEGER REFERENCES usuarios(id)
);

-- Tabla de eventos
CREATE TABLE eventos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_evento TIMESTAMP NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de participantes en eventos
CREATE TABLE participantes_evento (
    evento_id INTEGER REFERENCES eventos(id) ON DELETE CASCADE,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha_adhesion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (evento_id, usuario_id)
);

-- Tabla de donaciones repartidas en eventos
CREATE TABLE donaciones_repartidas (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER REFERENCES eventos(id) ON DELETE CASCADE,
    donacion_id INTEGER REFERENCES donaciones(id),
    cantidad_repartida INTEGER NOT NULL CHECK (cantidad_repartida > 0),
    usuario_registro INTEGER REFERENCES usuarios(id),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tablas para red de ONGs

-- Tabla de solicitudes externas de donaciones
CREATE TABLE solicitudes_externas (
    id SERIAL PRIMARY KEY,
    organizacion_solicitante VARCHAR(100) NOT NULL,
    solicitud_id VARCHAR(100) NOT NULL,
    donaciones JSONB NOT NULL,
    activa BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organizacion_solicitante, solicitud_id)
);

-- Tabla de eventos externos
CREATE TABLE eventos_externos (
    id SERIAL PRIMARY KEY,
    organizacion_id VARCHAR(100) NOT NULL,
    evento_id VARCHAR(100) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_evento TIMESTAMP NOT NULL,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organizacion_id, evento_id)
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_nombre_usuario ON usuarios(nombre_usuario);
CREATE INDEX idx_usuarios_activo ON usuarios(activo);
CREATE INDEX idx_donaciones_categoria ON donaciones(categoria);
CREATE INDEX idx_donaciones_eliminado ON donaciones(eliminado);
CREATE INDEX idx_eventos_fecha ON eventos(fecha_evento);
CREATE INDEX idx_solicitudes_activa ON solicitudes_externas(activa);
CREATE INDEX idx_eventos_externos_activo ON eventos_externos(activo);
CREATE INDEX idx_eventos_externos_fecha ON eventos_externos(fecha_evento);

-- Trigger para actualizar fecha_actualizacion en usuarios
CREATE OR REPLACE FUNCTION update_fecha_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_usuarios_fecha_actualizacion
    BEFORE UPDATE ON usuarios
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_actualizacion();

CREATE TRIGGER trigger_eventos_fecha_actualizacion
    BEFORE UPDATE ON eventos
    FOR EACH ROW
    EXECUTE FUNCTION update_fecha_actualizacion();