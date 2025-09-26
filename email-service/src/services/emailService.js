const nodemailer = require('nodemailer');

// Configurar transporter de Nodemailer
const createTransporter = async () => {
  // Si estamos en desarrollo y no hay credenciales reales, usar Ethereal
  if (process.env.NODE_ENV === 'development' &&
    (process.env.SMTP_USER === 'ethereal-dev' || !process.env.SMTP_USER)) {

    console.log('🔧 Usando Ethereal Email para desarrollo...');

    // Crear cuenta de prueba de Ethereal
    const testAccount = await nodemailer.createTestAccount();

    return nodemailer.createTransport({
      host: 'smtp.ethereal.email',
      port: 587,
      secure: false,
      auth: {
        user: testAccount.user,
        pass: testAccount.pass
      }
    });
  }

  // Configuración SMTP real
  return nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: parseInt(process.env.SMTP_PORT) || 587,
    secure: process.env.SMTP_SECURE === 'true', // true para 465, false para otros puertos
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS
    },
    tls: {
      rejectUnauthorized: false // Para desarrollo, en producción debería ser true
    }
  });
};

// Plantilla HTML para email de bienvenida
const getWelcomeTemplate = (data) => {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Bienvenido al Sistema</title>
      <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #28a745; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; background-color: #f8f9fa; }
        .credentials { background-color: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        .button { display: inline-block; padding: 12px 24px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>¡Bienvenido!</h1>
          <h2>${data.organizationName}</h2>
        </div>
        
        <div class="content">
          <h3>Hola ${data.fullName},</h3>
          
          <p>¡Bienvenido al sistema de gestión de ${data.organizationName}! Tu cuenta ha sido creada exitosamente.</p>
          
          <div class="credentials">
            <h4>Tus credenciales de acceso:</h4>
            <p><strong>Usuario:</strong> ${data.username}</p>
            <p><strong>Contraseña temporal:</strong> <code>${data.temporaryPassword}</code></p>
          </div>
          
          <p><strong>Próximos pasos:</strong></p>
          <ol>
            <li>Accede al sistema usando las credenciales proporcionadas</li>
            <li>Explora las funcionalidades disponibles según tu rol</li>
          </ol>
          
          <p><strong>Recuerda:</strong></p>
          <ul>
            <li>Mantén tus credenciales seguras</li>
            <li>Si tienes dudas, contacta al administrador</li>
          </ul>
          
          <a href="${process.env.FRONTEND_URL || 'http://localhost:3001'}" class="button">Acceder al Sistema</a>
        </div>
        
        <div class="footer">
          <p>Este es un mensaje automático, por favor no responder a este email.</p>
          <p>&copy; 2025 ${data.organizationName}. Todos los derechos reservados.</p>
        </div>
      </div>
    </body>
    </html>
  `;
};

// Enviar email de bienvenida
const sendWelcomeEmail = async (data) => {
  try {
    const transporter = await createTransporter();

    const mailOptions = {
      from: `"${data.organizationName}" <${process.env.SMTP_FROM || process.env.SMTP_USER}>`,
      to: data.email,
      subject: `¡Bienvenido a ${data.organizationName}!`,
      html: getWelcomeTemplate(data),
      text: `¡Bienvenido ${data.fullName}! Tu usuario es: ${data.username} y tu contraseña temporal es: ${data.temporaryPassword}. Por favor cámbiala en tu primer inicio de sesión.`
    };

    const info = await transporter.sendMail(mailOptions);

    // Si estamos usando Ethereal, mostrar URL de previsualización
    if (process.env.NODE_ENV === 'development' &&
      (process.env.SMTP_USER === 'ethereal-dev' || !process.env.SMTP_USER)) {
      console.log('📧 Email de bienvenida enviado!');
      console.log('🔗 URL de previsualización:', nodemailer.getTestMessageUrl(info));
    }

    return {
      success: true,
      messageId: info.messageId,
      response: info.response,
      previewUrl: process.env.NODE_ENV === 'development' ? nodemailer.getTestMessageUrl(info) : null
    };
  } catch (error) {
    console.error('Error enviando email de bienvenida:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

// Verificar configuración SMTP
const verifyEmailConfig = async () => {
  try {
    const transporter = await createTransporter();
    const verified = await transporter.verify();

    if (verified) {
      console.log('✅ Configuración SMTP verificada correctamente');
      return {
        success: true,
        message: 'Configuración SMTP válida',
        config: {
          host: process.env.SMTP_HOST || 'smtp.ethereal.email',
          port: process.env.SMTP_PORT || 587,
          secure: process.env.SMTP_SECURE === 'true',
          user: process.env.SMTP_USER || 'ethereal-test-account'
        }
      };
    }
  } catch (error) {
    console.error('❌ Error en configuración SMTP:', error.message);
    return {
      success: false,
      error: 'Error de configuración SMTP',
      message: error.message
    };
  }
};

module.exports = {
  sendWelcomeEmail,
  verifyEmailConfig
};