-- Migración para agregar tablas faltantes de la red de ONGs (MySQL)
-- Ejecutar después de la inicialización básica de la base de datos

-- Tabla para ofertas de donaciones externas
CREATE TABLE IF NOT EXISTS ofertas_externas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organizacion_donante VARCHAR(100) NOT NULL,
    oferta_id VARCHAR(100) NOT NULL,
    donaciones JSON NOT NULL,
    activa BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE(organizacion_donante, oferta_id)
);

-- Tabla para adhesiones a eventos externos
CREATE TABLE IF NOT EXISTS adhesiones_eventos_externos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evento_externo_id INTEGER,
    voluntario_id INTEGER,
    fecha_adhesion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('PENDIENTE', 'CONFIRMADA', 'CANCELADA') DEFAULT 'PENDIENTE',
    datos_voluntario JSON, -- Para almacenar datos del voluntario externo si es necesario
    UNIQUE(evento_externo_id, voluntario_id)
);

-- Tabla para historial de transferencias de donaciones
CREATE TABLE IF NOT EXISTS transferencias_donaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM('ENVIADA', 'RECIBIDA') NOT NULL,
    organizacion_contraparte VARCHAR(100) NOT NULL,
    solicitud_id VARCHAR(100),
    donaciones JSON NOT NULL,
    estado ENUM('PENDIENTE', 'COMPLETADA', 'CANCELADA') DEFAULT 'COMPLETADA',
    fecha_transferencia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_registro INTEGER,
    notas TEXT
);

-- Tabla para configuración de la organización
CREATE TABLE IF NOT EXISTS configuracion_organizacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    clave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT NOT NULL,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla para historial de mensajes Kafka (para auditoría)
CREATE TABLE IF NOT EXISTS historial_mensajes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(200) NOT NULL,
    tipo_mensaje VARCHAR(50) NOT NULL,
    mensaje_id VARCHAR(100),
    organizacion_origen VARCHAR(100),
    organizacion_destino VARCHAR(100),
    contenido JSON NOT NULL,
    estado ENUM('PROCESADO', 'ERROR', 'PENDIENTE') DEFAULT 'PROCESADO',
    fecha_procesamiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_detalle TEXT
);

-- Índices para optimizar consultas de red
CREATE INDEX idx_ofertas_externas_activa ON ofertas_externas(activa);
CREATE INDEX idx_ofertas_externas_organizacion ON ofertas_externas(organizacion_donante);
CREATE INDEX idx_ofertas_externas_fecha ON ofertas_externas(fecha_creacion);

CREATE INDEX idx_adhesiones_evento_externo ON adhesiones_eventos_externos(evento_externo_id);
CREATE INDEX idx_adhesiones_voluntario ON adhesiones_eventos_externos(voluntario_id);
CREATE INDEX idx_adhesiones_estado ON adhesiones_eventos_externos(estado);

CREATE INDEX idx_transferencias_tipo ON transferencias_donaciones(tipo);
CREATE INDEX idx_transferencias_organizacion ON transferencias_donaciones(organizacion_contraparte);
CREATE INDEX idx_transferencias_fecha ON transferencias_donaciones(fecha_transferencia);
CREATE INDEX idx_transferencias_estado ON transferencias_donaciones(estado);

CREATE INDEX idx_configuracion_clave ON configuracion_organizacion(clave);

CREATE INDEX idx_historial_topic ON historial_mensajes(topic);
CREATE INDEX idx_historial_tipo ON historial_mensajes(tipo_mensaje);
CREATE INDEX idx_historial_fecha ON historial_mensajes(fecha_procesamiento);
CREATE INDEX idx_historial_estado ON historial_mensajes(estado);

-- Insertar configuración inicial de la organización
INSERT IGNORE INTO configuracion_organizacion (clave, valor, descripcion) VALUES
('ORGANIZATION_ID', 'empuje-comunitario', 'Identificador único de la organización en la red de ONGs'),
('KAFKA_ENABLED', 'true', 'Habilitar funcionalidades de mensajería Kafka'),
('AUTO_PROCESS_EXTERNAL_REQUESTS', 'true', 'Procesar automáticamente solicitudes externas'),
('MAX_TRANSFER_AMOUNT', '1000', 'Cantidad máxima permitida para transferencias automáticas');

-- Datos de prueba para las nuevas tablas

-- Ofertas externas de prueba
INSERT IGNORE INTO ofertas_externas (organizacion_donante, oferta_id, donaciones) VALUES
('fundacion-esperanza', 'OFE-2025-001', '[{"categoria": "ALIMENTOS", "descripcion": "Conservas variadas", "cantidad": "20 latas"}]'),
('ong-solidaria', 'OFE-2025-002', '[{"categoria": "ROPA", "descripcion": "Ropa de abrigo", "cantidad": "15 prendas"}, {"categoria": "JUGUETES", "descripcion": "Juegos de mesa", "cantidad": "8 unidades"}]'),
('centro-comunitario', 'OFE-2025-003', '[{"categoria": "UTILES_ESCOLARES", "descripcion": "Kits escolares completos", "cantidad": "25 kits"}]');

-- Transferencias de prueba (historial)
INSERT IGNORE INTO transferencias_donaciones (tipo, organizacion_contraparte, solicitud_id, donaciones, usuario_registro, notas) VALUES
('ENVIADA', 'fundacion-esperanza', 'SOL-2024-001', '[{"categoria": "ALIMENTOS", "descripcion": "Puré de tomates", "cantidad": "10 latas"}]', 1, 'Transferencia completada exitosamente'),
('RECIBIDA', 'ong-solidaria', 'SOL-2024-002', '[{"categoria": "JUGUETES", "descripcion": "Pelotas de goma", "cantidad": "5 unidades"}]', 2, 'Donación recibida en buen estado'),
('ENVIADA', 'centro-comunitario', 'SOL-2024-003', '[{"categoria": "UTILES_ESCOLARES", "descripcion": "Cuadernos", "cantidad": "20 unidades"}]', 1, 'Entrega coordinada para inicio de clases');

-- Adhesiones a eventos externos de prueba
INSERT IGNORE INTO adhesiones_eventos_externos (evento_externo_id, voluntario_id, estado) VALUES
(1, 4, 'CONFIRMADA'), -- Ana se adhiere a Maratón Solidaria
(1, 5, 'PENDIENTE'),  -- Pedro pendiente para Maratón Solidaria
(2, 3, 'CONFIRMADA'), -- Carlos confirmado para Taller de Reciclaje
(3, 4, 'PENDIENTE');  -- Ana pendiente para Feria de Salud