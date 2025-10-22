-- Migration: Create filtros_guardados table
-- Description: Table to store saved filters for donation and event reports

USE ong_management;

CREATE TABLE IF NOT EXISTS filtros_guardados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    tipo ENUM('DONACIONES', 'EVENTOS') NOT NULL,
    configuracion JSON NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_filter (usuario_id, nombre, tipo)
);

-- Create index for better performance
CREATE INDEX idx_filtros_guardados_usuario ON filtros_guardados(usuario_id);
CREATE INDEX idx_filtros_guardados_tipo ON filtros_guardados(tipo);