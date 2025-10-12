-- Migración para agregar el estado 'RECHAZADA' a las adhesiones de eventos externos
-- y las columnas necesarias para el sistema de aprobación

-- Agregar el estado 'RECHAZADA' al ENUM
ALTER TABLE adhesiones_eventos_externos 
MODIFY COLUMN estado ENUM('PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'RECHAZADA') DEFAULT 'PENDIENTE';

-- Agregar columnas para el sistema de aprobación
ALTER TABLE adhesiones_eventos_externos 
ADD COLUMN fecha_aprobacion TIMESTAMP NULL;

ALTER TABLE adhesiones_eventos_externos 
ADD COLUMN motivo_rechazo TEXT NULL;

-- Crear índices para mejorar el rendimiento
CREATE INDEX idx_adhesiones_estado_fecha ON adhesiones_eventos_externos(estado, fecha_adhesion DESC);
CREATE INDEX idx_adhesiones_aprobacion ON adhesiones_eventos_externos(fecha_aprobacion);

-- Comentarios para documentar los cambios
ALTER TABLE adhesiones_eventos_externos COMMENT = 'Tabla de adhesiones a eventos externos con sistema de aprobación';