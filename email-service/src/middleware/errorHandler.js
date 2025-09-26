const errorHandler = (err, req, res, next) => {
  console.error('Error:', err);

  // Error de validación de Joi
  if (err.isJoi) {
    return res.status(400).json({
      error: 'Datos inválidos',
      details: err.details.map(d => d.message)
    });
  }

  // Error de Nodemailer
  if (err.code === 'EAUTH' || err.code === 'ECONNECTION') {
    return res.status(500).json({
      error: 'Error de configuración de email',
      message: 'Verifica la configuración SMTP'
    });
  }

  // Error genérico
  res.status(500).json({
    error: 'Error interno del servidor',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Ha ocurrido un error inesperado'
  });
};

module.exports = { errorHandler };