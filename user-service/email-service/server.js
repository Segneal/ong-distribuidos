const express = require('express');
const nodemailer = require('nodemailer');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.EMAIL_SERVICE_PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Configurar transporter de Nodemailer
const transporter = nodemailer.createTransporter({
    host: process.env.SMTP_HOST || 'smtp.gmail.com',
    port: process.env.SMTP_PORT || 587,
    secure: false, // true para 465, false para otros puertos
    auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS
    }
});

// Función para escribir al archivo de log
function logPasswordToFile(username, password) {
    try {
        const logDir = path.join(__dirname, '../../testing/usuarios');
        const logFile = path.join(logDir, 'passlogs.txt');
        
        // Crear directorio si no existe
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }
        
        const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
        const logEntry = `[${timestamp}] Usuario: ${username}, Contraseña: ${password}\n`;
        
        fs.appendFileSync(logFile, logEntry, 'utf8');
        return true;
    } catch (error) {
        console.error('Error escribiendo al archivo de log:', error);
        return false;
    }
}

// Endpoint para enviar contraseña por email
app.post('/send-password', async (req, res) => {
    try {
        const { email, username, password, firstName, lastName } = req.body;
        
        if (!email || !username || !password) {
            return res.status(400).json({
                success: false,
                message: 'Email, username y password son requeridos'
            });
        }
        
        // Escribir al archivo de log para testing
        logPasswordToFile(username, password);
        
        // Configurar el email
        const mailOptions = {
            from: process.env.SMTP_USER || 'noreply@empujecomunitario.org',
            to: email,
            subject: 'Bienvenido a Empuje Comunitario - Credenciales de Acceso',
            html: `
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #2c3e50;">Bienvenido a Empuje Comunitario</h2>
                    <p>Hola ${firstName} ${lastName},</p>
                    <p>Tu cuenta ha sido creada exitosamente en el sistema de gestión de Empuje Comunitario.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #495057; margin-top: 0;">Tus credenciales de acceso:</h3>
                        <p><strong>Usuario:</strong> ${username}</p>
                        <p><strong>Contraseña:</strong> ${password}</p>
                    </div>
                    
                    <p>Por favor, guarda estas credenciales en un lugar seguro y considera cambiar tu contraseña después del primer inicio de sesión.</p>
                    
                    <p>Si tienes alguna pregunta, no dudes en contactar al administrador del sistema.</p>
                    
                    <p>Saludos,<br>
                    Equipo de Empuje Comunitario</p>
                </div>
            `
        };
        
        // Enviar email solo si las credenciales SMTP están configuradas
        if (process.env.SMTP_USER && process.env.SMTP_PASS) {
            await transporter.sendMail(mailOptions);
            console.log(`Email enviado exitosamente a ${email} para usuario ${username}`);
        } else {
            console.log(`Modo testing: Email simulado para ${email} - Usuario: ${username}`);
        }
        
        res.json({
            success: true,
            message: 'Email enviado exitosamente'
        });
        
    } catch (error) {
        console.error('Error enviando email:', error);
        res.status(500).json({
            success: false,
            message: 'Error enviando email'
        });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'OK', service: 'email-service' });
});

// Iniciar servidor
app.listen(PORT, () => {
    console.log(`Servicio de email iniciado en puerto ${PORT}`);
});