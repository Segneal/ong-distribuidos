-- Índices adicionales para optimizar consultas de red de ONGs
-- Ejecutar después de la migración de tablas de red

-- Índices compuestos para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_ofertas_externas_org_activa ON ofertas_externas(organizacion_donante, activa);
CREATE INDEX IF NOT EXISTS idx_ofertas_externas_fecha_activa ON ofertas_externas(fecha_creacion DESC, activa) WHERE activa = true;

CREATE INDEX IF NOT EXISTS idx_solicitudes_externas_org_activa ON solicitudes_externas(organizacion_solicitante, activa);
CREATE INDEX IF NOT EXISTS idx_solicitudes_externas_fecha_activa ON solicitudes_externas(fecha_creacion DESC, activa) WHERE activa = true;

CREATE INDEX IF NOT EXISTS idx_eventos_externos_org_activo ON eventos_externos(organizacion_id, activo);
CREATE INDEX IF NOT EXISTS idx_eventos_externos_fecha_activo ON eventos_externos(fecha_evento ASC, activo) WHERE activo = true;
CREATE INDEX IF NOT EXISTS idx_eventos_externos_upcoming ON eventos_externos(fecha_evento) WHERE activo = true AND fecha_evento > CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_transferencias_org_tipo ON transferencias_donaciones(organizacion_contraparte, tipo);
CREATE INDEX IF NOT EXISTS idx_transferencias_fecha_tipo ON transferencias_donaciones(fecha_transferencia DESC, tipo);
CREATE INDEX IF NOT EXISTS idx_transferencias_estado_fecha ON transferencias_donaciones(estado, fecha_transferencia DESC);

CREATE INDEX IF NOT EXISTS idx_adhesiones_voluntario_estado ON adhesiones_eventos_externos(voluntario_id, estado);
CREATE INDEX IF NOT EXISTS idx_adhesiones_evento_estado ON adhesiones_eventos_externos(evento_externo_id, estado);

CREATE INDEX IF NOT EXISTS idx_historial_org_fecha ON historial_mensajes(organizacion_origen, fecha_procesamiento DESC);
CREATE INDEX IF NOT EXISTS idx_historial_topic_estado ON historial_mensajes(topic, estado);

-- Índices para búsquedas de texto en JSON (donaciones)
CREATE INDEX IF NOT EXISTS idx_ofertas_donaciones_gin ON ofertas_externas USING gin(donaciones);
CREATE INDEX IF NOT EXISTS idx_solicitudes_donaciones_gin ON solicitudes_externas USING gin(donaciones);
CREATE INDEX IF NOT EXISTS idx_transferencias_donaciones_gin ON transferencias_donaciones USING gin(donaciones);

-- Índices parciales para mejorar rendimiento en consultas específicas
CREATE INDEX IF NOT EXISTS idx_eventos_externos_future ON eventos_externos(fecha_evento, organizacion_id) 
    WHERE activo = true AND fecha_evento > CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_adhesiones_confirmadas ON adhesiones_eventos_externos(evento_externo_id, voluntario_id) 
    WHERE estado = 'CONFIRMADA';

CREATE INDEX IF NOT EXISTS idx_transferencias_recientes ON transferencias_donaciones(fecha_transferencia DESC, organizacion_contraparte) 
    WHERE fecha_transferencia > CURRENT_TIMESTAMP - INTERVAL '30 days';

-- Índices para estadísticas y reportes
CREATE INDEX IF NOT EXISTS idx_historial_mensajes_stats ON historial_mensajes(topic, estado, fecha_procesamiento);
CREATE INDEX IF NOT EXISTS idx_ofertas_stats ON ofertas_externas(organizacion_donante, activa, fecha_creacion);
CREATE INDEX IF NOT EXISTS idx_eventos_stats ON eventos_externos(organizacion_id, activo, fecha_evento);

-- Comentarios para documentar el propósito de los índices
COMMENT ON INDEX idx_ofertas_externas_org_activa IS 'Optimiza consultas de ofertas por organización y estado activo';
COMMENT ON INDEX idx_eventos_externos_upcoming IS 'Optimiza consultas de eventos próximos';
COMMENT ON INDEX idx_ofertas_donaciones_gin IS 'Permite búsquedas eficientes en el contenido JSON de donaciones';
COMMENT ON INDEX idx_adhesiones_confirmadas IS 'Optimiza consultas de adhesiones confirmadas por evento';

-- Estadísticas para el optimizador de consultas
ANALYZE ofertas_externas;
ANALYZE solicitudes_externas;
ANALYZE eventos_externos;
ANALYZE adhesiones_eventos_externos;
ANALYZE transferencias_donaciones;
ANALYZE configuracion_organizacion;
ANALYZE historial_mensajes;