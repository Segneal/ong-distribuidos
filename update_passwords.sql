-- Actualizar contraseñas de todos los usuarios a 'admin123'
UPDATE usuarios 
SET password_hash = '$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS';

-- Verificar la actualización
SELECT nombre_usuario, nombre, apellido, rol, email 
FROM usuarios 
WHERE activo = true;