-- Tabla para notificaciones de usuarios
CREATE TABLE IF NOT EXISTS notificaciones_usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    mensaje TEXT NOT NULL,
    tipo ENUM('EVENT_CANCELLED', 'EVENT_UPDATED', 'DONATION_RECEIVED', 'GENERAL') DEFAULT 'GENERAL',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_leida TIMESTAMP NULL,
    leida BOOLEAN DEFAULT false,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Índices para optimizar consultas
CREATE INDEX idx_notificaciones_usuario ON notificaciones_usuarios(usuario_id);
CREATE INDEX idx_notificaciones_leida ON notificaciones_usuarios(leida);
CREATE INDEX idx_notificaciones_fecha ON notificaciones_usuarios(fecha_creacion);
CREATE INDEX idx_notificaciones_tipo ON notificaciones_usuarios(tipo);