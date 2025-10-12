-- Migración para crear tabla de notificaciones de usuarios

CREATE TABLE IF NOT EXISTS notificaciones_usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    mensaje TEXT NOT NULL,
    tipo ENUM('INFO', 'SUCCESS', 'WARNING', 'ERROR') DEFAULT 'INFO',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_leida TIMESTAMP NULL,
    leida BOOLEAN DEFAULT FALSE,
    
    INDEX idx_usuario_fecha (usuario_id, fecha_creacion DESC),
    INDEX idx_usuario_leida (usuario_id, leida),
    INDEX idx_fecha_creacion (fecha_creacion DESC)
);

-- Comentario para documentar la tabla
ALTER TABLE notificaciones_usuarios COMMENT = 'Tabla de notificaciones para usuarios del sistema';