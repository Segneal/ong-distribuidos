-- Migración para sistema de solicitudes de inscripción
USE ong_management;

-- Tabla para solicitudes de inscripción de usuarios
CREATE TABLE IF NOT EXISTS solicitudes_inscripcion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    solicitud_id VARCHAR(100) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    organizacion_destino VARCHAR(100) NOT NULL,
    rol_solicitado ENUM('COORDINADOR', 'VOLUNTARIO') NOT NULL,
    mensaje TEXT,
    estado ENUM('PENDIENTE', 'APROBADA', 'DENEGADA') DEFAULT 'PENDIENTE',
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_respuesta TIMESTAMP NULL,
    usuario_revisor INT NULL,
    comentarios_revisor TEXT,
    datos_adicionales JSON,
    FOREIGN KEY (usuario_revisor) REFERENCES usuarios(id),
    INDEX idx_organizacion_estado (organizacion_destino, estado),
    INDEX idx_fecha_solicitud (fecha_solicitud),
    INDEX idx_estado (estado)
);

-- Tabla para notificaciones de solicitudes (para PRESIDENTE y VOCAL)
CREATE TABLE IF NOT EXISTS notificaciones_solicitudes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    solicitud_id VARCHAR(100) NOT NULL,
    usuario_destinatario INT NOT NULL,
    tipo_notificacion ENUM('NUEVA_SOLICITUD', 'SOLICITUD_APROBADA', 'SOLICITUD_DENEGADA') NOT NULL,
    leida BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_destinatario) REFERENCES usuarios(id),
    FOREIGN KEY (solicitud_id) REFERENCES solicitudes_inscripcion(solicitud_id),
    INDEX idx_usuario_leida (usuario_destinatario, leida),
    INDEX idx_fecha_creacion (fecha_creacion)
);

-- Insertar algunas solicitudes de prueba
INSERT INTO solicitudes_inscripcion (
    solicitud_id, nombre, apellido, email, telefono, 
    organizacion_destino, rol_solicitado, mensaje
) VALUES 
(
    'INS-2025-001', 
    'Roberto', 
    'García', 
    'roberto.garcia@email.com', 
    '+54911111111',
    'empuje-comunitario', 
    'VOLUNTARIO', 
    'Me gustaría colaborar con la organización en actividades comunitarias'
),
(
    'INS-2025-002', 
    'Laura', 
    'Fernández', 
    'laura.fernandez@email.com', 
    '+54922222222',
    'fundacion-esperanza', 
    'COORDINADOR', 
    'Tengo experiencia en gestión de proyectos sociales y me interesa coordinar actividades'
),
(
    'INS-2025-003', 
    'Miguel', 
    'Torres', 
    'miguel.torres@email.com', 
    '+54933333333',
    'empuje-comunitario', 
    'VOLUNTARIO', 
    'Quiero ayudar en eventos y distribución de donaciones'
);