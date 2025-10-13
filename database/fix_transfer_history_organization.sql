-- Migración para agregar campo organizacion_propietaria a transferencias_donaciones
-- Esto permite filtrar el historial por organización en un sistema multi-organizacional

-- Agregar campo organizacion_propietaria
ALTER TABLE transferencias_donaciones 
ADD COLUMN organizacion_propietaria VARCHAR(100) DEFAULT 'empuje-comunitario';

-- Actualizar registros existentes basándose en la lógica:
-- - Si tipo='ENVIADA', la organización propietaria es la que envía (empuje-comunitario por defecto)
-- - Si tipo='RECIBIDA', la organización propietaria es la que recibe (organizacion_contraparte)

-- Para transferencias enviadas, la organización propietaria es empuje-comunitario
UPDATE transferencias_donaciones 
SET organizacion_propietaria = 'empuje-comunitario' 
WHERE tipo = 'ENVIADA';

-- Para transferencias recibidas, necesitamos determinar quién las recibió
-- Por ahora, asumimos que las recibidas son de empuje-comunitario también
UPDATE transferencias_donaciones 
SET organizacion_propietaria = 'empuje-comunitario' 
WHERE tipo = 'RECIBIDA';

-- Crear índice para mejorar rendimiento
CREATE INDEX idx_transferencias_organizacion_propietaria 
ON transferencias_donaciones(organizacion_propietaria, fecha_transferencia DESC);

-- Hacer el campo NOT NULL después de actualizar los datos
ALTER TABLE transferencias_donaciones 
MODIFY COLUMN organizacion_propietaria VARCHAR(100) NOT NULL;