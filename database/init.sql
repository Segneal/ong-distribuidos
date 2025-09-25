-- Script de inicialización de la base de datos
-- Este archivo será ejecutado automáticamente por PostgreSQL al inicializar el contenedor

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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

-- Insertar datos de prueba
-- NOTA: Todos los usuarios tienen la contraseña 'admin123' para facilitar las pruebas
INSERT INTO usuarios (nombre_usuario, nombre, apellido, telefono, email, password_hash, rol) VALUES
('admin', 'Juan', 'Pérez', '+54911234567', 'admin@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'PRESIDENTE'),
('vocal1', 'María', 'González', '+54911234568', 'maria@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'VOCAL'),
('coord1', 'Carlos', 'López', '+54911234569', 'carlos@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'COORDINADOR'),
('vol1', 'Ana', 'Martínez', '+54911234570', 'ana@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'VOLUNTARIO'),
('vol2', 'Pedro', 'Rodríguez', '+54911234571', 'pedro@empujecomunitario.org', '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS', 'VOLUNTARIO');

-- Insertar donaciones de prueba
INSERT INTO donaciones (categoria, descripcion, cantidad, usuario_alta) VALUES
('ALIMENTOS', 'Puré de tomates en lata', 50, 1),
('ALIMENTOS', 'Arroz blanco 1kg', 25, 1),
('ROPA', 'Camisetas talle M', 30, 2),
('ROPA', 'Pantalones infantiles', 20, 2),
('JUGUETES', 'Pelotas de fútbol', 15, 1),
('JUGUETES', 'Muñecas de trapo', 10, 2),
('UTILES_ESCOLARES', 'Cuadernos rayados', 100, 1),
('UTILES_ESCOLARES', 'Lápices de colores', 50, 2);

-- Insertar eventos de prueba
INSERT INTO eventos (nombre, descripcion, fecha_evento) VALUES
('Entrega de Alimentos - Barrio Norte', 'Distribución de alimentos no perecederos', '2025-01-15 10:00:00'),
('Jornada de Juegos - Plaza Central', 'Actividades recreativas para niños', '2025-01-20 14:00:00'),
('Entrega de Útiles Escolares', 'Preparación para inicio de clases', '2025-02-01 09:00:00'),
('Evento Pasado - Navidad 2024', 'Celebración navideña comunitaria', '2024-12-24 18:00:00');

-- Insertar participantes en eventos
INSERT INTO participantes_evento (evento_id, usuario_id) VALUES
(1, 3), -- Carlos en entrega de alimentos
(1, 4), -- Ana en entrega de alimentos
(1, 5), -- Pedro en entrega de alimentos
(2, 3), -- Carlos en jornada de juegos
(2, 4), -- Ana en jornada de juegos
(3, 4), -- Ana en entrega de útiles
(3, 5), -- Pedro en entrega de útiles
(4, 3), -- Carlos en evento pasado
(4, 4), -- Ana en evento pasado
(4, 5); -- Pedro en evento pasado

-- Insertar donaciones repartidas en evento pasado
INSERT INTO donaciones_repartidas (evento_id, donacion_id, cantidad_repartida, usuario_registro) VALUES
(4, 1, 10, 3), -- 10 latas de puré repartidas en Navidad
(4, 5, 5, 3),  -- 5 pelotas repartidas en Navidad
(4, 6, 3, 4);  -- 3 muñecas repartidas en Navidad

-- Insertar solicitudes externas de prueba
INSERT INTO solicitudes_externas (organizacion_solicitante, solicitud_id, donaciones) VALUES
('fundacion-esperanza', 'SOL-2025-001', '[{"categoria": "ALIMENTOS", "descripcion": "Leche en polvo"}, {"categoria": "ROPA", "descripcion": "Abrigos de invierno"}]'),
('ong-solidaria', 'SOL-2025-002', '[{"categoria": "JUGUETES", "descripcion": "Juegos didácticos"}, {"categoria": "UTILES_ESCOLARES", "descripcion": "Mochilas escolares"}]');

-- Insertar eventos externos de prueba
INSERT INTO eventos_externos (organizacion_id, evento_id, nombre, descripcion, fecha_evento) VALUES
('fundacion-esperanza', 'EVT-2025-001', 'Maratón Solidaria', 'Carrera benéfica para recaudar fondos', '2025-02-10 08:00:00'),
('ong-solidaria', 'EVT-2025-002', 'Taller de Reciclaje', 'Enseñanza de técnicas de reciclaje', '2025-02-15 15:00:00'),
('centro-comunitario', 'EVT-2025-003', 'Feria de Salud', 'Controles médicos gratuitos', '2025-02-20 09:00:00');