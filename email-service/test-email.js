// Cargar variables de entorno
require('dotenv').config();

const { sendWelcomeEmail, verifyEmailConfig } = require('./src/services/emailService');

async function testEmailService() {
  console.log('🧪 Probando servicio de email...\n');

  try {
    // Probar configuración
    console.log('1. Verificando configuración SMTP...');
    const configResult = await verifyEmailConfig();
    console.log('Resultado:', configResult);
    console.log('');

    if (configResult.success) {
      // Probar email de bienvenida
      console.log('2. Probando email de bienvenida...');
      const welcomeResult = await sendWelcomeEmail({
        email: 'nuevo@example.com',
        username: 'nuevo_usuario',
        fullName: 'Usuario Nuevo',
        temporaryPassword: 'welcome123',
        organizationName: 'ONG Empuje Comunitario'
      });
      
      console.log('Resultado:', welcomeResult);
      if (welcomeResult.previewUrl) {
        console.log('🔗 Ver email en:', welcomeResult.previewUrl);
      }
    }

  } catch (error) {
    console.error('❌ Error durante las pruebas:', error);
  }
}

// Ejecutar pruebas
testEmailService();