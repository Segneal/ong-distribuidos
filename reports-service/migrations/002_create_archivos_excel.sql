-- Migration: Create archivos_excel table
-- Description: Table to store temporary Excel files for download

USE ong_management;

CREATE TABLE IF NOT EXISTS archivos_excel (
    id VARCHAR(36) PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Create index for better performance
CREATE INDEX idx_archivos_excel_usuario ON archivos_excel(usuario_id);
CREATE INDEX idx_archivos_excel_expiracion ON archivos_excel(fecha_expiracion);